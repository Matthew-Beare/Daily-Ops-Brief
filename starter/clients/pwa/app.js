"use strict";

const CLIENT_VERSION = "0.2.0";
const API_CONTRACT = "1.1";
const QUEUE_KEY = "mirror.capture.pending.v2";
const API_BASE_STORAGE_KEY = "mirror.capture.api-base.v2";
const CLIENT_KEY = "mirror.capture.client-id.v1";
const MAX_PHOTO_BYTES = 15 * 1024 * 1024;

const state = { tree: { categories: [], locations: [] }, selectedAsset: null, lastScan: null, mutationAllowed: false };
const byId = (id) => document.getElementById(id);
const statusEl = byId("status");
const queueCountEl = byId("queueCount");
const videoEl = byId("camera");
let stream = null;
let detector = null;
let scanLoopActive = false;
let lastCameraValue = "";
let lastCameraAt = 0;
let previewUrl = null;

function setStatus(message) { if (statusEl) statusEl.textContent = String(message || ""); }
function uuid() { if (globalThis.crypto?.randomUUID) return crypto.randomUUID(); throw new Error("This client requires crypto.randomUUID in a secure context."); }
function clientId() { let value = localStorage.getItem(CLIENT_KEY); if (!value) { value = uuid(); localStorage.setItem(CLIENT_KEY, value); } return value; }
function pending() { try { const rows = JSON.parse(localStorage.getItem(QUEUE_KEY) || "[]"); return Array.isArray(rows) ? rows : []; } catch { return []; } }
function savePending(rows) { localStorage.setItem(QUEUE_KEY, JSON.stringify(rows)); if (queueCountEl) queueCountEl.textContent = `${rows.length} capture${rows.length === 1 ? "" : "s"} pending sync`; }
function apiBase() {
  const configured = byId("apiBase")?.value.trim().replace(/\/+$/, "");
  if (configured) return configured;
  if (["http:", "https:"].includes(location.protocol) && location.hostname !== "appassets.androidplatform.net") return location.origin;
  return "";
}
function token() { return byId("token")?.value.trim() || ""; }
function apiUrl(path) { const base = apiBase(); if (!base) throw new Error("No API base URL configured."); return `${base}${path}`; }

async function authorizedFetch(url, options = {}) {
  const headers = new Headers(options.headers || {});
  headers.set("X-Mirror-Api-Version", API_CONTRACT);
  headers.set("X-Mirror-Client", `mira-ui/${CLIENT_VERSION}`);
  if (token()) headers.set("Authorization", `Bearer ${token()}`);
  return fetch(url, { ...options, headers });
}

async function apiJson(path, options = {}) {
  const response = await authorizedFetch(apiUrl(path), options);
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(payload.detail || `API returned HTTP ${response.status}.`);
  return payload;
}

function setMutationAllowed(allowed, reason = "") {
  state.mutationAllowed = Boolean(allowed);
  document.querySelectorAll("[data-mutation]").forEach((el) => { el.disabled = !state.mutationAllowed; });
  if (!allowed && reason) setStatus(reason);
}

async function preflight() {
  const result = await apiJson(`/v1/compatibility?client_api=${encodeURIComponent(API_CONTRACT)}&client_version=${encodeURIComponent(CLIENT_VERSION)}`);
  setMutationAllowed(Boolean(result.mutation_allowed), result.reason);
  const health = await apiJson("/v1/health");
  setStatus(`mirror ${health.product_version} | API ${health.api_contract} | ${result.reason}`);
  return result;
}

function commandEnvelope(commandType, payload) {
  const commandId = uuid();
  return {
    command_id: commandId,
    command_type: commandType,
    actor_id: `client:${clientId()}`,
    submitted_at: new Date().toISOString(),
    idempotency_key: `${commandType}:${commandId}`,
    payload,
  };
}

