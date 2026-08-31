"use strict";

(() => {
  const WORKBOOK_NAME = "MIRA MIRROR Reality Record";
  const MANIFEST_NAME = "MIRA MIRROR Authority Manifest.json";
  const FOLDER_NAME = "MIRA MIRROR";
  const AUTHORITY_STATE_KEY = "mira.google.authority.v1";
  const DEPLOYMENT_KEY = "mira.deployment.mode.v1";
  const TABLES = {
    Settings: ["setting_key", "value_json", "updated_at", "updated_by"],
    Assets: ["asset_uuid", "name", "description", "category_uuid", "location_uuid", "status", "metadata_json", "created_at", "updated_at"],
    Identifiers: ["identifier_uuid", "asset_uuid", "namespace", "value", "source", "provenance_url", "created_at", "retired_at"],
    Categories: ["category_uuid", "name", "parent_category_uuid", "created_at", "updated_at"],
    Locations: ["location_uuid", "name", "location_type", "parent_location_uuid", "created_at", "updated_at"],
    ContainerLinks: ["container_asset_uuid", "container_location_uuid", "created_at", "updated_at"],
    Merchants: ["merchant_uuid", "canonical_name", "normalized_name", "official_domain", "aliases_json", "metadata_json", "created_at", "updated_at"],
    Receipts: ["receipt_uuid", "merchant_uuid", "merchant_display", "purchase_at", "currency", "subtotal", "tax", "total", "evidence_drive_file_id", "raw_extract_json", "status", "created_at", "updated_at"],
    ReceiptLines: ["receipt_line_uuid", "receipt_uuid", "line_index", "description", "retailer_sku", "quantity", "unit_price", "amount", "asset_uuid", "status", "candidate_json", "provenance_json", "created_at", "updated_at"],
    Evidence: ["evidence_uuid", "asset_uuid", "receipt_uuid", "drive_file_id", "filename", "mime_type", "sha256", "role", "source", "provenance_url", "created_at"],
    AssetMeters: ["meter_uuid", "asset_uuid", "meter_type", "unit", "label", "created_at", "updated_at"],
    MeterReadings: ["reading_uuid", "meter_uuid", "value", "observed_at", "source", "evidence_uuid", "created_at"],
    MaintenanceEvents: ["maintenance_uuid", "asset_uuid", "service_type", "performed_at", "meter_uuid", "meter_value", "receipt_uuid", "receipt_line_uuid", "total_cost", "notes", "metadata_json", "created_at", "updated_at"],
    Media: ["media_uuid", "media_type", "title", "year", "metadata_json", "created_at", "updated_at"],
    MediaIdentifiers: ["namespace", "value", "media_uuid", "created_at"],
    MediaProviderBindings: ["media_uuid", "integration_uuid", "provider_item_id", "provider_json", "last_verified_at"],
    IntegrationInstances: ["integration_uuid", "service_type", "display_name", "connection_mode", "capabilities_json", "state", "bridge_device_uuid", "created_at", "updated_at"],
    IntegrationActions: ["action_uuid", "integration_uuid", "capability", "action_type", "payload_json", "idempotency_key", "created_at", "expires_at", "state", "claimed_device_uuid"],
    IntegrationResults: ["result_uuid", "action_uuid", "succeeded", "result_json", "readback_verified", "completed_at", "device_uuid"],
    BackupPolicy: ["singleton", "enabled", "full_interval_days", "incremental_interval_days", "destination", "retention_mode", "updated_at"],
    BackupRuns: ["backup_uuid", "requested_type", "effective_type", "destination", "status", "sha256", "size_bytes", "provider_locator", "readback_verified", "detail_json", "started_at", "completed_at"],
    FeatureRequests: ["request_uuid", "title", "request_text", "acceptance_json", "target_surfaces_json", "status", "source", "created_at", "updated_at"],
    OrderEvents: ["event_uuid", "order_uuid", "event_type", "provider", "external_reference", "payload_json", "observed_at", "created_at"],
    Audit: ["event_uuid", "event_type", "target_uuid", "actor", "payload_json", "created_at"]
  };
  const PRIMARY = {
    Settings: "setting_key", Assets: "asset_uuid", Identifiers: "identifier_uuid", Categories: "category_uuid",
    Locations: "location_uuid", Merchants: "merchant_uuid", Receipts: "receipt_uuid", ReceiptLines: "receipt_line_uuid",
    Evidence: "evidence_uuid", AssetMeters: "meter_uuid", MeterReadings: "reading_uuid", MaintenanceEvents: "maintenance_uuid",
    Media: "media_uuid", IntegrationInstances: "integration_uuid", IntegrationActions: "action_uuid", IntegrationResults: "result_uuid",
    BackupRuns: "backup_uuid", FeatureRequests: "request_uuid", OrderEvents: "event_uuid", Audit: "event_uuid"
  };
  const callbacks = new Map();
  let sequence = 0;
  let authority = readLocalAuthority();
  let bootstrapPromise = null;

  function now() { return new Date().toISOString(); }
  function makeUuid() { return globalThis.crypto?.randomUUID ? crypto.randomUUID() : `${Date.now()}-${Math.random()}`; }
  function mode() { return localStorage.getItem(DEPLOYMENT_KEY) || "cloud"; }
  function cloudMode() { return mode() === "cloud" || mode() === "cloud_local"; }
  function googleConnected() { return globalThis.MiraProviderConnect?.state?.().provider === "google_workspace" && globalThis.MiraProviderConnect?.isCloudConnected?.(); }
  function nativeTransportReady() { return Boolean(globalThis.MirrorNative?.googleApiRequest); }
  function available() { return cloudMode() && googleConnected() && nativeTransportReady(); }

  function announce(message) {
    if (globalThis.MiraActionAudit?.announce) globalThis.MiraActionAudit.announce(message);
    else if (typeof setStatus === "function") setStatus(message);
  }

  function readLocalAuthority() {
    try { return JSON.parse(localStorage.getItem(AUTHORITY_STATE_KEY) || "null"); } catch (_) { return null; }
  }

  function saveLocalAuthority(value) {
    authority = value;
    localStorage.setItem(AUTHORITY_STATE_KEY, JSON.stringify(value));
    return value;
  }

  function encodeQueryValue(value) { return String(value).replace(/\\/g, "\\\\").replace(/'/g, "\\'"); }
  function encodeRange(value) { return encodeURIComponent(value).replace(/%2F/g, "/"); }

  function nativeRequest(method, url, body = null, contentType = "application/json; charset=utf-8") {
    if (!nativeTransportReady()) return Promise.reject(new Error("This build has no Google data transport."));
    const requestId = `google-${Date.now()}-${++sequence}`;
    return new Promise((resolve, reject) => {
      const timer = setTimeout(() => { callbacks.delete(requestId); reject(new Error("Google did not answer within two minutes.")); }, 120000);
      callbacks.set(requestId, { resolve, reject, timer });
      try {
        globalThis.MirrorNative.googleApiRequest(requestId, method, url, body == null ? "" : String(body), contentType || "application/json; charset=utf-8");
      } catch (error) {
        clearTimeout(timer); callbacks.delete(requestId); reject(error);
      }
    });
  }

  function nativeRequestBase64(method, url, bodyBase64, contentType) {
    if (!globalThis.MirrorNative?.googleApiRequestBase64) return Promise.reject(new Error("This build cannot upload binary evidence to Google."));
    const requestId = `google-bin-${Date.now()}-${++sequence}`;
    return new Promise((resolve, reject) => {
      const timer = setTimeout(() => { callbacks.delete(requestId); reject(new Error("Google evidence upload timed out.")); }, 120000);
      callbacks.set(requestId, { resolve, reject, timer });
      try { globalThis.MirrorNative.googleApiRequestBase64(requestId, method, url, bodyBase64, contentType || "application/octet-stream"); }
      catch (error) { clearTimeout(timer); callbacks.delete(requestId); reject(error); }
    });
  }

  globalThis.onMirrorNativeGoogleApiResponse = function onGoogleApiResponse(requestId, status, responseText) {
    const pending = callbacks.get(requestId); if (!pending) return;
    callbacks.delete(requestId); clearTimeout(pending.timer);
    const response = { status: Number(status), ok: Number(status) >= 200 && Number(status) < 300, text: String(responseText || "") };
    try { response.json = response.text ? JSON.parse(response.text) : {}; } catch (_) { response.json = {}; }
    if (!response.ok) {
      const detail = response.json?.error?.message || response.json?.error || response.text || `Google returned HTTP ${response.status}.`;
      pending.reject(new Error(typeof detail === "string" ? detail : JSON.stringify(detail)));
    } else pending.resolve(response);
  };

  async function driveSearch(name, mimeType = "") {
    let q = `trashed=false and name='${encodeQueryValue(name)}'`;
    if (mimeType) q += ` and mimeType='${encodeQueryValue(mimeType)}'`;
    const url = `https://www.googleapis.com/drive/v3/files?q=${encodeURIComponent(q)}&spaces=drive&fields=files(id,name,mimeType,parents,appProperties,createdTime,modifiedTime)&pageSize=20`;
    const result = (await nativeRequest("GET", url)).json;
    return result.files || [];
  }

  async function createFolder() {
    const payload = { name: FOLDER_NAME, mimeType: "application/vnd.google-apps.folder", appProperties: { mira_mirror: "authority_folder", schema_version: "3" } };
    return (await nativeRequest("POST", "https://www.googleapis.com/drive/v3/files?fields=id,name,mimeType,parents", JSON.stringify(payload))).json;
  }

  async function createWorkbook(folderId) {
    const payload = {
      properties: { title: WORKBOOK_NAME },
      sheets: Object.keys(TABLES).map((title) => ({ properties: { title } }))
    };
    const created = (await nativeRequest("POST", "https://sheets.googleapis.com/v4/spreadsheets?fields=spreadsheetId,properties,sheets.properties", JSON.stringify(payload))).json;
    const spreadsheetId = created.spreadsheetId;
    const data = Object.entries(TABLES).map(([name, headers]) => ({ range: `'${name}'!A1`, values: [headers] }));
    await nativeRequest("POST", `https://sheets.googleapis.com/v4/spreadsheets/${encodeURIComponent(spreadsheetId)}/values:batchUpdate`, JSON.stringify({ valueInputOption: "RAW", data }));
    try {
      await nativeRequest("PATCH", `https://www.googleapis.com/drive/v3/files/${encodeURIComponent(spreadsheetId)}?addParents=${encodeURIComponent(folderId)}&removeParents=root&fields=id,parents`, "{}");
    } catch (_) { /* workbook identity is still valid even if Drive keeps its original parent */ }
    return { id: spreadsheetId, name: WORKBOOK_NAME };
  }

  async function createManifest(folderId, workbookId) {
    const authorityUuid = makeUuid();
    const metadata = {
      name: MANIFEST_NAME,
      mimeType: "application/json",
      parents: [folderId],
      appProperties: { mira_mirror: "authority_manifest", schema_version: "3", authority_uuid: authorityUuid, workbook_id: workbookId }
    };
    const created = (await nativeRequest("POST", "https://www.googleapis.com/drive/v3/files?fields=id,name,parents,appProperties", JSON.stringify(metadata))).json;
    const manifest = {
      schema_version: 3,
      authority_uuid: authorityUuid,
      authority_name: WORKBOOK_NAME,
      workbook_file_id: workbookId,
      folder_id: folderId,
      created_at: now(),
      product: "MIRA",
      data_layer: "MIRROR"
    };
    await nativeRequest("PATCH", `https://www.googleapis.com/upload/drive/v3/files/${encodeURIComponent(created.id)}?uploadType=media`, JSON.stringify(manifest), "application/json; charset=utf-8");
    return { ...manifest, manifest_file_id: created.id };
  }

  async function readManifest(fileId) {
    const result = await nativeRequest("GET", `https://www.googleapis.com/drive/v3/files/${encodeURIComponent(fileId)}?alt=media`);
    const manifest = JSON.parse(result.text || "{}");
    if (!manifest.workbook_file_id || !manifest.authority_uuid) throw new Error("The MIRROR manifest exists but is incomplete. MIRA stopped rather than creating a competing database.");
    return { ...manifest, manifest_file_id: fileId };
  }

  async function verifyHeaders(workbookId) {
    for (const [table, expected] of Object.entries(TABLES)) {
      const range = encodeRange(`'${table}'!1:1`);
      const response = await nativeRequest("GET", `https://sheets.googleapis.com/v4/spreadsheets/${encodeURIComponent(workbookId)}/values/${range}`);
      const actual = response.json?.values?.[0] || [];
      if (JSON.stringify(actual) !== JSON.stringify(expected)) throw new Error(`MIRROR table ${table} does not match this MIRA release. Run migration/upgrade before writing.`);
    }
  }

  async function bootstrap(force = false) {
    if (!available()) throw new Error("Connect Google before MIRA can open the cloud MIRROR database.");
    if (bootstrapPromise && !force) return bootstrapPromise;
    bootstrapPromise = (async () => {
      const manifests = await driveSearch(MANIFEST_NAME, "application/json");
      const books = await driveSearch(WORKBOOK_NAME, "application/vnd.google-apps.spreadsheet");
      if (manifests.length > 1 || books.length > 1) throw new Error("MIRA found more than one MIRROR database. Nothing was changed. Open migration/recovery to choose the correct one.");
      if ((manifests.length === 1) !== (books.length === 1)) throw new Error("MIRA found only part of the MIRROR database. Nothing was created or overwritten. Use recovery to reconcile it.");
      let resolved;
      if (!manifests.length) {
        const folderMatches = await driveSearch(FOLDER_NAME, "application/vnd.google-apps.folder");
        const folder = folderMatches.length === 1 ? folderMatches[0] : await createFolder();
        if (folderMatches.length > 1) throw new Error("MIRA found multiple MIRROR folders. Nothing was changed.");
        const workbook = await createWorkbook(folder.id);
        resolved = await createManifest(folder.id, workbook.id);
      } else {
        resolved = await readManifest(manifests[0].id);
        if (resolved.workbook_file_id !== books[0].id) throw new Error("The MIRROR manifest points to a different workbook. MIRA stopped before writing.");
      }
      await verifyHeaders(resolved.workbook_file_id);
      saveLocalAuthority({ ...resolved, workbook_id: resolved.workbook_file_id, verified_at: now() });
      announce("MIRROR is connected and verified in Google.");
      return authority;
    })();
    try { return await bootstrapPromise; } finally { bootstrapPromise = null; }
  }

  async function ready() {
    if (!available()) return false;
    if (!authority?.workbook_id) {
      try { await bootstrap(); } catch (_) { return false; }
    }
    return Boolean(authority?.workbook_id);
  }

  async function tableValues(table) {
    if (!TABLES[table]) throw new Error(`Unknown MIRROR table ${table}.`);
    await bootstrap();
    const range = encodeRange(`'${table}'!A:ZZ`);
    const response = await nativeRequest("GET", `https://sheets.googleapis.com/v4/spreadsheets/${encodeURIComponent(authority.workbook_id)}/values/${range}?majorDimension=ROWS`);
    const values = response.json?.values || [];
    const headers = values[0] || TABLES[table];
    return { headers, rows: values.slice(1), objects: values.slice(1).map((row) => Object.fromEntries(headers.map((key, index) => [key, row[index] ?? ""]))) };
  }

  function rowValues(table, object) { return TABLES[table].map((key) => object[key] == null ? "" : String(object[key])); }

  async function appendRow(table, object, readbackPredicate = null) {
    await bootstrap();
    const range = encodeRange(`'${table}'!A1`);
    await nativeRequest("POST", `https://sheets.googleapis.com/v4/spreadsheets/${encodeURIComponent(authority.workbook_id)}/values/${range}:append?valueInputOption=RAW&insertDataOption=INSERT_ROWS`, JSON.stringify({ values: [rowValues(table, object)] }));
    const data = await tableValues(table);
    const predicate = readbackPredicate || ((row) => PRIMARY[table] && row[PRIMARY[table]] === object[PRIMARY[table]]);
    const found = data.objects.find(predicate);
    if (!found) throw new Error(`${table} write did not read back from Google. MIRA did not report success.`);
    return found;
  }

  async function updateRow(table, primaryValue, update) {
    const primary = PRIMARY[table]; if (!primary) throw new Error(`MIRROR does not have a simple update key for ${table}.`);
    const data = await tableValues(table);
    const index = data.objects.findIndex((row) => row[primary] === primaryValue);
    if (index < 0) throw new Error(`${table} record not found.`);
    const merged = { ...data.objects[index], ...update };
    const rowNumber = index + 2;
    const endColumn = columnName(TABLES[table].length);
    const range = encodeRange(`'${table}'!A${rowNumber}:${endColumn}${rowNumber}`);
    await nativeRequest("PUT", `https://sheets.googleapis.com/v4/spreadsheets/${encodeURIComponent(authority.workbook_id)}/values/${range}?valueInputOption=RAW`, JSON.stringify({ values: [rowValues(table, merged)] }));
    const verify = await tableValues(table);
    const found = verify.objects.find((row) => row[primary] === primaryValue);
    if (!found) throw new Error(`${table} update did not read back from Google.`);
    for (const [key, value] of Object.entries(update)) if (String(found[key] ?? "") !== String(value ?? "")) throw new Error(`${table} update readback did not match ${key}.`);
    return found;
  }

  function columnName(count) {
    let value = count, out = "";
    while (value > 0) { value -= 1; out = String.fromCharCode(65 + (value % 26)) + out; value = Math.floor(value / 26); }
    return out;
  }

  function parseJson(value, fallback = {}) { try { return value ? JSON.parse(value) : fallback; } catch (_) { return fallback; } }

  async function audit(eventType, targetUuid, payload) {
    return appendRow("Audit", { event_uuid: makeUuid(), event_type: eventType, target_uuid: targetUuid || "", actor: `mira-app:${typeof clientId === "function" ? clientId() : "device"}`, payload_json: JSON.stringify(payload || {}), created_at: now() });
  }

  async function assetReadback(assetUuid) {
    const [assets, identifiers, evidence] = await Promise.all([tableValues("Assets"), tableValues("Identifiers"), tableValues("Evidence")]);
    const row = assets.objects.find((item) => item.asset_uuid === assetUuid);
    if (!row) throw new Error("Item not found in MIRROR.");
    const linkedEvidence = evidence.objects.filter((item) => item.asset_uuid === assetUuid).map((item) => ({
      evidence_uuid: item.evidence_uuid, asset_uuid: item.asset_uuid, receipt_uuid: item.receipt_uuid || null,
      drive_file_id: item.drive_file_id, filename: item.filename, mime_type: item.mime_type, sha256: item.sha256,
      role: item.role, source: item.source, provenance_url: item.provenance_url, created_at: item.created_at
    }));
    return {
      uuid: row.asset_uuid, name: row.name, description: row.description, category_uuid: row.category_uuid || null,
      location_uuid: row.location_uuid || null, status: row.status || "active", metadata: parseJson(row.metadata_json, {}),
      created_at: row.created_at, updated_at: row.updated_at,
      identifiers: identifiers.objects.filter((item) => item.asset_uuid === assetUuid && !item.retired_at).map((item) => ({ identifier_uuid: item.identifier_uuid, namespace: item.namespace, value: item.value, source: item.source })),
      evidence: linkedEvidence,
      photo_evidence: linkedEvidence.filter((item) => ["primary", "gallery", "condition", "location_context"].includes(item.role))
    };
  }

  async function tree() {
    const [categories, locations] = await Promise.all([tableValues("Categories"), tableValues("Locations")]);
    return {
      categories: categories.objects.map((row) => ({ uuid: row.category_uuid, name: row.name, parent_uuid: row.parent_category_uuid || null })),
      locations: locations.objects.map((row) => ({ uuid: row.location_uuid, name: row.name, location_type: row.location_type || "storage", parent_uuid: row.parent_location_uuid || null }))
    };
  }

  async function listAssets(searchParams) {
    const data = await tableValues("Assets");
    const q = (searchParams.get("q") || "").trim().toLowerCase();
    const category = searchParams.get("category_uuid") || "";
    const location = searchParams.get("location_uuid") || "";
    const assets = data.objects.filter((row) => !row.status || row.status !== "removed").filter((row) => {
      if (q && !`${row.name} ${row.description} ${row.asset_uuid}`.toLowerCase().includes(q)) return false;
      if (category && row.category_uuid !== category) return false;
      if (location && row.location_uuid !== location) return false;
      return true;
    }).map((row) => ({ uuid: row.asset_uuid, name: row.name, description: row.description, category_uuid: row.category_uuid || null, location_uuid: row.location_uuid || null, status: row.status || "active", metadata: parseJson(row.metadata_json, {}) }));
    return { assets };
  }

  async function command(envelope) {
    const type = envelope.command_type, payload = envelope.payload || {}, timestamp = now();
    if (type === "inventory.category.create") {
      const categoryUuid = payload.category_uuid || makeUuid();
      const row = await appendRow("Categories", { category_uuid: categoryUuid, name: payload.name, parent_category_uuid: payload.parent_uuid || "", created_at: timestamp, updated_at: timestamp });
      await audit(type, categoryUuid, payload);
      return { readback_verified: true, category: { uuid: row.category_uuid, name: row.name, parent_uuid: row.parent_category_uuid || null } };
    }
    if (type === "inventory.location.create") {
      const locationUuid = payload.location_uuid || makeUuid();
      const row = await appendRow("Locations", { location_uuid: locationUuid, name: payload.name, location_type: payload.location_type || "storage", parent_location_uuid: payload.parent_uuid || "", created_at: timestamp, updated_at: timestamp });
      await audit(type, locationUuid, payload);
      return { readback_verified: true, location: { uuid: row.location_uuid, name: row.name, location_type: row.location_type, parent_uuid: row.parent_location_uuid || null } };
    }
    if (type === "inventory.asset.create") {
      const assetUuid = payload.asset_uuid || makeUuid();
      await appendRow("Assets", { asset_uuid: assetUuid, name: payload.name, description: payload.description || "", category_uuid: payload.category_uuid || "", location_uuid: payload.location_uuid || "", status: "active", metadata_json: JSON.stringify(payload.metadata || {}), created_at: timestamp, updated_at: timestamp });
      await audit(type, assetUuid, payload);
      return { readback_verified: true, asset: await assetReadback(assetUuid) };
    }
    if (type === "inventory.asset.update") {
      const existing = await assetReadback(payload.asset_uuid);
      await updateRow("Assets", payload.asset_uuid, { name: payload.name ?? existing.name, description: payload.description ?? existing.description, category_uuid: payload.category_uuid || "", location_uuid: payload.location_uuid || "", metadata_json: JSON.stringify(payload.metadata || existing.metadata || {}), updated_at: timestamp });
      await audit(type, payload.asset_uuid, payload);
      return { readback_verified: true, asset: await assetReadback(payload.asset_uuid) };
    }
    if (type === "inventory.asset.relocate") {
      await updateRow("Assets", payload.asset_uuid, { location_uuid: payload.location_uuid || "", updated_at: timestamp });
      await audit(type, payload.asset_uuid, payload);
      return { readback_verified: true, asset: await assetReadback(payload.asset_uuid) };
    }
    if (type === "inventory.identifier.assign") {
      const duplicates = (await tableValues("Identifiers")).objects.filter((row) => !row.retired_at && row.namespace === payload.namespace && row.value === payload.value);
      if (duplicates.some((row) => row.asset_uuid !== payload.asset_uuid)) throw new Error("That code is already attached to another item. MIRA stopped instead of duplicating it.");
      if (!duplicates.some((row) => row.asset_uuid === payload.asset_uuid)) await appendRow("Identifiers", { identifier_uuid: makeUuid(), asset_uuid: payload.asset_uuid, namespace: payload.namespace || "preprinted", value: payload.value, source: "mira_app", provenance_url: "", created_at: timestamp, retired_at: "" });
      await audit(type, payload.asset_uuid, payload);
      return { readback_verified: true, asset: await assetReadback(payload.asset_uuid) };
    }
    if (type === "capture.barcode_qr_scan") {
      const value = String(payload.raw_value || "").trim();
      const match = (await tableValues("Identifiers")).objects.find((row) => !row.retired_at && row.value === value);
      return { readback_verified: true, scan: payload, matched: Boolean(match), asset: match ? await assetReadback(match.asset_uuid) : null, next_action: match ? "open_asset" : "classify_or_assign_identifier" };
    }
    throw new Error(`This cloud MIRA build does not support ${type} yet.`);
  }

  async function settingsGet() {
    const rows = (await tableValues("Settings")).objects;
    const settings = {};
    rows.forEach((row) => { settings[row.setting_key] = parseJson(row.value_json, row.value_json); });
    return { settings };
  }

  async function settingsPatch(payload) {
    for (const [key, value] of Object.entries(payload.settings || {})) {
      const rows = await tableValues("Settings");
      const existing = rows.objects.find((row) => row.setting_key === key);
      const update = { setting_key: key, value_json: JSON.stringify(value), updated_at: now(), updated_by: `mira-app:${typeof clientId === "function" ? clientId() : "device"}` };
      if (existing) await updateRow("Settings", key, update); else await appendRow("Settings", update);
    }
    return settingsGet();
  }

  async function sha256(file) {
    const bytes = await file.arrayBuffer();
    const digest = await crypto.subtle.digest("SHA-256", bytes);
    return [...new Uint8Array(digest)].map((value) => value.toString(16).padStart(2, "0")).join("");
  }

  async function fileBase64(file) {
    const bytes = new Uint8Array(await file.arrayBuffer());
    let binary = "";
    const chunk = 0x8000;
    for (let i = 0; i < bytes.length; i += chunk) binary += String.fromCharCode(...bytes.subarray(i, i + chunk));
    return btoa(binary);
  }

  async function uploadDriveEvidence(file, { assetUuid = "", receiptUuid = "", role = "attachment" } = {}) {
    await bootstrap();
    const evidenceUuid = makeUuid(), digest = await sha256(file);
    const metadata = {
      name: `${evidenceUuid}-${file.name || "evidence"}`,
      mimeType: file.type || "application/octet-stream",
      parents: authority.folder_id ? [authority.folder_id] : undefined,
      appProperties: { mira_mirror: "evidence", evidence_uuid: evidenceUuid, asset_uuid: assetUuid || "", receipt_uuid: receiptUuid || "", sha256: digest, role }
    };
    if (!metadata.parents) delete metadata.parents;
    const created = (await nativeRequest("POST", "https://www.googleapis.com/drive/v3/files?fields=id,name,size,mimeType,webViewLink,thumbnailLink,appProperties", JSON.stringify(metadata))).json;
    await nativeRequestBase64("PATCH", `https://www.googleapis.com/upload/drive/v3/files/${encodeURIComponent(created.id)}?uploadType=media`, await fileBase64(file), file.type || "application/octet-stream");
    const verify = (await nativeRequest("GET", `https://www.googleapis.com/drive/v3/files/${encodeURIComponent(created.id)}?fields=id,name,size,mimeType,webViewLink,thumbnailLink,appProperties`)).json;
    if (String(verify.size || "0") !== String(file.size) || verify.appProperties?.sha256 !== digest || verify.appProperties?.evidence_uuid !== evidenceUuid) throw new Error("Google stored the evidence file, but MIRROR readback did not match. MIRA did not report success.");
    const row = await appendRow("Evidence", { evidence_uuid: evidenceUuid, asset_uuid: assetUuid, receipt_uuid: receiptUuid, drive_file_id: created.id, filename: file.name || "evidence", mime_type: file.type || "application/octet-stream", sha256: digest, role, source: "mira_app", provenance_url: verify.webViewLink || "", created_at: now() });
    await audit("evidence.upload", assetUuid || receiptUuid, { evidence_uuid: evidenceUuid, drive_file_id: created.id, sha256: digest, role });
    return { row, drive: verify };
  }

  async function uploadAssetEvidence(form) {
    const assetUuid = String(form.get("asset_uuid") || "");
    const file = form.get("file");
    const role = String(form.get("media_role") || form.get("role") || "attachment");
    if (!assetUuid || !(file instanceof File)) throw new Error("Select an item and choose a file first.");
    await assetReadback(assetUuid);
    const uploaded = await uploadDriveEvidence(file, { assetUuid, role });
    const asset = await assetReadback(assetUuid);
    if (!asset.evidence.some((row) => row.evidence_uuid === uploaded.row.evidence_uuid)) throw new Error("The file reached Google Drive but was not linked back to the item in MIRROR.");
    return { readback_verified: true, evidence_uuid: uploaded.row.evidence_uuid, asset_uuid: assetUuid, filename: uploaded.row.filename, mime_type: uploaded.row.mime_type, content_hash: uploaded.row.sha256, role: uploaded.row.role, replication: { provider: "google_drive", provider_object_id: uploaded.row.drive_file_id, provider_locator: `google-drive:${uploaded.row.drive_file_id}`, web_url: uploaded.drive.webViewLink || null, readback_verified: true } };
  }

  async function receiptReadback(receiptUuid) {
    const [receipts, lines] = await Promise.all([tableValues("Receipts"), tableValues("ReceiptLines")]);
    const row = receipts.objects.find((item) => item.receipt_uuid === receiptUuid);
    if (!row) throw new Error("Receipt not found in MIRROR.");
    return { receipt_uuid: row.receipt_uuid, merchant_uuid: row.merchant_uuid || null, merchant_display: row.merchant_display || "", purchase_at: row.purchase_at || null, currency: row.currency || "USD", subtotal: row.subtotal || null, tax: row.tax || null, total: row.total || null, evidence_drive_file_id: row.evidence_drive_file_id, raw_extract: parseJson(row.raw_extract_json, {}), status: row.status || "captured", created_at: row.created_at, updated_at: row.updated_at, lines: lines.objects.filter((item) => item.receipt_uuid === receiptUuid) };
  }

  async function uploadReceipt(form) {
    const file = form.get("file"); if (!(file instanceof File)) throw new Error("Take or choose a receipt photo first.");
    const receiptUuid = makeUuid(), uploaded = await uploadDriveEvidence(file, { receiptUuid, role: "receipt" });
    await appendRow("Receipts", { receipt_uuid: receiptUuid, merchant_uuid: "", merchant_display: "", purchase_at: "", currency: "USD", subtotal: "", tax: "", total: "", evidence_drive_file_id: uploaded.row.drive_file_id, raw_extract_json: "{}", status: "captured", created_at: now(), updated_at: now() });
    await audit("receipt.capture", receiptUuid, { evidence_uuid: uploaded.row.evidence_uuid, drive_file_id: uploaded.row.drive_file_id });
    const receipt = await receiptReadback(receiptUuid);
    if (receipt.evidence_drive_file_id !== uploaded.row.drive_file_id) throw new Error("Receipt evidence reached Drive but the MIRROR receipt relationship did not read back.");
    return { readback_verified: true, receipt };
  }

  async function evidenceLink(evidenceUuid) {
    const row = (await tableValues("Evidence")).objects.find((item) => item.evidence_uuid === evidenceUuid);
    if (!row) throw new Error("Evidence not found in MIRROR.");
    const drive = (await nativeRequest("GET", `https://www.googleapis.com/drive/v3/files/${encodeURIComponent(row.drive_file_id)}?fields=id,name,mimeType,webViewLink,thumbnailLink,size,appProperties`)).json;
    return { url: drive.thumbnailLink || drive.webViewLink, web_url: drive.webViewLink || null, evidence_uuid: evidenceUuid };
  }

  async function route(path, options = {}) {
    await bootstrap();
    const method = String(options.method || "GET").toUpperCase();
    const [pathname, queryString = ""] = String(path).split("?", 2);
    const params = new URLSearchParams(queryString);
    if (pathname === "/v1/health") return { status: "ready", product_version: CLIENT_VERSION || "0.2.0", api_contract: API_CONTRACT || "1.1", authority: "google_workspace", mirror_authority_uuid: authority.authority_uuid };
    if (pathname === "/v1/compatibility") return { mutation_allowed: true, reason: "MIRA app and Google MIRROR authority are compatible.", minimum_client_version: CLIENT_VERSION || "0.2.0", api_contract: API_CONTRACT || "1.1" };
    if (pathname === "/v1/inventory/tree") return tree();
    if (pathname === "/v1/assets" && method === "GET") return listAssets(params);
    if (pathname.startsWith("/v1/assets/") && method === "GET") return assetReadback(decodeURIComponent(pathname.slice("/v1/assets/".length)));
    if (pathname === "/v1/commands" && method === "POST") return command(JSON.parse(options.body || "{}"));
    if (pathname === "/v1/settings" && method === "GET") return settingsGet();
    if (pathname === "/v1/settings" && method === "PATCH") return settingsPatch(JSON.parse(options.body || "{}"));
    if (pathname === "/v1/evidence" && method === "POST") return uploadAssetEvidence(options.body);
    if (pathname === "/v1/receipts/upload" && method === "POST") return uploadReceipt(options.body);
    if (pathname.startsWith("/v1/receipts/") && method === "GET" && !pathname.endsWith("/retailer-search-plan")) return { receipt: await receiptReadback(decodeURIComponent(pathname.slice("/v1/receipts/".length))) };
    if (pathname === "/v1/access-link" && method === "GET") {
      const resource = params.get("resource") || "";
      if (resource.startsWith("evidence:")) return evidenceLink(resource.slice("evidence:".length));
      throw new Error("Cloud label generation is not available in this build yet.");
    }
    throw new Error("This action is not yet available in Google cloud mode. MIRA did not change your data.");
  }

  function pseudoUrl(path) { return `mira-authority://${String(path).replace(/^\//, "")}`; }
  function pseudoPath(url) { const value = String(url); return "/" + value.slice("mira-authority://".length); }
  function response(payload, status = 200) { return new Response(JSON.stringify(payload), { status, headers: { "Content-Type": "application/json" } }); }

  const originalApiUrl = typeof apiUrl === "function" ? apiUrl : null;
  const originalAuthorizedFetch = typeof authorizedFetch === "function" ? authorizedFetch : null;
  const originalPreflight = typeof preflight === "function" ? preflight : null;

  if (originalApiUrl) apiUrl = function authorityAwareApiUrl(path) {
    const base = typeof apiBase === "function" ? apiBase() : "";
    if (!base && cloudMode()) return pseudoUrl(path);
    return originalApiUrl(path);
  };

  if (originalAuthorizedFetch) authorizedFetch = async function authorityAwareFetch(url, options = {}) {
    if (String(url).startsWith("mira-authority://")) {
      try { return response(await route(pseudoPath(url), options), 200); }
      catch (error) { return response({ detail: error?.message || String(error) }, 400); }
    }
    return originalAuthorizedFetch(url, options);
  };

  if (originalPreflight) preflight = async function authorityAwarePreflight() {
    const base = typeof apiBase === "function" ? apiBase() : "";
    if (!base && cloudMode()) {
      if (!googleConnected()) { setMutationAllowed(false, "Connect Google before saving to MIRROR."); throw new Error("Connect Google before saving to MIRROR."); }
      await bootstrap();
      setMutationAllowed(true);
      setStatus("MIRROR is connected through Google.");
      return { mutation_allowed: true, reason: "Google MIRROR is connected." };
    }
    return originalPreflight();
  };

  globalThis.MiraGoogleAuthority = { bootstrap, ready, available, route, tableValues, assetReadback, uploadDriveEvidence, authority: () => authority };
})();
