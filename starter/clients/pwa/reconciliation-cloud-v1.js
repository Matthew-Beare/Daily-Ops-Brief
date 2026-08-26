"use strict";

(() => {
  const TABLES = {
    ReconciliationWork: ["work_uuid","feature_namespace","source_type","source_uuid","work_type","processing_mode","status","priority","freshness_minutes","capabilities_json","allowed_mutations_json","confidence_threshold","idempotency_key","attempts","next_attempt_at","claimed_by","claimed_at","processor_uuid","processor_version","result_json","last_error","created_at","updated_at","completed_at"],
    ReconciliationDependencies: ["work_uuid","depends_on_work_uuid","created_at"],
    FeatureProcessingPolicies: ["feature_namespace","enabled","processing_mode","freshness","capabilities_json","allowed_mutations_json","preferred_processor_uuid","local_only","max_cost_per_work","confidence_threshold","created_at","updated_at"],
    AIProcessors: ["processor_uuid","provider_kind","display_name","model_name","execution_mode","capabilities_json","enabled","metered","local_only","privacy_class","priority","health","config_json","created_at","updated_at"],
    AIUsage: ["usage_uuid","processor_uuid","provider_kind","model_name","work_uuid","feature_namespace","input_units","output_units","cached_units","estimated_cost","currency","price_snapshot_json","created_at"],
    UserCorrections: ["correction_uuid","entity_type","entity_uuid","field_name","previous_value_json","confirmed_value_json","reason","source","created_at"],
    RecognitionProfiles: ["profile_uuid","profile_type","lookup_key","value_json","confidence","user_confirmed","source_entity_type","source_entity_uuid","created_at","updated_at"],
    MerchantLocations: ["merchant_location_uuid","merchant_uuid","display_name","store_number","address_line1","address_line2","city","region","postal_code","country","latitude","longitude","metadata_json","user_confirmed","created_at","updated_at"],
    ReceiptMerchantLocationLinks: ["receipt_uuid","merchant_location_uuid","confidence","user_confirmed","linked_at"]
  };
  const WORK_STATES = new Set(["queued","processing","needs_review","failed_retryable","quarantined","complete"]);
  const callbacks = new Map();
  const previousCallback = globalThis.onMirrorNativeGoogleApiResponse;
  let sequence = 0;
  let ensuredWorkbook = "";
  let ensurePromise = null;

  function now() { return new Date().toISOString(); }
  function uuid() { return globalThis.crypto?.randomUUID ? crypto.randomUUID() : `${Date.now()}-${Math.random()}`; }
  function authority() { return globalThis.MiraGoogleAuthority?.authority?.() || null; }
  function nativeReady() { return Boolean(globalThis.MirrorNative?.googleApiRequest); }
  function encodeRange(value) { return encodeURIComponent(value).replace(/%2F/g, "/"); }
  function columnName(index) {
    let value = Number(index), out = "";
    while (value > 0) { value -= 1; out = String.fromCharCode(65 + (value % 26)) + out; value = Math.floor(value / 26); }
    return out || "A";
  }
  function json(value, fallback = {}) {
    if (value == null || value === "") return fallback;
    if (typeof value !== "string") return value;
    try { return JSON.parse(value); } catch (_) { return fallback; }
  }

  function request(method, url, body = "", contentType = "application/json; charset=utf-8") {
    if (!nativeReady()) return Promise.reject(new Error("Google MIRROR transport is not available."));
    const requestId = `reconcile-${Date.now()}-${++sequence}`;
    return new Promise((resolve, reject) => {
      const timer = setTimeout(() => { callbacks.delete(requestId); reject(new Error("Google did not answer the reconciliation request within two minutes.")); }, 120000);
      callbacks.set(requestId, { resolve, reject, timer });
      try { globalThis.MirrorNative.googleApiRequest(requestId, method, url, body, contentType); }
      catch (error) { clearTimeout(timer); callbacks.delete(requestId); reject(error); }
    });
  }

  globalThis.onMirrorNativeGoogleApiResponse = function reconciliationGoogleResponse(requestId, status, responseText) {
    const pending = callbacks.get(requestId);
    if (!pending) {
      if (typeof previousCallback === "function") previousCallback(requestId, status, responseText);
      return;
    }
    callbacks.delete(requestId); clearTimeout(pending.timer);
    const code = Number(status);
    let parsed = {};
    try { parsed = responseText ? JSON.parse(String(responseText)) : {}; } catch (_) { parsed = {}; }
    if (code < 200 || code >= 300) {
      const detail = parsed?.error?.message || parsed?.error || responseText || `Google returned HTTP ${code}.`;
      pending.reject(new Error(typeof detail === "string" ? detail : JSON.stringify(detail)));
    } else pending.resolve({ status: code, json: parsed, text: String(responseText || "") });
  };

  async function rowsDirect(info, table) {
    const headers = TABLES[table];
    if (!headers) throw new Error(`Unknown MIRROR reconciliation table ${table}.`);
    const range = encodeRange(`'${table}'!A:${columnName(headers.length)}`);
    const result = (await request("GET", `https://sheets.googleapis.com/v4/spreadsheets/${encodeURIComponent(info.workbook_id)}/values/${range}?majorDimension=ROWS`)).json;
    const values = result.values || [];
    const actual = values[0] || headers;
    return values.slice(1).map((row, rowIndex) => ({ __row: rowIndex + 2, ...Object.fromEntries(actual.map((key, index) => [key, row[index] ?? ""])) }));
  }

  async function appendDirect(info, table, object) {
    const headers = TABLES[table];
    const values = headers.map((key) => object[key] == null ? "" : String(object[key]));
    const range = encodeRange(`'${table}'!A:${columnName(headers.length)}`);
    await request("POST", `https://sheets.googleapis.com/v4/spreadsheets/${encodeURIComponent(info.workbook_id)}/values/${range}:append?valueInputOption=RAW&insertDataOption=INSERT_ROWS`, JSON.stringify({ majorDimension: "ROWS", values: [values] }));
    return object;
  }

  async function replaceRowDirect(info, table, rowNumber, object) {
    const headers = TABLES[table];
    const values = headers.map((key) => object[key] == null ? "" : String(object[key]));
    const rangeText = `'${table}'!A${rowNumber}:${columnName(headers.length)}${rowNumber}`;
    await request("PUT", `https://sheets.googleapis.com/v4/spreadsheets/${encodeURIComponent(info.workbook_id)}/values/${encodeRange(rangeText)}?valueInputOption=RAW`, JSON.stringify({ range: rangeText, majorDimension: "ROWS", values: [values] }));
  }

  async function ensureDefaultProcessorsDirect(info) {
    const existing = await rowsDirect(info, "AIProcessors");
    const timestamp = now();
    const defaults = [
      { processor_uuid: "chatgpt-scheduled", provider_kind: "chatgpt_scheduled_mira", display_name: "MIRA in ChatGPT", model_name: "", execution_mode: "scheduled", capabilities_json: JSON.stringify(["text_reasoning","vision","tool_use","web_research","structured_output"]), enabled: "1", metered: "0", local_only: "0", privacy_class: "standard", priority: "100", health: "available", config_json: "{}", created_at: timestamp, updated_at: timestamp },
      { processor_uuid: "manual", provider_kind: "manual", display_name: "Manual review", model_name: "", execution_mode: "manual", capabilities_json: "[]", enabled: "1", metered: "0", local_only: "1", privacy_class: "local", priority: "1000", health: "available", config_json: "{}", created_at: timestamp, updated_at: timestamp }
    ];
    for (const row of defaults) if (!existing.some((item) => item.processor_uuid === row.processor_uuid)) await appendDirect(info, "AIProcessors", row);
  }

  async function ensureTables() {
    if (ensurePromise) return ensurePromise;
    ensurePromise = (async () => {
      if (!globalThis.MiraGoogleAuthority?.ready || !(await globalThis.MiraGoogleAuthority.ready())) throw new Error("Connect Google before using Daily Cleanup.");
      const info = authority();
      if (!info?.workbook_id) throw new Error("MIRROR workbook is not connected.");
      if (ensuredWorkbook === info.workbook_id) return info;
      const workbook = (await request("GET", `https://sheets.googleapis.com/v4/spreadsheets/${encodeURIComponent(info.workbook_id)}?fields=sheets.properties`)).json;
      const existing = new Set((workbook.sheets || []).map((sheet) => sheet.properties?.title));
      const missing = Object.keys(TABLES).filter((name) => !existing.has(name));
      if (missing.length) await request("POST", `https://sheets.googleapis.com/v4/spreadsheets/${encodeURIComponent(info.workbook_id)}:batchUpdate`, JSON.stringify({ requests: missing.map((title) => ({ addSheet: { properties: { title } } })) }));
      for (const [name, headers] of Object.entries(TABLES)) {
        const rangeText = `'${name}'!A1:${columnName(headers.length)}1`;
        await request("PUT", `https://sheets.googleapis.com/v4/spreadsheets/${encodeURIComponent(info.workbook_id)}/values/${encodeRange(rangeText)}?valueInputOption=RAW`, JSON.stringify({ range: rangeText, majorDimension: "ROWS", values: [headers] }));
      }
      await ensureDefaultProcessorsDirect(info);
      ensuredWorkbook = info.workbook_id;
      return info;
    })();
    try { return await ensurePromise; }
    finally { ensurePromise = null; }
  }

  async function rawRows(table) { return rowsDirect(await ensureTables(), table); }
  async function append(table, object) { return appendDirect(await ensureTables(), table, object); }

  async function upsert(table, key, value, object) {
    const info = await ensureTables();
    const rows = await rowsDirect(info, table);
    const existing = rows.find((row) => String(row[key]) === String(value));
    const timestamp = now();
    if (existing) {
      const merged = { ...existing, ...object, [key]: value, updated_at: object.updated_at || timestamp };
      delete merged.__row;
      await replaceRowDirect(info, table, existing.__row, merged);
      const verify = (await rowsDirect(info, table)).find((row) => String(row[key]) === String(value));
      if (!verify) throw new Error(`${table} update did not read back from MIRROR.`);
      return verify;
    }
    const created = { ...object, [key]: value, created_at: object.created_at || timestamp, updated_at: object.updated_at || timestamp };
    await appendDirect(info, table, created);
    const verify = (await rowsDirect(info, table)).find((row) => String(row[key]) === String(value));
    if (!verify) throw new Error(`${table} insert did not read back from MIRROR.`);
    return verify;
  }

  async function queueWork(payload) {
    if (!payload?.source_uuid) throw new Error("Cleanup work requires a source record.");
    const rows = await rawRows("ReconciliationWork");
    const feature = payload.feature_namespace || "general", sourceType = payload.source_type || "record", workType = payload.work_type || "general.reconcile";
    const existing = rows.find((row) => row.feature_namespace === feature && row.source_type === sourceType && row.source_uuid === payload.source_uuid && row.work_type === workType);
    if (existing) return { work: existing, readback_verified: true, idempotent_replay: true };
    const timestamp = now();
    const row = {
      work_uuid: payload.work_uuid || uuid(), feature_namespace: feature, source_type: sourceType, source_uuid: payload.source_uuid,
      work_type: workType, processing_mode: payload.processing_mode || "deferred_reconciliation", status: "queued", priority: payload.priority || "20",
      freshness_minutes: payload.freshness_minutes || "1440", capabilities_json: JSON.stringify(payload.capabilities || ["text_reasoning"]), allowed_mutations_json: JSON.stringify(payload.allowed_mutations || []),
      confidence_threshold: payload.confidence_threshold || "0.90", idempotency_key: payload.idempotency_key || `${feature}:${sourceType}:${payload.source_uuid}:${workType}`,
      attempts: "0", next_attempt_at: "", claimed_by: "", claimed_at: "", processor_uuid: "", processor_version: "", result_json: "{}", last_error: "", created_at: timestamp, updated_at: timestamp, completed_at: ""
    };
    await append("ReconciliationWork", row);
    const readback = (await rawRows("ReconciliationWork")).find((item) => item.work_uuid === row.work_uuid);
    if (!readback || readback.idempotency_key !== row.idempotency_key) throw new Error("Cleanup work was written but did not read back correctly from MIRROR.");
    return { work: readback, readback_verified: true };
  }

  async function dependenciesComplete(workUuid) {
    const [deps, work] = await Promise.all([rawRows("ReconciliationDependencies"), rawRows("ReconciliationWork")]);
    const required = deps.filter((row) => row.work_uuid === workUuid).map((row) => row.depends_on_work_uuid);
    return required.every((id) => work.some((row) => row.work_uuid === id && row.status === "complete"));
  }

  async function claimWork(workUuid, { worker = "mira", processor_uuid = "" } = {}) {
    const info = await ensureTables();
    const rows = await rowsDirect(info, "ReconciliationWork");
    const current = rows.find((row) => row.work_uuid === workUuid);
    if (!current) throw new Error("Cleanup work was not found in MIRROR.");
    if (current.status === "complete") return { work: current, readback_verified: true, idempotent_replay: true };
    if (!(await dependenciesComplete(workUuid))) throw new Error("This cleanup item is waiting for another cleanup item to finish first.");
    const updated = { ...current, status: "processing", claimed_by: worker, claimed_at: now(), processor_uuid: processor_uuid || current.processor_uuid || "", attempts: String(Number(current.attempts || 0) + 1), last_error: "", updated_at: now() };
    delete updated.__row;
    await replaceRowDirect(info, "ReconciliationWork", current.__row, updated);
    const verify = (await rowsDirect(info, "ReconciliationWork")).find((row) => row.work_uuid === workUuid);
    if (!verify || verify.status !== "processing" || verify.claimed_by !== worker) throw new Error("Cleanup claim did not read back from MIRROR.");
    return { work: verify, readback_verified: true };
  }

  async function finishWork(workUuid, payload = {}) {
    const outcome = String(payload.outcome || "needs_review");
    if (!WORK_STATES.has(outcome) || ["queued","processing"].includes(outcome)) throw new Error("Invalid cleanup result state.");
    const info = await ensureTables();
    const rows = await rowsDirect(info, "ReconciliationWork");
    const current = rows.find((row) => row.work_uuid === workUuid);
    if (!current) throw new Error("Cleanup work was not found in MIRROR.");
    const updated = { ...current, status: outcome, processor_version: payload.processor_version || current.processor_version || "", result_json: JSON.stringify(payload.result || {}), last_error: payload.error || "", next_attempt_at: payload.next_attempt_at || "", updated_at: now(), completed_at: outcome === "complete" ? now() : "" };
    delete updated.__row;
    await replaceRowDirect(info, "ReconciliationWork", current.__row, updated);
    const verify = (await rowsDirect(info, "ReconciliationWork")).find((row) => row.work_uuid === workUuid);
    if (!verify || verify.status !== outcome) throw new Error("Cleanup result did not read back from MIRROR.");
    return { work: verify, readback_verified: true };
  }

  async function migrateReceiptQueue() {
    if (!globalThis.MiraReceiptQueue?.rows) return;
    const receiptRows = await globalThis.MiraReceiptQueue.rows();
    for (const item of receiptRows) {
      if (!item.receipt_uuid || item.status === "complete") continue;
      await queueWork({ feature_namespace: "receipts", source_type: "receipt", source_uuid: item.receipt_uuid, work_type: "receipt.reconcile", allowed_mutations: ["receipt_fields","receipt_lines","merchant","merchant_location","inventory_suggestions"] });
    }
  }

  async function summary() {
    const [work, usage, processors] = await Promise.all([rawRows("ReconciliationWork"), rawRows("AIUsage"), rawRows("AIProcessors")]);
    const counts = {};
    work.forEach((row) => { counts[row.status] = (counts[row.status] || 0) + 1; });
    const today = new Date().toISOString().slice(0, 10), month = today.slice(0, 7);
    const costToday = usage.filter((row) => String(row.created_at).slice(0, 10) === today).reduce((sum, row) => sum + Number(row.estimated_cost || 0), 0);
    const costMonth = usage.filter((row) => String(row.created_at).slice(0, 7) === month).reduce((sum, row) => sum + Number(row.estimated_cost || 0), 0);
    return { waiting: (counts.queued || 0) + (counts.processing || 0) + (counts.failed_retryable || 0), needs_review: (counts.needs_review || 0) + (counts.quarantined || 0), counts, api_cost: { today: costToday, month: costMonth, currency: "USD", metered_processors_enabled: processors.some((row) => row.enabled !== "0" && row.metered === "1") }, default_daily_cleanup_time: "00:01", readback_verified: true };
  }

  async function listWork(status = "") {
    let rows = await rawRows("ReconciliationWork");
    if (status) rows = rows.filter((row) => row.status === status);
    rows.sort((a, b) => Number(b.priority || 0) - Number(a.priority || 0) || String(a.created_at).localeCompare(String(b.created_at)));
    return { items: rows, count: rows.length };
  }

  async function recordUsage(payload) {
    const cost = Number(payload.estimated_cost || 0);
    if (!Number.isFinite(cost) || cost < 0) throw new Error("Paid AI cost must be zero or greater.");
    const row = { usage_uuid: payload.usage_uuid || uuid(), processor_uuid: payload.processor_uuid || "", provider_kind: payload.provider_kind || "unknown", model_name: payload.model_name || "", work_uuid: payload.work_uuid || "", feature_namespace: payload.feature_namespace || "", input_units: payload.input_units || 0, output_units: payload.output_units || 0, cached_units: payload.cached_units || 0, estimated_cost: cost, currency: payload.currency || "USD", price_snapshot_json: JSON.stringify(payload.price_snapshot || {}), created_at: now() };
    await append("AIUsage", row);
    const verify = (await rawRows("AIUsage")).find((item) => item.usage_uuid === row.usage_uuid);
    if (!verify || Number(verify.estimated_cost || 0) !== cost) throw new Error("AI usage cost did not read back from MIRROR.");
    return { usage: verify, readback_verified: true };
  }

  async function registerProcessor(payload) {
    const config = payload.config || {};
    if (Object.keys(config).some((key) => ["api_key","token","secret","password"].includes(key.toLowerCase()))) throw new Error("Processor credentials belong in protected secret storage, not MIRROR.");
    const id = payload.processor_uuid || uuid(), timestamp = now();
    const row = await upsert("AIProcessors", "processor_uuid", id, { processor_uuid: id, provider_kind: payload.provider_kind || "custom", display_name: payload.display_name || "AI processor", model_name: payload.model_name || "", execution_mode: payload.execution_mode || "api", capabilities_json: JSON.stringify(payload.capabilities || []), enabled: payload.enabled === false ? "0" : "1", metered: payload.metered ? "1" : "0", local_only: payload.local_only ? "1" : "0", privacy_class: payload.privacy_class || "standard", priority: payload.priority || "100", health: payload.health || "unknown", config_json: JSON.stringify(config), created_at: timestamp, updated_at: timestamp });
    return { processor: row, readback_verified: true };
  }

  async function processors() { return { processors: await rawRows("AIProcessors") }; }

  async function setFeaturePolicy(namespace, payload) {
    const timestamp = now();
    const row = await upsert("FeatureProcessingPolicies", "feature_namespace", namespace, { feature_namespace: namespace, enabled: payload.enabled === false ? "0" : "1", processing_mode: payload.processing_mode || "deferred_reconciliation", freshness: payload.freshness || "next_daily_cleanup", capabilities_json: JSON.stringify(payload.capabilities || ["text_reasoning"]), allowed_mutations_json: JSON.stringify(payload.allowed_mutations || []), preferred_processor_uuid: payload.preferred_processor_uuid || "", local_only: payload.local_only ? "1" : "0", max_cost_per_work: payload.max_cost_per_work ?? "", confidence_threshold: payload.confidence_threshold || "0.90", created_at: timestamp, updated_at: timestamp });
    return { policy: row, readback_verified: true };
  }

  async function canonicalTableRows(table) {
    const info = await ensureTables();
    const range = encodeRange(`'${table}'!A:ZZ`);
    const result = (await request("GET", `https://sheets.googleapis.com/v4/spreadsheets/${encodeURIComponent(info.workbook_id)}/values/${range}?majorDimension=ROWS`)).json;
    const values = result.values || [];
    const headers = values[0] || [];
    return { info, headers, rows: values.slice(1).map((row, index) => ({ __row: index + 2, ...Object.fromEntries(headers.map((key, offset) => [key, row[offset] ?? ""])) })) };
  }

  async function applyUserCorrection(entityType, entityUuid, fieldName, confirmedValue) {
    const configs = {
      asset: { table: "Assets", id: "asset_uuid", allowed: new Set(["name","description","category_uuid","location_uuid","status"]) },
      receipt: { table: "Receipts", id: "receipt_uuid", allowed: new Set(["merchant_display","purchase_at","currency","subtotal","tax","total","status"]) }
    };
    const config = configs[entityType];
    if (!config || !config.allowed.has(fieldName)) return { applied: false, previous_value: null };
    const data = await canonicalTableRows(config.table);
    const current = data.rows.find((row) => row[config.id] === entityUuid);
    if (!current) throw new Error(`${entityType === "asset" ? "Item" : "Receipt"} was not found in MIRROR.`);
    const fieldIndex = data.headers.indexOf(fieldName);
    if (fieldIndex < 0) throw new Error(`MIRROR does not expose ${fieldName} on this record.`);
    const cell = `'${config.table}'!${columnName(fieldIndex + 1)}${current.__row}`;
    await request("PUT", `https://sheets.googleapis.com/v4/spreadsheets/${encodeURIComponent(data.info.workbook_id)}/values/${encodeRange(cell)}?valueInputOption=RAW`, JSON.stringify({ range: cell, majorDimension: "ROWS", values: [[confirmedValue]] }));
    const verify = await canonicalTableRows(config.table);
    const after = verify.rows.find((row) => row[config.id] === entityUuid);
    if (!after || String(after[fieldName] ?? "") !== String(confirmedValue ?? "")) throw new Error("Your correction was written but did not read back correctly from MIRROR.");
    return { applied: true, previous_value: current[fieldName] ?? null };
  }

  async function recordCorrection(payload) {
    const entityType = String(payload.entity_type || "").trim(), entityUuid = String(payload.entity_uuid || "").trim(), fieldName = String(payload.field_name || "").trim();
    if (!entityType || !entityUuid || !fieldName) throw new Error("Correction requires a record type, record ID, and field.");
    const applied = await applyUserCorrection(entityType, entityUuid, fieldName, payload.confirmed_value);
    const correction = { correction_uuid: payload.correction_uuid || uuid(), entity_type: entityType, entity_uuid: entityUuid, field_name: fieldName, previous_value_json: JSON.stringify(payload.previous_value !== undefined ? payload.previous_value : applied.previous_value), confirmed_value_json: JSON.stringify(payload.confirmed_value), reason: payload.reason || "Corrected in MIRA app", source: "user", created_at: now() };
    await append("UserCorrections", correction);
    if (payload.recognition_profile?.lookup_key) {
      const profile = payload.recognition_profile;
      await upsert("RecognitionProfiles", "profile_uuid", profile.profile_uuid || uuid(), { profile_uuid: profile.profile_uuid || uuid(), profile_type: profile.profile_type || "correction", lookup_key: profile.lookup_key, value_json: JSON.stringify(profile.value ?? payload.confirmed_value), confidence: "1", user_confirmed: "1", source_entity_type: entityType, source_entity_uuid: entityUuid, created_at: now(), updated_at: now() });
    }
    const verify = (await rawRows("UserCorrections")).find((row) => row.correction_uuid === correction.correction_uuid);
    if (!verify) throw new Error("Your correction did not read back from MIRROR.");
    return { correction: verify, applied_to_record: applied.applied, authority: "user_confirmed", readback_verified: true };
  }

  async function recognition(profileType, lookupKey) {
    const rows = await rawRows("RecognitionProfiles");
    const match = rows.find((row) => row.profile_type === profileType && row.lookup_key === lookupKey);
    if (!match) return { match: null };
    return { match: { ...match, value: json(match.value_json, null) } };
  }

  async function upsertMerchantLocation(payload) {
    const id = payload.merchant_location_uuid || uuid();
    const existing = (await rawRows("MerchantLocations")).find((row) => row.merchant_location_uuid === id);
    const userConfirmed = payload.user_confirmed ? "1" : (existing?.user_confirmed || "0");
    const row = await upsert("MerchantLocations", "merchant_location_uuid", id, { merchant_location_uuid: id, merchant_uuid: payload.merchant_uuid || "", display_name: payload.display_name || "Store location", store_number: payload.store_number || "", address_line1: payload.address_line1 || "", address_line2: payload.address_line2 || "", city: payload.city || "", region: payload.region || "", postal_code: payload.postal_code || "", country: payload.country || "", latitude: payload.latitude ?? "", longitude: payload.longitude ?? "", metadata_json: JSON.stringify(payload.metadata || {}), user_confirmed: userConfirmed, created_at: existing?.created_at || now(), updated_at: now() });
    if (payload.receipt_uuid) await upsert("ReceiptMerchantLocationLinks", "receipt_uuid", payload.receipt_uuid, { receipt_uuid: payload.receipt_uuid, merchant_location_uuid: id, confidence: payload.confidence ?? (payload.user_confirmed ? 1 : 0.9), user_confirmed: payload.user_confirmed ? "1" : "0", linked_at: now() });
    return { merchant_location: row, readback_verified: true };
  }

  document.addEventListener("mira:provider-state", (event) => {
    if (event.detail?.provider !== "google_workspace" || event.detail?.mirror_verified !== true) return;
    ensureTables().then(migrateReceiptQueue).catch((error) => globalThis.MiraActionAudit?.announce?.(error?.message || String(error)));
  });

  globalThis.MiraCloudReconciliation = { ensureTables, queueWork, claimWork, finishWork, listWork, summary, recordUsage, registerProcessor, processors, setFeaturePolicy, recordCorrection, recognition, upsertMerchantLocation, migrateReceiptQueue };
})();