async function submitCommand(command) {
  if (!state.mutationAllowed && command.command_type !== "capture.barcode_qr_scan") await preflight();
  const response = await authorizedFetch(apiUrl("/v1/commands"), { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(command) });
  const result = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(result.detail || `API returned HTTP ${response.status}.`);
  if (result?.readback_verified === false) throw new Error("Server did not verify canonical readback.");
  return result;
}

async function mutate(commandType, payload) { return submitCommand(commandEnvelope(commandType, payload)); }

function hierarchyRows(rows) {
  const children = new Map();
  rows.forEach((row) => { const key = row.parent_uuid || ""; if (!children.has(key)) children.set(key, []); children.get(key).push(row); });
  for (const list of children.values()) list.sort((a, b) => a.name.localeCompare(b.name));
  const out = [];
  const walk = (parent, depth) => (children.get(parent) || []).forEach((row) => { out.push({ ...row, depth }); walk(row.uuid, depth + 1); });
  walk("", 0);
  return out;
}

function populateSelect(id, rows, emptyLabel) {
  const select = byId(id); if (!select) return;
  const current = select.value;
  select.replaceChildren(new Option(emptyLabel, ""));
  hierarchyRows(rows).forEach((row) => select.add(new Option(`${"  ".repeat(row.depth)}${row.name}`, row.uuid)));
  if ([...select.options].some((opt) => opt.value === current)) select.value = current;
}

async function loadTree() {
  state.tree = await apiJson("/v1/inventory/tree");
  ["filterCategory", "newAssetCategory", "editAssetCategory", "categoryParent"].forEach((id) => populateSelect(id, state.tree.categories, id === "filterCategory" ? "All categories" : id === "categoryParent" ? "Top level" : "No category"));
  ["filterLocation", "newAssetLocation", "editAssetLocation", "locationParent"].forEach((id) => populateSelect(id, state.tree.locations, id === "filterLocation" ? "All locations" : id === "locationParent" ? "Top level" : "No location"));
  byId("treeResult").textContent = JSON.stringify({ categories: hierarchyRows(state.tree.categories), locations: hierarchyRows(state.tree.locations) }, null, 2);
}

function categoryName(uuidValue) { return state.tree.categories.find((row) => row.uuid === uuidValue)?.name || "Uncategorized"; }
function locationName(uuidValue) { return state.tree.locations.find((row) => row.uuid === uuidValue)?.name || "Unlocated"; }

async function loadAssets() {
  const params = new URLSearchParams();
  if (byId("assetSearch").value.trim()) params.set("q", byId("assetSearch").value.trim());
  if (byId("filterCategory").value) params.set("category_uuid", byId("filterCategory").value);
  if (byId("filterLocation").value) params.set("location_uuid", byId("filterLocation").value);
  const result = await apiJson(`/v1/assets?${params}`);
  const list = byId("assetList"); list.replaceChildren();
  result.assets.forEach((asset) => {
    const button = document.createElement("button"); button.className = "asset-row";
    const title = document.createElement("strong"); title.textContent = asset.name;
    const detail = document.createElement("small"); detail.textContent = `${categoryName(asset.category_uuid)} | ${locationName(asset.location_uuid)} | ${asset.uuid}`;
    button.append(title, detail); button.addEventListener("click", () => selectAsset(asset.uuid).catch(showError)); list.appendChild(button);
  });
  if (!result.assets.length) list.textContent = "No matching assets.";
}

