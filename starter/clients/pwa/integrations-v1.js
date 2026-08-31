"use strict";

(() => {
  const $ = (id) => document.getElementById(id);

  function el(tag, attrs = {}, children = []) {
    const node = document.createElement(tag);
    Object.entries(attrs).forEach(([key, value]) => {
      if (key === "text") node.textContent = value;
      else if (key === "class") node.className = value;
      else node.setAttribute(key, value);
    });
    children.forEach((child) => node.append(child));
    return node;
  }

  async function loadCatalog() {
    const result = await apiJson("/v1/integrations/catalog");
    const grid = $("miraIntegrationCatalog");
    if (!grid) return;
    grid.replaceChildren();
    Object.entries(result.services || {}).forEach(([serviceType, spec]) => {
      if (spec.status === "reserved_contract_only") return;
      const button = el("button", { class: "mira-integration-card" }, [
        el("strong", { text: spec.display_name }),
        el("small", { text: `${spec.category.replaceAll("_", " ")} • ${spec.default_connection_mode === "local_bridge" ? "works with Google-first local bridge" : "direct integration"}` }),
      ]);
      button.addEventListener("click", () => selectService(serviceType, spec));
      grid.append(button);
    });
    await loadEnrolled();
  }

  function selectService(serviceType, spec) {
    $("integrationServiceType").value = serviceType;
    $("integrationDisplayName").value = spec.display_name || serviceType;
    $("integrationMode").value = "local_bridge";
    $("integrationUrl").value = "";
    $("integrationFormTitle").textContent = `Add ${spec.display_name}`;
    $("integrationHelp").textContent = "Google-first users should keep Local bridge selected. MIRA on a Windows, Linux, or Android device talks to the service on your home network while Google remains your reality store. Self-hosted MIRROR users can choose direct access instead.";
    $("integrationEnrollment").hidden = false;
  }

  async function enroll() {
    const serviceType = $("integrationServiceType").value;
    const connectionMode = $("integrationMode").value;
    const baseUrl = $("integrationUrl").value.trim();
    if (!serviceType) throw new Error("Choose a service first.");
    if (connectionMode !== "local_bridge" && !baseUrl) throw new Error("Enter the service address.");
    const result = await apiJson("/v1/integrations/enroll", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        service_type: serviceType,
        display_name: $("integrationDisplayName").value.trim(),
        connection_mode: connectionMode,
        base_url: baseUrl || undefined,
      }),
    });
    setStatus(result.next_step || "Integration enrolled.");
    $("integrationEnrollment").hidden = true;
    await loadEnrolled();
  }

  async function loadEnrolled() {
    const host = $("miraEnrolledIntegrations");
    if (!host) return;
    const result = await apiJson("/v1/integrations");
    host.replaceChildren();
    if (!(result.integrations || []).length) {
      host.append(el("p", { class: "muted", text: "No local/self-hosted services enrolled yet. Stock MIRA still works with Google Workspace." }));
      return;
    }
    (result.integrations || []).forEach((item) => {
      const card = el("div", { class: "mira-integration-row" }, [
        el("strong", { text: item.display_name }),
        el("span", { class: "pill", text: item.service_type }),
        el("small", { text: `${item.connection_mode.replaceAll("_", " ")} • ${item.connection_state.replaceAll("_", " ")}` }),
      ]);
      if (item.connection_mode !== "local_bridge") {
        const verify = el("button", { text: "Verify connection" });
        verify.addEventListener("click", async () => {
          const checked = await apiJson(`/v1/integrations/${item.integration_uuid}/verify`, { method: "POST" });
          setStatus(checked.readback_verified ? `${item.display_name} verified.` : `${item.display_name} could not be verified.`);
          await loadEnrolled();
        });
        card.append(verify);
      } else {
        card.append(el("div", { class: "mira-callout", text: "Next: pair a MIRA app on the same network. Service credentials stay on that device and are never sent to ChatGPT." }));
      }
      host.append(card);
    });
  }

  async function loadBackupPolicy() {
    const host = $("miraBackupPolicy");
    if (!host || !apiBase()) return;
    try {
      const policy = await apiJson("/v1/backups/policy");
      $("backupEnabled").checked = Boolean(policy.enabled);
      $("backupFullDays").value = String(policy.full_interval_days || 7);
      $("backupIncrementalDays").value = String(policy.incremental_interval_days || 1);
      $("backupDestination").value = policy.destination || "google_drive";
      host.hidden = false;
    } catch (_) {
      host.hidden = true;
    }
  }

  async function saveBackupPolicy() {
    const result = await apiJson("/v1/backups/policy", {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        enabled: $("backupEnabled").checked,
        full_interval_days: Number($("backupFullDays").value),
        incremental_interval_days: Number($("backupIncrementalDays").value),
        destination: $("backupDestination").value,
      }),
    });
    setStatus(`Backup schedule saved. Complete every ${result.policy.full_interval_days} day(s); change backup every ${result.policy.incremental_interval_days} day(s).`);
  }

  function buildPanel() {
    const nav = document.querySelector("header nav");
    if (!nav || $("panel-integrations-v1")) return;
    const tab = el("button", { "data-tab": "integrations-v1", "aria-selected": "false", text: "Integrations" });
    tab.addEventListener("click", () => { switchTab("integrations-v1"); loadCatalog().catch(showError); loadBackupPolicy().catch(() => {}); });
    nav.append(tab);

    const panel = el("section", { id: "panel-integrations-v1", class: "panel" });
    panel.innerHTML = `
      <div class="card wide">
        <h2>Add self-hosted services</h2>
        <div class="mira-callout"><strong>No Linux required.</strong> Google Workspace remains the stock MIRA authority. A local MIRA app can bridge private services such as Paperless, Home Assistant, Plex, Sonarr/Radarr, Node-RED or MQTT without exposing their passwords to ChatGPT.</div>
        <div id="miraIntegrationCatalog" class="mira-integration-grid"></div>
      </div>
      <div id="integrationEnrollment" class="card wide" hidden>
        <h2 id="integrationFormTitle">Add service</h2>
        <p id="integrationHelp" class="muted"></p>
        <input id="integrationServiceType" type="hidden">
        <label>Name<input id="integrationDisplayName"></label>
        <label>How should MIRA reach it?
          <select id="integrationMode">
            <option value="local_bridge">Local bridge — recommended for Google-first users</option>
            <option value="self_hosted_mirror">Self-hosted MIRROR on the same network</option>
            <option value="direct_https">Verified HTTPS endpoint</option>
          </select>
        </label>
        <label>Service address<input id="integrationUrl" placeholder="Example: http://homeassistant.local:8123"></label>
        <p class="muted">For Local bridge, the address and service secret are finished on the local device. Do not paste service passwords into ChatGPT.</p>
        <button id="integrationEnrollButton" class="primary-action">Add service</button>
      </div>
      <div class="card wide"><h2>Your enrolled services</h2><div id="miraEnrolledIntegrations"></div></div>
      <div id="miraBackupPolicy" class="card wide" hidden>
        <h2>Automatic backups</h2>
        <p class="muted">Recommended: a complete backup once a week, and a change backup once a day. Google Drive is the stock destination.</p>
        <label class="mira-v1-choice"><input id="backupEnabled" type="checkbox"> <span>Automatic backups on</span></label>
        <div class="split">
          <label>Complete backup<select id="backupFullDays"><option value="1">Every day</option><option value="7">Once a week — recommended</option><option value="14">Every two weeks</option><option value="30">Once a month</option></select></label>
          <label>Change backup<select id="backupIncrementalDays"><option value="1">Every day — recommended</option><option value="2">Every two days</option><option value="7">Once a week</option></select></label>
          <label>Backup location<select id="backupDestination"><option value="google_drive">Google Drive — recommended</option><option value="onedrive">OneDrive</option><option value="local">This self-hosted MIRROR server</option></select></label>
        </div>
        <button id="backupSaveButton" class="primary-action">Save backup schedule</button>
      </div>`;
    document.querySelector("main")?.append(panel);
    $("integrationEnrollButton")?.addEventListener("click", () => enroll().catch(showError));
    $("backupSaveButton")?.addEventListener("click", () => saveBackupPolicy().catch(showError));
  }

  function augmentSetupAndWizard() {
    const setup = document.getElementById("panel-setup");
    if (setup && !document.getElementById("miraSelfHostedSetupShortcut")) {
      const card = el("div", { id: "miraSelfHostedSetupShortcut", class: "card wide" }, [
        el("h2", { text: "Optional services on your home or business network" }),
        el("p", { class: "muted", text: "MIRA works with Google Workspace first. You can also add Paperless, Home Assistant, Plex, Sonarr/Radarr, Node-RED, MQTT, and future local services without changing where your canonical data lives." }),
      ]);
      const button = el("button", { class: "primary-action", text: "Add self-hosted services" });
      button.addEventListener("click", () => { switchTab("integrations-v1"); loadCatalog().catch(showError); });
      card.append(button); setup.append(card);
    }
    const dialog = document.querySelector(".mira-v1-dialog");
    if (dialog && !dialog.querySelector("[data-mira-local-services]")) {
      const steps = [...dialog.querySelectorAll(".step")];
      const connectStep = steps.find((step) => /connect your accounts/i.test(step.querySelector("h3")?.textContent || ""));
      if (connectStep) {
        const hint = el("div", { class: "mira-callout", "data-mira-local-services": "true", text: "Optional later: add self-hosted services such as Home Assistant, Paperless or Plex. You do not need Linux or a server for stock MIRA." });
        connectStep.append(hint);
      }
    }
  }

  const observer = new MutationObserver(() => { buildPanel(); augmentSetupAndWizard(); });
  observer.observe(document.documentElement, { childList: true, subtree: true });
  document.addEventListener("DOMContentLoaded", () => { buildPanel(); augmentSetupAndWizard(); });
})();
