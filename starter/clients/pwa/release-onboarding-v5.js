"use strict";

(() => {
  const LEGACY_KEY = "mira.onboarding.1.0.completed";
  const KEY = "mira.onboarding.release-v5.completed";
  const MODE_KEY = "mira.deployment.mode.v1";
  const API_STORAGE_KEY = "mirror.capture.api-base.v2";
  let currentOverlay = null;

  function el(tag, cls = "", text = "") {
    const node = document.createElement(tag);
    if (cls) node.className = cls;
    if (text) node.textContent = text;
    return node;
  }

  function button(label, action, primary = false) {
    const item = el("button", primary ? "primary-action" : "", label);
    item.type = "button";
    item.addEventListener("click", () => Promise.resolve(action()).catch((error) => {
      globalThis.MiraActionAudit?.announce?.(error?.message || String(error));
    }));
    return item;
  }

  function announce(message) {
    if (globalThis.MiraActionAudit?.announce) globalThis.MiraActionAudit.announce(message);
    else if (typeof setStatus === "function") setStatus(message);
  }

  function modeCard(value, title, description, recommended = false) {
    const label = el("label", "mira-release-mode");
    const radio = document.createElement("input");
    radio.type = "radio";
    radio.name = "miraReleaseMode";
    radio.value = value;
    if (value === (localStorage.getItem(MODE_KEY) || "cloud")) radio.checked = true;
    const copy = el("span", "mira-release-mode-copy");
    const head = el("strong", "", title);
    if (recommended) head.append(el("span", "mira-release-badge", "Recommended"));
    copy.append(head, el("span", "muted", description));
    label.append(radio, copy);
    return label;
  }

  function selectedMode(root) {
    return root.querySelector("input[name='miraReleaseMode']:checked")?.value || "cloud";
  }

  function connectionState() {
    return globalThis.MiraProviderConnect?.state?.() || {};
  }

  function cloudConnected() {
    return globalThis.MiraProviderConnect?.isCloudConnected?.() === true;
  }

  function saveDeploymentMode(mode) {
    localStorage.setItem(MODE_KEY, mode);
  }

  async function testSelfHosted(urlInput, result) {
    const base = urlInput.value.trim().replace(/\/+$/, "");
    if (!/^https?:\/\//i.test(base)) throw new Error("Enter the full MIRROR address, beginning with https:// (or http:// for local testing).");
    result.textContent = "Checking MIRROR…";
    const response = await fetch(`${base}/v1/health`, { headers: { "X-Mirror-Client": "mira-setup/0.2.0" } });
    if (!response.ok) throw new Error(`MIRROR answered with HTTP ${response.status}.`);
    const payload = await response.json();
    if (payload.status !== "ready") throw new Error("That server answered, but MIRROR is not ready yet.");
    localStorage.setItem(API_STORAGE_KEY, base);
    const field = document.getElementById("apiBase");
    if (field) field.value = base;
    result.textContent = "Connected to MIRROR.";
    result.dataset.connected = "true";
    announce("Self-hosted MIRROR is connected.");
  }

  function providerPanel() {
    const panel = el("div", "mira-release-provider-panel");
    const status = el("div", "mira-release-connection-status");
    status.id = "miraReleaseProviderStatus";
    const actions = el("div", "actions");
    actions.append(
      button("Continue with Google", () => globalThis.MiraProviderConnect.connect("google", "identity"), true),
      button("Use Microsoft 365", () => globalThis.MiraProviderConnect.connect("microsoft", "identity"))
    );
    panel.append(actions, status);
    refreshConnection(connectionState(), status);
    return panel;
  }

  function refreshConnection(state = connectionState(), explicitHost = null) {
    const host = explicitHost || document.getElementById("miraReleaseProviderStatus");
    if (!host) return;
    if (state.status === "connected") {
      host.className = "mira-release-connection-status connected";
      host.textContent = state.provider === "microsoft_365" ? "Microsoft 365 connected." : "Google connected.";
      return;
    }
    if (state.status === "release_configuration_missing") {
      host.className = "mira-release-connection-status error";
      host.textContent = state.error || "This build is missing its cloud connection registration.";
      return;
    }
    if (state.status === "error") {
      host.className = "mira-release-connection-status error";
      host.textContent = state.error || "Account connection did not finish.";
      return;
    }
    host.className = "mira-release-connection-status";
    host.textContent = "No cloud account connected yet.";
  }

  function show(force = false) {
    if (!force && localStorage.getItem(KEY) === "true") return;
    currentOverlay?.remove();
    const overlay = el("div", "mira-release-overlay");
    overlay.id = "miraReleaseOnboarding";
    const card = el("div", "mira-release-dialog");
    const brand = document.createElement("img");
    brand.src = "brand-wordmark.svg";
    brand.alt = "MIRA — assistant. MIRROR — your private data.";
    brand.className = "mira-release-brand";
    const title = el("h2", "", "Set up MIRA");
    const sub = el("p", "muted", "MIRA is your assistant. MIRROR is the private data store that keeps MIRA consistent between ChatGPT and any MIRA app you choose to use.");
    card.append(brand, title, sub);

    const steps = [];
    const welcome = el("section", "mira-release-step");
    welcome.append(
      el("h3", "", "One assistant. One shared memory of what is true."),
      el("p", "", "Talk to MIRA in ChatGPT. MIRROR keeps the durable records. The MIRA app is optional: it is a fast way to scan, photograph, enter and display MIRROR data."),
      el("div", "mira-release-explain", "Anything added in the app goes into MIRROR. Anything MIRA writes into MIRROR can appear in the app. Both must agree on the same state.")
    );
    steps.push(welcome);

    const deployment = el("section", "mira-release-step");
    deployment.append(el("h3", "", "Where should MIRROR live?"), el("p", "muted", "There is no chat-only mode. MIRA always needs a durable place to keep your data."));
    const modes = el("div", "mira-release-modes");
    modes.append(
      modeCard("cloud", "Cloud", "ChatGPT + Google Workspace or Microsoft 365. No Linux or server required.", true),
      modeCard("cloud_local", "Cloud + local services", "Same simple cloud setup, plus optional access to Home Assistant, Plex, Paperless and other services on your network."),
      modeCard("self_hosted", "Self-hosted", "Run MIRROR on your own system. Google or Microsoft can still be connected later, but they are optional.")
    );
    deployment.append(modes);
    steps.push(deployment);

    const connection = el("section", "mira-release-step");
    connection.append(el("h3", "", "Connect MIRROR"), el("p", "mira-release-mode-help", "Connect the account or server that will hold your MIRROR data."));
    const cloud = providerPanel();
    cloud.id = "miraReleaseCloudConnect";
    const selfHost = el("div", "mira-release-selfhost");
    selfHost.id = "miraReleaseSelfHost";
    const server = document.createElement("input");
    server.type = "url";
    server.placeholder = "https://mirror.example.com";
    server.value = localStorage.getItem(API_STORAGE_KEY) || "";
    const serverResult = el("div", "mira-release-connection-status", "Not connected yet.");
    selfHost.append(server, button("Check MIRROR connection", () => testSelfHosted(server, serverResult), true), serverResult);
    connection.append(cloud, selfHost);
    steps.push(connection);

    const profile = el("section", "mira-release-step");
    profile.append(el("h3", "", "A few useful defaults"), el("p", "muted", "These can all be changed later. The app does not replace MIRA's full first-time interview in ChatGPT."));
    const profileSelect = document.createElement("select");
    profileSelect.id = "miraReleaseProfile";
    [["personal", "Personal"], ["family", "Family"], ["institutional-pilot", "Institutional pilot"]].forEach(([value, label]) => profileSelect.add(new Option(label, value)));
    const toggles = el("div", "mira-release-toggles");
    [
      ["inventory", "Inventory and item tracking", true],
      ["receipts", "Receipt capture and purchase history", true],
      ["spoken", "Spoken reminders on supported devices", true],
      ["nfc", "NFC / RFID item tagging", false],
      ["ble", "Bluetooth proximity tags", false]
    ].forEach(([value, label, checked]) => {
      const row = el("label", "mira-release-toggle");
      const input = document.createElement("input"); input.type = "checkbox"; input.value = value; input.checked = checked;
      row.append(input, el("span", "", label)); toggles.append(row);
    });
    profile.append(profileSelect, toggles);
    steps.push(profile);

    const physical = el("section", "mira-release-step");
    physical.append(
      el("h3", "", "How item tracking works"),
      el("p", "", "Every item gets one permanent MIRA identity. Serial numbers, UPCs, QR labels, NFC/RFID tags and other codes can all point to that item."),
      el("p", "muted", "You normally never need to see the technical record ID. MIRA keeps it underneath so changing a sticker or tag does not create a new item."),
      el("p", "", "Locations are hierarchical too. Put an item in Tote A, put Tote A on Shelf 3, and MIRA understands the full location automatically.")
    );
    steps.push(physical);

    const ready = el("section", "mira-release-step");
    ready.append(
      el("h3", "", "Ready"),
      el("p", "", "Use the MIRA app for quick capture and display: scan items, take pictures, add receipts, move things between locations and see Upcoming or your to-do list."),
      el("p", "muted", "Use ChatGPT for the larger MIRA experience: conversation, planning, reconciliation, feature requests and anything that benefits from reasoning. Both use MIRROR.")
    );
    steps.push(ready);

    let index = 0;
    const footer = el("div", "mira-release-footer");
    const back = button("Back", () => { if (index > 0) { index -= 1; render(); } });
    const next = button("Next", async () => {
      if (index === 1) {
        const mode = selectedMode(card);
        saveDeploymentMode(mode);
      }
      if (index === 2) {
        const mode = localStorage.getItem(MODE_KEY) || selectedMode(card);
        if (mode === "self_hosted") {
          if (serverResult.dataset.connected !== "true") throw new Error("Connect MIRROR before continuing.");
        } else if (!cloudConnected()) {
          throw new Error("Connect Google or Microsoft before continuing. MIRA does not have a chat-only mode.");
        }
      }
      if (index < steps.length - 1) { index += 1; render(); return; }
      localStorage.setItem(KEY, "true");
      localStorage.setItem(LEGACY_KEY, "true");
      const mode = localStorage.getItem(MODE_KEY) || "cloud";
      const hosted = mode === "self_hosted";
      if (hosted && typeof apiBase === "function" && apiBase()) {
        try {
          await apiJson("/v1/settings", {
            method: "PATCH",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ settings: { "deployment.mode": mode, "profile.mode": profileSelect.value, "onboarding.completed": true } })
          });
        } catch (_) { /* connection was verified; settings can retry later */ }
      }
      overlay.remove(); currentOverlay = null;
      announce("MIRA setup is complete on this device.");
    }, true);
    footer.append(back, next);
    card.append(...steps, footer);
    overlay.append(card);
    document.body.append(overlay);
    currentOverlay = overlay;

    function render() {
      steps.forEach((step, i) => step.classList.toggle("active", i === index));
      back.disabled = index === 0;
      next.textContent = index === steps.length - 1 ? "Finish setup" : "Next";
      const mode = selectedMode(card);
      if (index === 2) {
        cloud.hidden = mode === "self_hosted";
        selfHost.hidden = mode !== "self_hosted";
        connection.querySelector(".mira-release-mode-help").textContent = mode === "self_hosted"
          ? "Enter the address of your own MIRROR server."
          : "Choose Google or Microsoft. This account holds the MIRROR data shared with ChatGPT and the app.";
      }
    }
    modes.addEventListener("change", () => { saveDeploymentMode(selectedMode(card)); render(); });
    render();
  }

  function installStyles() {
    if (document.getElementById("miraReleaseOnboardingStyles")) return;
    const style = document.createElement("style");
    style.id = "miraReleaseOnboardingStyles";
    style.textContent = `
      .mira-release-overlay{position:fixed;inset:0;z-index:12000;display:grid;place-items:center;padding:18px;background:rgba(3,8,16,.88);backdrop-filter:blur(16px)}
      .mira-release-dialog{width:min(760px,100%);max-height:92vh;overflow:auto;padding:clamp(20px,4vw,34px);border-radius:28px;border:1px solid rgba(151,177,215,.18);background:linear-gradient(160deg,#0b1422,#07101b 75%);box-shadow:0 30px 100px rgba(0,0,0,.55)}
      .mira-release-brand{width:min(430px,100%);height:auto;margin-bottom:18px}.mira-release-step{display:none;gap:15px}.mira-release-step.active{display:grid}.mira-release-step h3{font-size:clamp(1.35rem,4vw,1.75rem);margin:.25rem 0}.mira-release-explain{padding:16px;border-radius:16px;background:rgba(105,167,255,.08);border:1px solid rgba(105,167,255,.2)}
      .mira-release-modes{display:grid;gap:12px}.mira-release-mode{display:grid;grid-template-columns:auto 1fr;gap:13px;align-items:flex-start;padding:16px;border-radius:18px;border:1px solid rgba(150,175,210,.17);background:rgba(255,255,255,.025);cursor:pointer}.mira-release-mode:has(input:checked){border-color:#79f2c0;background:rgba(121,242,192,.07)}.mira-release-mode input{margin-top:4px;transform:scale(1.2)}.mira-release-mode-copy{display:grid;gap:5px}.mira-release-mode-copy strong{font-size:1.05rem}.mira-release-badge{display:inline-block;margin-left:9px;padding:3px 7px;border-radius:99px;font-size:.68rem;text-transform:uppercase;letter-spacing:.08em;background:rgba(121,242,192,.14);color:#9ef6ce}
      .mira-release-provider-panel,.mira-release-selfhost{display:grid;gap:13px}.mira-release-connection-status{padding:12px 14px;border-radius:13px;background:rgba(255,255,255,.04);color:#a9b7ca}.mira-release-connection-status.connected{background:rgba(121,242,192,.08);color:#9ef6ce}.mira-release-connection-status.error{background:rgba(248,113,113,.08);color:#fca5a5}.mira-release-selfhost input{min-height:50px}
      .mira-release-toggles{display:grid;gap:9px}.mira-release-toggle{display:flex;gap:11px;align-items:center;padding:11px 13px;border:1px solid rgba(150,175,210,.13);border-radius:13px}.mira-release-toggle input{width:auto}.mira-release-footer{display:flex;justify-content:space-between;gap:12px;margin-top:24px}.mira-release-footer button{min-width:120px}
    `;
    document.head.append(style);
  }

  // Suppress the legacy engineering wizard. This release wizard owns first boot.
  localStorage.setItem(LEGACY_KEY, "true");
  installStyles();
  if (globalThis.MiraV1) globalThis.MiraV1.showOnboarding = () => show(true);
  document.addEventListener("DOMContentLoaded", () => {
    localStorage.setItem(LEGACY_KEY, "true");
    if (globalThis.MiraV1) globalThis.MiraV1.showOnboarding = () => show(true);
    setTimeout(() => show(false), 90);
  });
  globalThis.MiraReleaseOnboarding = { show, refreshConnection };
})();