function renderSelected(asset) {
  state.selectedAsset = asset;
  byId("editAssetName").value = asset.name || "";
  byId("editAssetDescription").value = asset.description || "";
  byId("editAssetCategory").value = asset.category_uuid || "";
  byId("editAssetLocation").value = asset.location_uuid || "";
  byId("editAssetMetadata").value = JSON.stringify(asset.metadata || {}, null, 2);
  byId("assetResult").textContent = JSON.stringify(asset, null, 2);
  const identifiers = byId("assetIdentifiers"); identifiers.replaceChildren();
  (asset.identifiers || []).forEach((row) => { const span = document.createElement("span"); span.className = "pill"; span.textContent = `${row.namespace}: ${row.value}`; identifiers.appendChild(span); });
  const evidence = byId("evidenceList"); evidence.replaceChildren();
  (asset.evidence || []).forEach((row) => { const p = document.createElement("p"); const link = document.createElement("a"); link.href = apiUrl(`/v1/evidence/${encodeURIComponent(row.evidence_uuid)}`); link.target = "_blank"; link.rel = "noopener"; link.textContent = `${row.role}: ${row.filename}`; p.appendChild(link); evidence.appendChild(p); });
  const gallery = byId("assetPhotos"); gallery.replaceChildren();
  (asset.photo_evidence || []).forEach((photo) => { const image = document.createElement("img"); image.src = apiUrl(`/v1/evidence/${encodeURIComponent(photo.evidence_uuid)}`); image.alt = photo.filename || photo.media_role || "Asset photo"; image.loading = "lazy"; gallery.appendChild(image); });
}

async function selectAsset(assetUuid) { renderSelected(await apiJson(`/v1/assets/${encodeURIComponent(assetUuid)}`)); setStatus(`Selected ${state.selectedAsset.name}.`); }

function parseMetadata(id) {
  const text = byId(id).value.trim(); if (!text) return {};
  const value = JSON.parse(text); if (!value || Array.isArray(value) || typeof value !== "object") throw new Error("Metadata must be a JSON object."); return value;
}

async function createAsset() {
  const name = byId("newAssetName").value.trim(); if (!name) throw new Error("Asset name is required.");
  const result = await mutate("inventory.asset.create", { name, description: byId("newAssetDescription").value.trim(), category_uuid: byId("newAssetCategory").value || null, location_uuid: byId("newAssetLocation").value || null, metadata: parseMetadata("newAssetMetadata") });
  byId("newAssetName").value = ""; byId("newAssetDescription").value = ""; byId("newAssetMetadata").value = "";
  await loadAssets(); renderSelected(result.asset); setStatus(`Created ${result.asset.name} with immutable UUID ${result.asset.uuid}.`);
}

async function saveAsset() {
  if (!state.selectedAsset) throw new Error("Select an asset first.");
  const result = await mutate("inventory.asset.update", { asset_uuid: state.selectedAsset.uuid, name: byId("editAssetName").value.trim(), description: byId("editAssetDescription").value.trim(), category_uuid: byId("editAssetCategory").value || null, location_uuid: byId("editAssetLocation").value || null, metadata: parseMetadata("editAssetMetadata") });
  renderSelected(result.asset); await loadAssets(); setStatus("Asset edits committed and read back.");
}

async function relocateAsset() {
  if (!state.selectedAsset) throw new Error("Select an asset first.");
  const locationUuid = byId("editAssetLocation").value; if (!locationUuid) throw new Error("Choose a destination location.");
  const result = await mutate("inventory.asset.relocate", { asset_uuid: state.selectedAsset.uuid, location_uuid: locationUuid });
  renderSelected(result.asset); await loadAssets(); setStatus(`Relocated asset to ${locationName(locationUuid)}.`);
}

async function createCategory() {
  const name = byId("categoryName").value.trim(); if (!name) throw new Error("Category name is required.");
  await mutate("inventory.category.create", { name, parent_uuid: byId("categoryParent").value || null }); byId("categoryName").value = ""; await loadTree(); setStatus("Category created and read back.");
}

async function createLocation() {
  const name = byId("locationName").value.trim(); if (!name) throw new Error("Location name is required.");
  await mutate("inventory.location.create", { name, parent_uuid: byId("locationParent").value || null, location_type: byId("locationType").value }); byId("locationName").value = ""; await loadTree(); setStatus("Location created and read back.");
}

function commandForScan(rawValue, symbology) {
  const commandId = uuid(); const capturedAt = new Date().toISOString();
  return { command_id: commandId, command_type: "capture.barcode_qr_scan", actor_id: `client:${clientId()}`, submitted_at: capturedAt, idempotency_key: `scan:${commandId}`, payload: { scan_uuid: commandId, captured_at: capturedAt, raw_value: rawValue, symbology: symbology || "UNKNOWN", client_id: clientId(), scan_class_candidate: "client_unverified" } };
}

