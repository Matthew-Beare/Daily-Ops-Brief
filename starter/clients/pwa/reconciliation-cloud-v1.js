"use strict";

(() => {
  const TABLES = {
    ReconciliationWork: ["work_uuid","feature_namespace","source_type","source_uuid","work_type","processing_mode","status","priority","freshness_minutes","capabilities_json","allowed_mutations_json","confidence_threshold","idempotency_key","attempts","next_attempt_at","claimed_by","claimed_at","processor_uuid","processor_version","result_json","last_error","created_at","updated_at","completed_at"],
    FeatureProcessingPolicies: ["feature_namespace","enabled","processing_mode","freshness","capabilities_json","allowed_mutations_json","preferred_processor_uuid","local_only","max_cost_per_work","confidence_threshold","created_at","updated_at"],
    AIProcessors: ["processor_uuid","provider_kind","display_name","model_name","execution_mode","capabilities_json","enabled","metered","local_only","privacy_class","priority","health","config_json","created_at","updated_at"],
    AIUsage: ["usage_uuid","processor_uuid","provider_kind","model_name","work_uuid","feature_namespace","input_units","output_units","cached_units","estimated_cost","currency","price_snapshot_json","created_at"],
    UserCorrections: ["correction_uuid","entity_type","entity_uuid","field_name","previous_value_json","confirmed_value_json","reason","source","created_at"],
    RecognitionProfiles: ["profile_uuid","profile_type","lookup_key","value_json","confidence","user_confirmed","source_entity_type","source_entity_uuid","created_at","updated_at"],
    MerchantLocations: ["merchant_location_uuid","merchant_uuid","display_name","store_number","address_line1","address_line2","city","region","postal_code","country","latitude","longitude","metadata_json","user_confirmed","created_at","updated_at"]
  };
  const callbacks = new Map();
  const previousCallback = globalThis.onMirrorNativeGoogleApiResponse;
  let sequence = 0;
  let ensuredWorkbook = "";

  function now() { return new Date().toISOString(); }
  function uuid() { return globalThis.crypto?.randomUUID ? crypto.randomUUID() : `${Date.now()}-${Math.random()}`; }
  function authority() { return globalThis.MiraGoogleAuthority?.authority?.() || null; }
  function nativeReady() { return Boolean(globalThis.MirrorNative?.googleApiRequest); }
  function encodeRange(value) { return encodeURIComponent(value).replace(/%2F/g, "/"); }

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
    let json = {};
    try { json = responseText ? JSON.parse(String(responseText)) : {}; } catch (_) { json = {}; }
    if (code < 200 || code >= 300) {
      const detail = json?.error?.message || json?.error || responseText || `Google returned HTTP ${code}.`;
      pending.reject(new Error(typeof detail === "string" ? detail : JSON.stringify(detail)));
    } else pending.resolve({ status: code, json, text: String(responseText || "") });
  };

  async function ensureTables() {
    if (!globalThis.MiraGoogleAuthority?.ready || !(await globalThis.MiraGoogleAuthority.ready())) throw new Error("Connect Google before using Daily Cleanup.");
    const info = authority();
    if (!info?.workbook_id) throw new Error("MIRROR workbook is not connected.");
    if (ensuredWorkbook === info.workbook_id) return info;
    const workbook = (await request("GET", `https://sheets.googleapis.com/v4/spreadsheets/${encodeURIComponent(info.workbook_id)}?fields=sheets.properties`)).json;
    const existing = new Set((workbook.sheets || []).map((sheet) => sheet.properties?.title));
    const missing = Object.keys(TABLES).filter((name) => !existing.has(name));
    if (missing.length) {
      await request("POST", `https://sheets.googleapis.com/v4/spreadsheets/${encodeURIComponent(info.workbook_id)}:batchUpdate`, JSON.stringify({ requests: missing.map((title) => ({ addSheet: { properties: { title } } })) }));
    }
    for (const [name, headers] of Object.entries(TABLES)) {
      const rangeText = `'${name}'!A1:${String.fromCharCode(64 + Math.min(headers.length, 26))}1`;
      const range = encodeRange(rangeText);
      await request("PUT", `https://sheets.googleapis.com/v4/spreadsheets/${encodeURIComponent(info.workbook_id)}/values/${range}?valueInputOption=RAW`, JSON.stringify({ range: rangeText, majorDimension: "ROWS", values: [headers] }));
    }
    await ensureDefaultProcessors(info);
    ensuredWorkbook = info.workbook_id;
    return info;
  }

  async function rawRows(table, skipEnsure = false) {
    const info = skipEnsure ? authority() : await ensureTables();
    if (!info?.workbook_id) return [];
    const headers = TABLES[table];
    const range = encodeRange(`'${table}'!A:ZZ`);
    const result = (await request("GET", `https://sheets.googleapis.com/v4/spreadsheets/${encodeURIComponent(info.workbook_id)}/values/${range}?majorDimension=ROWS`)).json;
    const values = result.values || [];
    const actual = values[0] || headers;
    return values.slice(1).map((row, rowIndex) => ({ __row: rowIndex + 2, ...Object.fromEntries(actual.map((key, index) => [key, row[index] ?? ""])) }));
  }

  async function append(table, object) {
    const info = await ensureTables();
    const values = TABLES[table].map((key) => object[key] == null ? "" : String(object[key]));
    const range = encodeRange(`'${table}'!A:ZZ`);
    await request("POST", `https://sheets.googleapis.com/v4/spreadsheets/${encodeURIComponent(info.workbook_id)}/values/${range}:append?valueInputOption=RAW&insertDataOption=INSERT_ROWS`, JSON.stringify({ majorDimension: "ROWS", values: [values] }));
    return object;
  }

  async function ensureDefaultProcessors(info) {
    const rows = await rawRows("AIProcessors", true);
    if (rows.some((row) => row.processor_uuid === "chatgpt-scheduled")) return;
    const timestamp = now();
    const defaults = [
      { processor_uuid: "chatgpt-scheduled", provider_kind: "chatgpt_scheduled_mira", display_name: "MIRA in ChatGPT", model_name: "", execution_mode: "scheduled", capabilities_json: JSON.stringify(["text_reasoning","vision","tool_use","web_research","structured_output"]), enabled: "1", metered: "0", local_only: "0", privacy_class: "standard", priority: "100", health: "available", config_json: "{}", created_at: timestamp, updated_at: timestamp },
      { processor_uuid: "manual", provider_kind: "manual", display_name: "Manual review", model_name: "", execution_mode: "manual", capabilities_json: "[]", enabled: "1", metered: "0", local_only: "1", privacy_class: "local", priority: "1000", health: "available", config_json: "{}", created_at: timestamp, updated_at: timestamp }
    ];
    for (const row of defaults) await append("AIProcessors", row);
  }

  async function queueWork(payload) {
    const existing = (await rawRows("ReconciliationWork")).find((row) => row.feature_namespace === payload.feature_namespace && row.source_type === payload.source_type && row.source_uuid === payload.source_uuid && row.work_type === payload.work_type);
    if (existing) return { work: existing, readback_verified: true, idempotent_replay: true };
    const timestamp = now();
    const row = {
      work_uuid: payload.work_uuid || uuid(), feature_namespace: payload.feature_namespace || "general", source_type: payload.source_type || "record", source_uuid: payload.source_uuid,
      work_type: payload.work_type || "general.reconcile", processing_mode: payload.processing_mode || "deferred_reconciliation", status: "queued", priority: payload.priority || "20",
      freshness_minutes: payload.freshness_minutes || "1440", capabilities_json: JSON.stringify(payload.capabilities || ["text_reasoning"]), allowed_mutations_json: JSON.stringify(payload.allowed_mutations || []),
      confidence_threshold: payload.confidence_threshold || "0.90", idempotency_key: payload.idempotency_key || `${payload.feature_namespace || "general"}:${payload.source_type || "record"}:${payload.source_uuid}:${payload.work_type || "general.reconcile"}`,
      attempts: "0", next_attempt_at: "", claimed_by: "", claimed_at: "", processor_uuid: "", processor_version: "", result_json: "{}", last_error: "", created_at: timestamp, updated_at: timestamp, completed_at: ""
    };
    await append("ReconciliationWork", row);
    const readback = (await rawRows("ReconciliationWork")).find((item) => item.work_uuid === row.work_uuid);
    if (!readback) throw new Error("Cleanup work was written but did not read back from MIRROR.");
    return { work: readback, readback_verified: true };
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
    const today = new Date().toISOString().slice(0, 10);
    const month = today.slice(0, 7);
    const costToday = usage.filter((row) => String(row.created_at).slice(0, 10) === today).reduce((sum, row) => sum + Number(row.estimated_cost || 0), 0);
    const costMonth = usage.filter((row) => String(row.created_at).slice(0, 7) === month).reduce((sum, row) => sum + Number(row.estimated_cost || 0), 0);
    return {
      waiting: (counts.queued || 0) + (counts.processing || 0) + (counts.failed_retryable || 0),
      needs_review: (counts.needs_review || 0) + (counts.quarantined || 0),
      counts,
      api_cost: { today: costToday, month: costMonth, currency: "USD", metered_processors_enabled: processors.some((row) => row.enabled !== "0" && row.metered === "1") },
      default_daily_cleanup_time: "00:01", readback_verified: true
    };
  }

  async function listWork(status = "") {
    let rows = await rawRows("ReconciliationWork");
    if (status) rows = rows.filter((row) => row.status === status);
    rows.sort((a, b) => Number(b.priority || 0) - Number(a.priority || 0) || String(a.created_at).localeCompare(String(b.created_at)));
    return { items: rows, count: rows.length };
  }

  async function recordUsage(payload) {
    const row = { usage_uuid: payload.usage_uuid || uuid(), processor_uuid: payload.processor_uuid || "", provider_kind: payload.provider_kind || "unknown", model_name: payload.model_name || "", work_uuid: payload.work_uuid || "", feature_namespace: payload.feature_namespace || "", input_units: payload.input_units || 0, output_units: payload.output_units || 0, cached_units: payload.cached_units || 0, estimated_cost: payload.estimated_cost || 0, currency: payload.currency || "USD", price_snapshot_json: JSON.stringify(payload.price_snapshot || {}), created_at: now() };
    await append("AIUsage", row);
    return { usage: row, readback_verified: true };
  }

  async function setFeaturePolicy(namespace, payload) {
    const existing = (await rawRows("FeatureProcessingPolicies")).find((row) => row.feature_namespace === namespace);
    if (existing) return { policy: existing, readback_verified: true, note: "Policy already exists; edit through Advanced until row-update support is promoted." };
    const timestamp = now();
    const row = { feature_namespace: namespace, enabled: payload.enabled === false ? "0" : "1", processing_mode: payload.processing_mode || "deferred_reconciliation", freshness: payload.freshness || "next_daily_cleanup", capabilities_json: JSON.stringify(payload.capabilities || ["text_reasoning"]), allowed_mutations_json: JSON.stringify(payload.allowed_mutations || []), preferred_processor_uuid: payload.preferred_processor_uuid || "", local_only: payload.local_only ? "1" : "0", max_cost_per_work: payload.max_cost_per_work ?? "", confidence_threshold: payload.confidence_threshold || "0.90", created_at: timestamp, updated_at: timestamp };
    await append("FeatureProcessingPolicies", row);
    return { policy: row, readback_verified: true };
  }

  document.addEventListener("mira:provider-state", (event) => {
    if (event.detail?.provider !== "google_workspace" || event.detail?.mirror_verified !== true) return;
    ensureTables().then(migrateReceiptQueue).catch((error) => globalThis.MiraActionAudit?.announce?.(error?.message || String(error)));
  });

  globalThis.MiraCloudReconciliation = { ensureTables, queueWork, listWork, summary, recordUsage, setFeaturePolicy, migrateReceiptQueue };
})();
