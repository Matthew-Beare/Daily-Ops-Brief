"use strict";

(() => {
  const MODE_KEY = "mira.deployment.mode.v1";
  const DB_NAME = "mira-local-mirror-v1";
  const DB_VERSION = 1;
  const BASE = "mira-local://";
  let dbPromise = null;

  function manualMode() { return localStorage.getItem(MODE_KEY) === "manual"; }
  function now() { return new Date().toISOString(); }
  function uuid() { return globalThis.crypto?.randomUUID ? crypto.randomUUID() : `${Date.now()}-${Math.random()}`; }

  function openDb() {
    if (dbPromise) return dbPromise;
    dbPromise = new Promise((resolve, reject) => {
      const request = indexedDB.open(DB_NAME, DB_VERSION);
      request.onerror = () => reject(request.error || new Error("Could not open local MIRROR storage."));
      request.onupgradeneeded = () => {
        const db = request.result;
        const stores = [
          ["settings", "setting_key"], ["assets", "asset_uuid"], ["identifiers", "identifier_uuid"], ["categories", "category_uuid"], ["locations", "location_uuid"],
          ["evidence", "evidence_uuid"], ["receipts", "receipt_uuid"], ["receiptLines", "receipt_line_uuid"], ["reconciliationWork", "work_uuid"],
          ["corrections", "correction_uuid"], ["recognitionProfiles", "profile_uuid"]
        ];
        stores.forEach(([name, keyPath]) => { if (!db.objectStoreNames.contains(name)) db.createObjectStore(name, { keyPath }); });
      };
      request.onsuccess = () => resolve(request.result);
    });
    return dbPromise;
  }

  async function tx(storeNames, mode, action) {
    const db = await openDb();
    return new Promise((resolve, reject) => {
      const transaction = db.transaction(storeNames, mode);
      transaction.onerror = () => reject(transaction.error || new Error("Local MIRROR transaction failed."));
      let value;
      try { value = action(transaction); } catch (error) { reject(error); return; }
      transaction.oncomplete = () => resolve(value);
    });
  }

  async function getAll(store) {
    const db = await openDb();
    return new Promise((resolve, reject) => {
      const transaction = db.transaction([store], "readonly");
      const request = transaction.objectStore(store).getAll();
      request.onsuccess = () => resolve(request.result || []);
      request.onerror = () => reject(request.error || new Error(`Could not read ${store}.`));
    });
  }

  async function get(store, key) {
    const db = await openDb();
    return new Promise((resolve, reject) => {
      const transaction = db.transaction([store], "readonly");
      const request = transaction.objectStore(store).get(key);
      request.onsuccess = () => resolve(request.result || null);
      request.onerror = () => reject(request.error || new Error(`Could not read ${store}.`));
    });
  }

  async function put(store, value) {
    await tx([store], "readwrite", (transaction) => transaction.objectStore(store).put(value));
    return value;
  }

  async function remove(store, key) {
    await tx([store], "readwrite", (transaction) => transaction.objectStore(store).delete(key));
  }

  async function seedDefaults() {
    const defaults = {
      "onboarding.completed": true,
      "deployment.mode": "manual",
      "daily_cleanup.enabled": true,
      "daily_cleanup.times": ["00:01"],
      "daily_cleanup.timezone_mode": "local",
      "ai.mode": "manual_only",
      "ai.monthly_budget": null,
      "ai.budget_hard_stop": false
    };
    for (const [key, value] of Object.entries(defaults)) {
      if (!(await get("settings", key))) await put("settings", { setting_key: key, value, updated_at: now() });
    }
  }

  async function settingsGet() {
    await seedDefaults();
    const rows = await getAll("settings");
    return { settings: Object.fromEntries(rows.map((row) => [row.setting_key, row.value])), revision: String(rows.length), authority: "Local MIRROR on this device" };
  }

  async function settingsPatch(payload) {
    const updates = payload?.settings || payload || {};
    for (const [key, value] of Object.entries(updates)) await put("settings", { setting_key: key, value, updated_at: now() });
    return { readback_verified: true, ...(await settingsGet()) };
  }

  async function assetReadback(assetUuid) {
    const asset = await get("assets", assetUuid);
    if (!asset || asset.status === "removed") throw new Error("Item not found in local MIRROR.");
    const [identifiers, evidence] = await Promise.all([getAll("identifiers"), getAll("evidence")]);
    const attached = evidence.filter((row) => row.asset_uuid === assetUuid).map(({ blob, ...row }) => row);
    return {
      uuid: asset.asset_uuid,
      name: asset.name,
      description: asset.description || "",
      category_uuid: asset.category_uuid || null,
      location_uuid: asset.location_uuid || null,
      status: asset.status || "active",
      metadata: asset.metadata || {},
      created_at: asset.created_at,
      updated_at: asset.updated_at,
      identifiers: identifiers.filter((row) => row.asset_uuid === assetUuid && !row.retired_at),
      evidence: attached,
      photo_evidence: attached.filter((row) => String(row.mime_type || "").startsWith("image/")).map((row) => ({ ...row, media_role: row.role, content_hash: row.sha256, captured_at: row.created_at }))
    };
  }

  async function tree() {
    return { categories: await getAll("categories"), locations: await getAll("locations") };
  }

  async function listAssets(params) {
    let rows = (await getAll("assets")).filter((row) => (row.status || "active") === (params.get("status") || "active"));
    const q = String(params.get("q") || "").toLowerCase();
    if (q) rows = rows.filter((row) => `${row.name} ${row.description} ${row.asset_uuid}`.toLowerCase().includes(q));
    if (params.get("category_uuid")) rows = rows.filter((row) => row.category_uuid === params.get("category_uuid"));
    if (params.get("location_uuid")) rows = rows.filter((row) => row.location_uuid === params.get("location_uuid"));
    rows.sort((a, b) => String(a.name).localeCompare(String(b.name)));
    return { assets: await Promise.all(rows.slice(0, Number(params.get("limit") || 250)).map((row) => assetReadback(row.asset_uuid))) };
  }

  async function command(payload) {
    const type = payload.command_type;
    const body = payload.payload || {};
    const timestamp = now();
    if (type === "inventory.category.create") {
      const category_uuid = body.category_uuid || uuid();
      await put("categories", { category_uuid, uuid: category_uuid, name: body.name, parent_category_uuid: body.parent_category_uuid || body.parent_uuid || "", parent_uuid: body.parent_category_uuid || body.parent_uuid || null, created_at: timestamp, updated_at: timestamp });
      return { readback_verified: true, category: { uuid: category_uuid, name: body.name, parent_uuid: body.parent_category_uuid || body.parent_uuid || null } };
    }
    if (type === "inventory.location.create") {
      const location_uuid = body.location_uuid || uuid();
      await put("locations", { location_uuid, uuid: location_uuid, name: body.name, location_type: body.location_type || "storage", parent_location_uuid: body.parent_location_uuid || body.parent_uuid || "", parent_uuid: body.parent_location_uuid || body.parent_uuid || null, created_at: timestamp, updated_at: timestamp });
      return { readback_verified: true, location: { uuid: location_uuid, name: body.name, location_type: body.location_type || "storage", parent_uuid: body.parent_location_uuid || body.parent_uuid || null } };
    }
    if (type === "inventory.asset.create") {
      const asset_uuid = body.asset_uuid || uuid();
      await put("assets", { asset_uuid, name: body.name || "Unnamed item", description: body.description || "", category_uuid: body.category_uuid || "", location_uuid: body.location_uuid || "", status: "active", metadata: body.metadata || {}, created_at: timestamp, updated_at: timestamp });
      return { readback_verified: true, asset: await assetReadback(asset_uuid) };
    }
    if (type === "inventory.asset.update" || type === "inventory.asset.relocate") {
      const existing = await get("assets", body.asset_uuid);
      if (!existing) throw new Error("Item not found in local MIRROR.");
      const updated = { ...existing, updated_at: timestamp };
      if (type === "inventory.asset.update") {
        if (body.name !== undefined) updated.name = body.name;
        if (body.description !== undefined) updated.description = body.description;
        if (body.category_uuid !== undefined) updated.category_uuid = body.category_uuid || "";
        if (body.location_uuid !== undefined) updated.location_uuid = body.location_uuid || "";
        if (body.metadata !== undefined) updated.metadata = body.metadata || {};
      } else updated.location_uuid = body.location_uuid || "";
      await put("assets", updated);
      return { readback_verified: true, asset: await assetReadback(body.asset_uuid) };
    }
    if (type === "inventory.identifier.assign") {
      const rows = await getAll("identifiers");
      const conflict = rows.find((row) => !row.retired_at && row.namespace === body.namespace && row.value === body.value && row.asset_uuid !== body.asset_uuid);
      if (conflict) throw new Error("That code is already attached to another item.");
      if (!rows.some((row) => !row.retired_at && row.namespace === body.namespace && row.value === body.value && row.asset_uuid === body.asset_uuid)) {
        await put("identifiers", { identifier_uuid: uuid(), asset_uuid: body.asset_uuid, namespace: body.namespace || "preprinted", value: body.value, source: "mira_app", created_at: timestamp, retired_at: "" });
      }
      return { readback_verified: true, asset: await assetReadback(body.asset_uuid) };
    }
    if (type === "capture.barcode_qr_scan") {
      const rows = await getAll("identifiers");
      const match = rows.find((row) => !row.retired_at && row.value === String(body.raw_value || "").trim());
      return { readback_verified: true, scan: body, matched: Boolean(match), asset: match ? await assetReadback(match.asset_uuid) : null, next_action: match ? "open_asset" : "classify_or_assign_identifier" };
    }
    throw new Error(`Manual MIRROR does not support ${type} yet.`);
  }

  async function sha256(file) {
    const digest = await crypto.subtle.digest("SHA-256", await file.arrayBuffer());
    return [...new Uint8Array(digest)].map((value) => value.toString(16).padStart(2, "0")).join("");
  }

  async function evidenceUpload(form) {
    const assetUuid = String(form.get("asset_uuid") || "");
    const file = form.get("file");
    if (!assetUuid || !(file instanceof File)) throw new Error("Select an item and choose a file first.");
    await assetReadback(assetUuid);
    const evidence_uuid = uuid();
    const digest = await sha256(file);
    const row = { evidence_uuid, asset_uuid: assetUuid, receipt_uuid: "", filename: file.name || "evidence", mime_type: file.type || "application/octet-stream", sha256: digest, role: String(form.get("media_role") || form.get("role") || "attachment"), source: "mira_app", created_at: now(), blob: file };
    await put("evidence", row);
    const readback = await get("evidence", evidence_uuid);
    if (!readback || readback.sha256 !== digest) throw new Error("Local MIRROR evidence readback failed.");
    return { readback_verified: true, evidence_uuid, asset_uuid: assetUuid, filename: row.filename, mime_type: row.mime_type, content_hash: digest, role: row.role, replication: { provider: "indexeddb", provider_object_id: evidence_uuid, readback_verified: true } };
  }

  async function receiptUpload(form) {
    const file = form.get("file");
    if (!(file instanceof File)) throw new Error("Take or choose a receipt first.");
    const receipt_uuid = uuid(), evidence_uuid = uuid(), digest = await sha256(file), timestamp = now();
    await put("evidence", { evidence_uuid, asset_uuid: "", receipt_uuid, filename: file.name || "receipt", mime_type: file.type || "application/octet-stream", sha256: digest, role: "receipt", source: "mira_app", created_at: timestamp, blob: file });
    await put("receipts", { receipt_uuid, merchant_uuid: "", merchant_display: "", purchase_at: "", currency: "USD", subtotal: "", tax: "", total: "", evidence_uuid, raw_extract: {}, status: "captured", created_at: timestamp, updated_at: timestamp });
    await put("reconciliationWork", { work_uuid: `receipt:${receipt_uuid}:reconcile`, feature_namespace: "receipts", source_type: "receipt", source_uuid: receipt_uuid, work_type: "receipt.reconcile", processing_mode: "manual_only", status: "needs_review", priority: 20, freshness_minutes: 1440, capabilities: ["text_reasoning"], allowed_mutations: ["receipt_fields","receipt_lines","merchant","merchant_location","inventory_suggestions"], confidence_threshold: 0.90, idempotency_key: `receipt:${receipt_uuid}:reconcile`, attempts: 0, created_at: timestamp, updated_at: timestamp });
    return { readback_verified: true, receipt: await receiptReadback(receipt_uuid) };
  }

  async function receiptReadback(receiptUuid) {
    const receipt = await get("receipts", receiptUuid);
    if (!receipt) throw new Error("Receipt not found in local MIRROR.");
    const lines = (await getAll("receiptLines")).filter((row) => row.receipt_uuid === receiptUuid);
    return { ...receipt, lines };
  }

  async function accessLink(resource) {
    if (resource.startsWith("evidence:")) {
      const id = resource.slice("evidence:".length);
      const row = await get("evidence", id);
      if (!row?.blob) throw new Error("Evidence file not found in local MIRROR.");
      return { url: URL.createObjectURL(row.blob), evidence_uuid: id };
    }
    throw new Error("Local label preview is not available yet.");
  }

  async function reconciliationSummary() {
    const rows = await getAll("reconciliationWork");
    const counts = {};
    rows.forEach((row) => { counts[row.status] = (counts[row.status] || 0) + 1; });
    return { waiting: (counts.queued || 0) + (counts.processing || 0), needs_review: (counts.needs_review || 0) + (counts.quarantined || 0), counts, api_cost: { today: 0, month: 0, currency: "USD", metered_processors_enabled: false }, default_daily_cleanup_time: "00:01", readback_verified: true };
  }

  async function route(path, options = {}) {
    await seedDefaults();
    const method = String(options.method || "GET").toUpperCase();
    const [pathname, query = ""] = String(path).split("?", 2);
    const params = new URLSearchParams(query);
    if (pathname === "/v1/health") return { status: "ready", authority: "local_manual", product_version: typeof CLIENT_VERSION !== "undefined" ? CLIENT_VERSION : "0.2.0", api_contract: typeof API_CONTRACT !== "undefined" ? API_CONTRACT : "1.1" };
    if (pathname === "/v1/compatibility") return { mutation_allowed: true, minimum_client_version: typeof CLIENT_VERSION !== "undefined" ? CLIENT_VERSION : "0.2.0", reason: "Local MIRROR is compatible." };
    if (pathname === "/v1/inventory/tree") return tree();
    if (pathname === "/v1/assets" && method === "GET") return listAssets(params);
    if (pathname.startsWith("/v1/assets/") && method === "GET") return assetReadback(decodeURIComponent(pathname.slice("/v1/assets/".length)));
    if (pathname === "/v1/commands" && method === "POST") return command(JSON.parse(options.body || "{}"));
    if (pathname === "/v1/settings" && method === "GET") return settingsGet();
    if (pathname === "/v1/settings" && method === "PATCH") return settingsPatch(JSON.parse(options.body || "{}"));
    if (pathname === "/v1/evidence" && method === "POST") return evidenceUpload(options.body);
    if (pathname === "/v1/receipts/upload" && method === "POST") return receiptUpload(options.body);
    if (pathname.startsWith("/v1/receipts/") && method === "GET") return { receipt: await receiptReadback(decodeURIComponent(pathname.slice("/v1/receipts/".length))) };
    if (pathname === "/v1/access-link" && method === "GET") return accessLink(params.get("resource") || "");
    if (pathname === "/v1/reconciliation/summary" && method === "GET") return reconciliationSummary();
    if (pathname === "/v1/reconciliation/work" && method === "GET") {
      let rows = await getAll("reconciliationWork");
      if (params.get("status")) rows = rows.filter((row) => row.status === params.get("status"));
      rows.sort((a, b) => Number(b.priority || 0) - Number(a.priority || 0) || String(a.created_at).localeCompare(String(b.created_at)));
      return { items: rows, count: rows.length };
    }
    throw new Error("This action needs a connected cloud or self-hosted MIRROR. Your local data was not changed.");
  }

  function response(payload, status = 200) { return new Response(JSON.stringify(payload), { status, headers: { "Content-Type": "application/json" } }); }
  function pseudoPath(url) { return "/" + String(url).slice(BASE.length); }

  const originalApiBase = typeof apiBase === "function" ? apiBase : null;
  const originalApiUrl = typeof apiUrl === "function" ? apiUrl : null;
  const originalAuthorizedFetch = typeof authorizedFetch === "function" ? authorizedFetch : null;
  const originalPreflight = typeof preflight === "function" ? preflight : null;

  if (originalApiBase) apiBase = function localAwareBase() { return manualMode() ? BASE : originalApiBase(); };
  if (originalApiUrl) apiUrl = function localAwareUrl(path) { return manualMode() ? `${BASE}${String(path || "").replace(/^\//, "")}` : originalApiUrl(path); };
  if (originalAuthorizedFetch) authorizedFetch = async function localAwareFetch(url, options = {}) {
    if (manualMode() && String(url).startsWith(BASE)) {
      try { return response(await route(pseudoPath(url), options)); }
      catch (error) { return response({ detail: error?.message || String(error) }, 400); }
    }
    return originalAuthorizedFetch(url, options);
  };
  if (originalPreflight) preflight = async function localAwarePreflight() {
    if (!manualMode()) return originalPreflight();
    await seedDefaults();
    if (typeof setMutationAllowed === "function") setMutationAllowed(true);
    if (typeof setStatus === "function") setStatus("Local MIRROR is ready. AI cleanup is not connected.");
    return { mutation_allowed: true, reason: "Local manual MIRROR is ready." };
  };

  globalThis.MiraLocalAuthority = { ready: async () => { if (!manualMode()) return false; await seedDefaults(); return true; }, route, assetReadback, exportAll: async () => ({ settings: await getAll("settings"), assets: await getAll("assets"), identifiers: await getAll("identifiers"), categories: await getAll("categories"), locations: await getAll("locations"), receipts: await getAll("receipts"), receipt_lines: await getAll("receiptLines"), reconciliation_work: await getAll("reconciliationWork"), corrections: await getAll("corrections"), recognition_profiles: await getAll("recognitionProfiles") }) };
})();