async function capture(rawValue, symbology) {
  const raw = String(rawValue || "").trim(); if (!raw) return;
  const command = commandForScan(raw, symbology);
  try {
    const result = await submitCommand(command);
    if (result.matched && result.asset) { renderSelected(result.asset); state.lastScan = null; byId("lastScan").textContent = `Matched ${raw} to ${result.asset.name}.`; switchTab("inventory"); }
    else { state.lastScan = { value: raw, symbology: symbology || "UNKNOWN" }; byId("lastScan").textContent = `Unmatched: ${raw}. Select or create an asset, then assign it.`; }
    setStatus(`Scan accepted: ${raw}`);
  } catch (error) {
    const rows = pending(); if (!rows.some((row) => row.idempotency_key === command.idempotency_key)) rows.push(command); savePending(rows); setStatus(`Queued locally: ${raw}\n${error.message}`);
  }
  byId("scanValue").value = "";
}

async function assignLastScan() {
  if (!state.lastScan) throw new Error("There is no unmatched scan waiting.");
  if (!state.selectedAsset) throw new Error("Select or create the asset that this code belongs to.");
  const result = await mutate("inventory.identifier.assign", { asset_uuid: state.selectedAsset.uuid, namespace: state.lastScan.symbology.toLowerCase() || "preprinted", value: state.lastScan.value });
  state.lastScan = null; byId("lastScan").textContent = "No unmatched scan waiting."; renderSelected(result.asset); setStatus("Identifier assigned to the selected asset.");
}

async function syncPending() {
  const rows = pending(); if (!rows.length) { setStatus("Nothing pending."); return; }
  const remaining = []; let synced = 0;
  for (const command of rows) { try { await submitCommand(command); synced += 1; } catch { remaining.push(command); } }
  savePending(remaining); setStatus(`Synced ${synced}; ${remaining.length} remain pending.`);
}

function exportPending() { const blob = new Blob([JSON.stringify(pending(), null, 2)], { type: "application/json" }); const url = URL.createObjectURL(blob); const anchor = document.createElement("a"); anchor.href = url; anchor.download = `mirror-pending-captures-${new Date().toISOString().replace(/[:.]/g, "-")}.json`; anchor.click(); URL.revokeObjectURL(url); }

async function makeDetector() {
  if (!("BarcodeDetector" in globalThis)) throw new Error("Camera barcode decoding is unavailable here. Use manual entry or a USB/Bluetooth keyboard-wedge scanner.");
  let formats = ["qr_code", "ean_13", "ean_8", "upc_a", "code_128"];
  if (typeof BarcodeDetector.getSupportedFormats === "function") { const supported = await BarcodeDetector.getSupportedFormats(); formats = formats.filter((format) => supported.includes(format)); }
  if (!formats.length) throw new Error("This runtime exposes BarcodeDetector but none of the requested formats.");
  return new BarcodeDetector({ formats });
}

async function cameraLoop() {
  if (!scanLoopActive || !detector || videoEl.readyState < 2) { if (scanLoopActive) requestAnimationFrame(cameraLoop); return; }
  try { const codes = await detector.detect(videoEl); if (codes.length) { const code = codes[0]; const value = String(code.rawValue || "").trim(); const now = Date.now(); if (value && (value !== lastCameraValue || now - lastCameraAt > 2500)) { lastCameraValue = value; lastCameraAt = now; await capture(value, String(code.format || "UNKNOWN").toUpperCase()); } } }
  catch (error) { setStatus(`Camera decode error: ${error.message}`); }
  if (scanLoopActive) requestAnimationFrame(cameraLoop);
}

