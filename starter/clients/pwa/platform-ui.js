"use strict";

(() => {
  function el(tag, attrs = {}, children = []) {
    const node = document.createElement(tag);
    for (const [key, value] of Object.entries(attrs)) {
      if (key === "class") node.className = value;
      else if (key === "text") node.textContent = value;
      else if (key === "html") node.innerHTML = value;
      else if (key.startsWith("data-")) node.setAttribute(key, value);
      else if (key === "checked") node.checked = Boolean(value);
      else node[key] = value;
    }
    for (const child of children) node.append(child);
    return node;
  }

  async function jsonRequest(path, method = "GET", body = null) {
    const options = { method, headers: {} };
    if (body !== null) {
      options.headers["Content-Type"] = "application/json";
      options.body = JSON.stringify(body);
    }
    return apiJson(path, options);
  }

  function addTab(name, label) {
    const nav = document.querySelector("header nav");
    if (!nav || nav.querySelector(`[data-tab='${name}']`)) return;
    const button = el("button", { text: label });
    button.dataset.tab = name;
    button.setAttribute("aria-selected", "false");
    button.addEventListener("click", () => switchTab(name));
    nav.append(button);
  }

  function card(title, className = "") {
    const wrapper = el("div", { class: `card ${className}`.trim() });
    wrapper.append(el("h2", { text: title }));
    return wrapper;
  }

  function ensurePanel(name) {
    const main = document.querySelector("main");
    let panel = document.getElementById(`panel-${name}`);
    if (!panel) {
      panel = el("section", { id: `panel-${name}`, class: "panel" });
      main.append(panel);
    }
    return panel;
  }

  function splitLines(value) {
    return String(value || "").split(/\r?\n/).map((line) => line.trim()).filter(Boolean);
  }

  function targetSurfaces() {
    return [...document.querySelectorAll("[data-feature-surface]:checked")].map((input) => input.value);
  }

  async function loadFeatureRequests() {
    const host = document.getElementById("featureRequestList");
    if (!host) return;
    const result = await apiJson("/v1/features/requests?limit=50");
    host.replaceChildren();
    for (const request of result.feature_requests || []) {
      const item = el("div", { class: "mira-list-item" });
      const header = el("div", { class: "mira-toolbar" });
      header.append(el("strong", { text: request.title }));
      header.append(el("span", { class: `mira-badge ${request.status === "deployed" ? "ok" : ""}`, text: request.status }));
      item.append(header);
      item.append(el("div", { class: "muted", text: request.request_text }));
      item.append(el("small", { text: `${request.request_uuid} • ${request.target_surfaces.join(", ")}` }));
      host.append(item);
    }
    if (!(result.feature_requests || []).length) host.append(el("div", { class: "muted", text: "No feature requests queued." }));
  }

  async function submitFeatureRequest() {
    const title = document.getElementById("featureTitle").value.trim();
    const requestText = document.getElementById("featureText").value.trim();
    if (!title || !requestText) throw new Error("Feature title and description are required.");
    const result = await jsonRequest("/v1/features/requests", "POST", {
      title,
      request_text: requestText,
      acceptance: splitLines(document.getElementById("featureAcceptance").value),
      target_surfaces: targetSurfaces(),
      source: "mira_feature_studio",
    });
    document.getElementById("featureTitle").value = "";
    document.getElementById("featureText").value = "";
    document.getElementById("featureAcceptance").value = "";
    setStatus(`Feature request ${result.request_uuid} stored in MIRROR. Git remains the implementation authority.`);
    await loadFeatureRequests();
  }

  async function loadPlatformCapabilities() {
    const result = await apiJson("/v1/platform/capabilities");
    const host = document.getElementById("platformCapabilityStatus");
    if (host) host.textContent = JSON.stringify(result, null, 2);
  }

  async function checkHomeAssistant() {
    const result = await apiJson("/v1/integrations/home-assistant/status");
    const host = document.getElementById("haStatus");
    if (host) {
      host.className = `mira-callout${result.configured && result.reachable ? "" : " mira-warning"}`;
      host.textContent = result.configured
        ? (result.reachable ? "Home Assistant is configured and reachable. It remains an integration, not canonical authority." : "Home Assistant is configured but not reachable.")
        : "Home Assistant adapter is installed but not configured on this MIRROR server.";
    }
  }

  async function bindRfidTag() {
    if (!state.selectedAsset) throw new Error("Select an asset in Inventory first.");
    const tagId = document.getElementById("rfidTagId").value.trim();
    if (!tagId) throw new Error("RFID/NFC tag ID is required.");
    const protocol = document.getElementById("rfidProtocol").value;
    const result = await jsonRequest("/v1/rfid/tags/bind", "POST", {
      asset_uuid: state.selectedAsset.uuid,
      protocol,
      tag_id: tagId,
    });
    document.getElementById("rfidTagId").value = "";
    setStatus(`RFID alias ${result.tag_value} bound to immutable asset UUID ${result.asset_uuid}.`);
    await selectAsset(state.selectedAsset.uuid);
  }

  async function exportMirror() {
    const result = await apiJson("/v1/migrations/export");
    const blob = new Blob([JSON.stringify(result, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `mirror-export-${new Date().toISOString().replace(/[:.]/g, "-")}.json`;
    link.click();
    URL.revokeObjectURL(url);
    setStatus("Canonical MIRROR export created. UUID identities are preserved in the export contract.");
  }

  async function stageJsonMigration() {
    const raw = document.getElementById("migrationJson").value.trim();
    if (!raw) throw new Error("Paste JSON to stage first.");
    const parsed = JSON.parse(raw);
    const result = await jsonRequest("/v1/migrations/stage", "POST", {
      source_type: "manual_json",
      source_locator: "mira-client-paste",
      payload: parsed,
    });
    document.getElementById("migrationResult").textContent = JSON.stringify(result, null, 2);
    setStatus(`Migration snapshot ${result.snapshot_uuid} staged without changing canonical state.`);
  }

  function startGoogleMigrationAuth() {
    const returnTo = apiBase() ? `${apiBase()}/` : "/";
    const url = apiUrl(`/v1/migrations/google/auth/start?return_to=${encodeURIComponent(returnTo)}`);
    if (globalThis.MirrorNative?.openExternal) globalThis.MirrorNative.openExternal(url);
    else location.href = url;
  }

  async function discoverGoogleSheets() {
    const result = await apiJson("/v1/migrations/google/discover?page_size=250");
    const select = document.getElementById("googleSheetSelect");
    select.replaceChildren(new Option("Choose a spreadsheet", ""));
    for (const sheet of result.spreadsheets || []) {
      select.add(new Option(`${sheet.name}${sheet.modifiedTime ? ` • ${sheet.modifiedTime.slice(0,10)}` : ""}`, sheet.id));
    }
    document.getElementById("migrationResult").textContent = JSON.stringify(result, null, 2);
    setStatus(`Discovered ${(result.spreadsheets || []).length} Google spreadsheets available to the migration scope.`);
  }

  async function stageGoogleSheet() {
    const fileId = document.getElementById("googleSheetSelect").value;
    if (!fileId) throw new Error("Choose a Google spreadsheet first.");
    const result = await jsonRequest("/v1/migrations/google/stage-sheet", "POST", { file_id: fileId });
    document.getElementById("migrationResult").textContent = JSON.stringify(result, null, 2);
    setStatus(`Google spreadsheet staged as ${result.snapshot_uuid}; canonical state was not changed.`);
  }

  function buildFeaturePanel() {
    addTab("features", "Feature Studio");
    const panel = ensurePanel("features");
    if (panel.childElementCount) return;

    const studio = card("Feature Studio", "wide");
    studio.append(el("div", { class: "mira-callout", text: "Describe the feature here. MIRROR stores the request durably. ChatGPT Plus can act as the conversational development console through the companion/MCP path; MIRA does not require an OpenAI API key." }));
    const form = el("div", { class: "row" });
    form.append(el("input", { id: "featureTitle", placeholder: "Short feature name" }));
    form.append(el("textarea", { id: "featureText", placeholder: "Describe what the feature should do in plain English." }));
    form.append(el("textarea", { id: "featureAcceptance", placeholder: "Acceptance criteria, one per line" }));
    const checks = el("div", { class: "mira-checkboxes" });
    for (const surface of ["web", "windows", "linux", "android"]) {
      const input = el("input", { type: "checkbox", value: surface, checked: true });
      input.setAttribute("data-feature-surface", "true");
      checks.append(el("label", {}, [input, document.createTextNode(surface)]));
    }
    form.append(checks);
    const submit = el("button", { id: "submitFeatureRequest", class: "primary-action", text: "Queue feature request" });
    submit.addEventListener("click", () => submitFeatureRequest().catch(showError));
    form.append(submit);
    studio.append(form);

    const flow = card("How feature delivery works");
    flow.append(el("div", { class: "mira-metric-grid" }, [
      el("div", { class: "mira-metric", html: "<strong>1. Request</strong><small>MIRA stores intent and acceptance criteria.</small>" }),
      el("div", { class: "mira-metric", html: "<strong>2. Build</strong><small>ChatGPT companion works against Git, not the live database.</small>" }),
      el("div", { class: "mira-metric", html: "<strong>3. Prove</strong><small>CI builds the same release for every client.</small>" }),
      el("div", { class: "mira-metric", html: "<strong>4. Deliver</strong><small>Signed release channels update installed clients.</small>" }),
    ]));

    const queue = card("Feature queue", "wide");
    const toolbar = el("div", { class: "mira-toolbar" });
    const refresh = el("button", { text: "Refresh queue" });
    refresh.addEventListener("click", () => loadFeatureRequests().catch(showError));
    toolbar.append(refresh);
    queue.append(toolbar, el("div", { id: "featureRequestList", class: "mira-list" }));
    panel.append(studio, flow, queue);
  }

  function buildIntegrationPanel() {
    addTab("integrations", "Integrations");
    const panel = ensurePanel("integrations");
    if (panel.childElementCount) return;

    const overview = card("Integration foundation", "wide");
    overview.append(el("div", { class: "mira-callout", text: "MIRROR owns canonical identity and state. Google, Microsoft, Home Assistant, RFID readers, and future providers connect through adapters so changing a provider does not rewrite the product." }));
    const capButton = el("button", { text: "Refresh platform capabilities" });
    capButton.addEventListener("click", () => loadPlatformCapabilities().catch(showError));
    overview.append(capButton, el("pre", { id: "platformCapabilityStatus", class: "mira-code" }));

    const rfid = card("RFID / NFC identity");
    rfid.append(el("p", { class: "muted", text: "Bind a replaceable tag to the immutable UUID of the asset currently selected in Inventory." }));
    const rfidForm = el("div", { class: "row" });
    const protocol = el("select", { id: "rfidProtocol" });
    for (const [value, label] of [["nfc_uid","NFC UID"],["hf_uid","HF UID"],["epc_gen2","UHF EPC Gen2"],["other","Other"]]) protocol.add(new Option(label, value));
    rfidForm.append(protocol, el("input", { id: "rfidTagId", placeholder: "Tag UID / EPC" }));
    const bind = el("button", { class: "primary-action", text: "Bind tag to selected asset" });
    bind.addEventListener("click", () => bindRfidTag().catch(showError));
    rfidForm.append(bind);
    rfid.append(rfidForm);

    const ha = card("Home Assistant");
    ha.append(el("p", { class: "muted", text: "Foundation supports geofence/presence events and generic HA service calls for later shopping-list, notification, device-state, and automation features. HA credentials stay on the MIRROR server." }));
    const check = el("button", { text: "Check Home Assistant" });
    check.addEventListener("click", () => checkHomeAssistant().catch(showError));
    ha.append(check, el("div", { id: "haStatus", class: "mira-warning", text: "Status not checked." }));
    panel.append(overview, rfid, ha);
  }

  function buildMigrationPanel() {
    addTab("migration", "Migration");
    const panel = ensurePanel("migration");
    if (panel.childElementCount) return;

    const exportCard = card("Portable MIRROR export");
    exportCard.append(el("p", { class: "muted", text: "Export canonical UUIDs and structured state before changing machines or storage providers." }));
    const exportButton = el("button", { class: "primary-action", text: "Export canonical state" });
    exportButton.addEventListener("click", () => exportMirror().catch(showError));
    exportCard.append(exportButton);

    const google = card("Import existing Google Sheets", "wide");
    google.append(el("div", { class: "mira-warning", text: "Migration access is intentionally separate from normal Drive access. It asks Google for read-only Drive/Sheets visibility, stages a snapshot, and does not silently overwrite MIRROR." }));
    const buttons = el("div", { class: "mira-toolbar" });
    const connect = el("button", { text: "Grant Google migration read access" });
    connect.addEventListener("click", startGoogleMigrationAuth);
    const discover = el("button", { text: "Discover spreadsheets" });
    discover.addEventListener("click", () => discoverGoogleSheets().catch(showError));
    buttons.append(connect, discover);
    const select = el("select", { id: "googleSheetSelect" });
    select.add(new Option("Choose a spreadsheet", ""));
    const stage = el("button", { class: "primary-action", text: "Stage selected spreadsheet" });
    stage.addEventListener("click", () => stageGoogleSheet().catch(showError));
    google.append(buttons, select, stage);

    const jsonCard = card("Stage JSON / legacy export");
    jsonCard.append(el("textarea", { id: "migrationJson", placeholder: "Paste a legacy JSON export here. Staging never changes canonical state." }));
    const stageJson = el("button", { text: "Stage JSON snapshot" });
    stageJson.addEventListener("click", () => stageJsonMigration().catch(showError));
    jsonCard.append(stageJson);

    const result = card("Migration result", "wide");
    result.append(el("pre", { id: "migrationResult", class: "mira-code" }));
    panel.append(exportCard, google, jsonCard, result);
  }

  async function initialize() {
    buildFeaturePanel();
    buildIntegrationPanel();
    buildMigrationPanel();
    if (apiBase()) {
      loadFeatureRequests().catch(() => {});
      loadPlatformCapabilities().catch(() => {});
      checkHomeAssistant().catch(() => {});
    }
  }

  globalThis.MirrorPlatformUI = { initialize };
})();