async function startCamera() {
  if (globalThis.MirrorNative?.scanBarcode) { globalThis.MirrorNative.scanBarcode(); setStatus("Native Android scanner requested."); return; }
  if (!navigator.mediaDevices?.getUserMedia) throw new Error("Camera access requires a current secure browser/runtime.");
  detector = await makeDetector(); stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: { ideal: "environment" } }, audio: false }); videoEl.srcObject = stream; videoEl.hidden = false; await videoEl.play(); scanLoopActive = true; byId("startCamera").disabled = true; byId("stopCamera").disabled = false; setStatus("Camera scanner active."); requestAnimationFrame(cameraLoop);
}

function stopCamera() { scanLoopActive = false; if (stream) stream.getTracks().forEach((track) => track.stop()); stream = null; detector = null; videoEl.srcObject = null; videoEl.hidden = true; byId("startCamera").disabled = false; byId("stopCamera").disabled = true; }
globalThis.onMirrorNativeScanResult = (value, symbology) => capture(value, symbology || "UNKNOWN").catch(showError);

async function uploadFiles(files, role) {
  if (!state.selectedAsset) throw new Error("Select an asset first.");
  const list = [...files]; if (!list.length) throw new Error("Choose at least one file.");
  let done = 0;
  for (const file of list) {
    const form = new FormData(); form.set("asset_uuid", state.selectedAsset.uuid); form.set("role", role || "attachment"); form.set("file", file, file.name);
    const response = await authorizedFetch(apiUrl("/v1/evidence"), { method: "POST", body: form }); const result = await response.json().catch(() => ({})); if (!response.ok) throw new Error(result.detail || `Evidence API returned HTTP ${response.status}.`); if (result.readback_verified === false) throw new Error("Evidence upload did not pass canonical readback."); done += 1;
  }
  await selectAsset(state.selectedAsset.uuid); setStatus(`Uploaded and linked ${done} file${done === 1 ? "" : "s"}.`);
}

function previewPhoto() { const file = byId("photoFile").files?.[0]; const image = byId("photoPreview"); if (previewUrl) URL.revokeObjectURL(previewUrl); previewUrl = null; if (!file) { image.hidden = true; image.removeAttribute("src"); return; } previewUrl = URL.createObjectURL(file); image.src = previewUrl; image.hidden = false; }

function printLabel(kind) {
  if (!state.selectedAsset) throw new Error("Select an asset first.");
  const url = apiUrl(`/v1/labels/${encodeURIComponent(state.selectedAsset.uuid)}.svg?kind=${encodeURIComponent(kind)}`);
  if (globalThis.MirrorNative?.openExternal) globalThis.MirrorNative.openExternal(url); else window.open(url, "_blank", "noopener");
}

function speakPreview() {
  const text = byId("speechText").value.trim(); if (!text) return;
  if (globalThis.MirrorNative?.speak) { globalThis.MirrorNative.speak(text); setStatus("Native Android TTS requested."); return; }
  if (!("speechSynthesis" in globalThis)) { setStatus("Foreground speech preview is unavailable in this runtime."); return; }
  speechSynthesis.cancel(); speechSynthesis.speak(new SpeechSynthesisUtterance(text)); setStatus("Foreground TTS preview requested. This is not background reminder-delivery evidence.");
}

function providerUrl(provider, capabilities) {
  return apiUrl(`/v1/auth/${provider}/start?return_to=${encodeURIComponent(apiBase() + "/")}&capabilities=${encodeURIComponent(capabilities)}`);
}
function connectProvider(provider, capabilities) { const url = providerUrl(provider, capabilities); if (globalThis.MirrorNative?.openExternal) globalThis.MirrorNative.openExternal(url); else location.href = url; }
async function loadProviders() { const result = await apiJson("/v1/auth/providers"); byId("providerStatus").textContent = JSON.stringify(result, null, 2); }

function switchTab(name) { document.querySelectorAll(".panel").forEach((panel) => panel.classList.toggle("active", panel.id === `panel-${name}`)); document.querySelectorAll("nav [data-tab]").forEach((button) => button.setAttribute("aria-selected", String(button.dataset.tab === name))); }
function showError(error) { setStatus(error?.message || String(error)); }

function bindEvents() {
  document.querySelectorAll("nav [data-tab]").forEach((button) => button.addEventListener("click", () => switchTab(button.dataset.tab)));
  byId("saveSettings").addEventListener("click", async () => { localStorage.setItem(API_BASE_STORAGE_KEY, apiBase()); await initializeData(); });
  byId("checkSystem").addEventListener("click", () => preflight().catch(showError));
  byId("searchAssets").addEventListener("click", () => loadAssets().catch(showError));
  byId("assetSearch").addEventListener("keydown", (event) => { if (event.key === "Enter") loadAssets().catch(showError); });
  byId("createAsset").addEventListener("click", () => createAsset().catch(showError));
  byId("saveAsset").addEventListener("click", () => saveAsset().catch(showError));
  byId("relocateAsset").addEventListener("click", () => relocateAsset().catch(showError));
  byId("createCategory").addEventListener("click", () => createCategory().catch(showError));
  byId("createLocation").addEventListener("click", () => createLocation().catch(showError));
  byId("scanForm").addEventListener("submit", async (event) => { event.preventDefault(); await capture(byId("scanValue").value, byId("symbology").value); });
  byId("startCamera").addEventListener("click", () => startCamera().catch(showError)); byId("stopCamera").addEventListener("click", stopCamera);
  byId("assignScan").addEventListener("click", () => assignLastScan().catch(showError)); byId("syncPending").addEventListener("click", () => syncPending().catch(showError)); byId("exportPending").addEventListener("click", exportPending);
  byId("evidenceFiles").addEventListener("change", () => setStatus(`${byId("evidenceFiles").files.length} file(s) selected.`));
  byId("uploadEvidence").addEventListener("click", () => uploadFiles(byId("evidenceFiles").files, byId("evidenceRole").value).catch(showError));
  byId("photoFile").addEventListener("change", previewPhoto); byId("uploadPhoto").addEventListener("click", () => { const file = byId("photoFile").files?.[0]; if (file && file.size > MAX_PHOTO_BYTES) return showError(new Error("Image exceeds the 15 MiB quick-photo limit.")); uploadFiles(file ? [file] : [], "gallery").catch(showError); });
  const drop = byId("dropzone"); ["dragenter", "dragover"].forEach((name) => drop.addEventListener(name, (event) => { event.preventDefault(); drop.classList.add("drag"); })); ["dragleave", "drop"].forEach((name) => drop.addEventListener(name, (event) => { event.preventDefault(); drop.classList.remove("drag"); })); drop.addEventListener("drop", (event) => uploadFiles(event.dataTransfer.files, byId("evidenceRole").value).catch(showError));
  byId("printQr").addEventListener("click", () => { try { printLabel("qr"); } catch (error) { showError(error); } }); byId("printBarcode").addEventListener("click", () => { try { printLabel("code128"); } catch (error) { showError(error); } });
  byId("speakTest").addEventListener("click", speakPreview);
  byId("googleIdentity").addEventListener("click", () => connectProvider("google", "identity")); byId("googleWorkspace").addEventListener("click", () => connectProvider("google", "drive,sheets,calendar")); byId("googleGmail").addEventListener("click", () => connectProvider("google", "gmail_read")); byId("microsoftIdentity").addEventListener("click", () => connectProvider("microsoft", "identity")); byId("microsoftWorkspace").addEventListener("click", () => connectProvider("microsoft", "drive,calendar"));
}

async function initializeData() {
  if (!apiBase()) { setMutationAllowed(false, "Configure the mirror API address in System."); return; }
  await preflight(); await Promise.all([loadTree(), loadAssets(), loadProviders()]);
}

function initialize() {
  const stored = localStorage.getItem(API_BASE_STORAGE_KEY) || ""; if (byId("apiBase")) byId("apiBase").value = stored;
  savePending(pending()); bindEvents(); setMutationAllowed(false); initializeData().catch(showError);
  if ("serviceWorker" in navigator && !globalThis.MirrorNative) navigator.serviceWorker.register("sw.js").catch(() => {});
}

document.addEventListener("DOMContentLoaded", initialize);
