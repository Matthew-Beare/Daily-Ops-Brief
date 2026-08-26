"use strict";

(() => {
  const LOCAL_ONBOARDING_KEY = "mira.onboarding.1.0.completed";
  const ALL_SURFACES = ["web", "windows", "linux", "android"];

  function node(tag, attrs = {}, children = []) {
    const item = document.createElement(tag);
    Object.entries(attrs).forEach(([key, value]) => {
      if (key === "text") item.textContent = value;
      else if (key === "class") item.className = value;
      else if (key === "html") item.innerHTML = value;
      else if (["checked", "disabled", "hidden"].includes(key)) item[key] = Boolean(value);
      else item.setAttribute(key, value);
    });
    children.forEach((child) => item.append(child));
    return item;
  }

  function currentPlatform() {
    if (globalThis.MirrorNative) return "android";
    const ua = navigator.userAgent.toLowerCase();
    if (ua.includes("windows")) return "windows";
    if (ua.includes("linux")) return "linux";
    return "web";
  }

  function openExternal(url) {
    if (!url) return;
    if (globalThis.MirrorNative?.openExternal) globalThis.MirrorNative.openExternal(url);
    else window.open(url, "_blank", "noopener");
  }

  function tutorialGraphic(src, alt) {
    return node("img", { src, alt, class: "mira-v1-tutorial" });
  }

  function installBranding() {
    document.title = "MIRA // MIRROR 1.0";
    const heading = document.querySelector("header h1");
    const subtitle = document.querySelector("header p");
    if (heading) heading.textContent = "MIRA // MIRROR";
    if (subtitle) subtitle.textContent = "Reflecting reality. • 1.0 Pilot";
    if (!document.getElementById("miraV1Styles")) {
      const style = node("style", { id: "miraV1Styles" });
      style.textContent = `
        header h1::after{content:"  •  Reflecting reality" !important}
        .mira-v1-overlay{position:fixed;inset:0;z-index:9999;background:rgba(5,8,14,.82);backdrop-filter:blur(14px);display:grid;place-items:center;padding:18px}
        .mira-v1-dialog{width:min(820px,100%);max-height:92vh;overflow:auto;border:1px solid rgba(255,255,255,.14);border-radius:24px;padding:24px;background:#10141d;color:#f7f9fc;box-shadow:0 30px 90px rgba(0,0,0,.55)}
        .mira-v1-dialog h2{font-size:1.55rem;margin-bottom:.35rem}.mira-v1-dialog h3{margin:.4rem 0}.mira-v1-dialog .step{display:none}.mira-v1-dialog .step.active{display:grid;gap:14px}
        .mira-v1-choice{display:flex;gap:10px;align-items:center;padding:12px;border:1px solid rgba(255,255,255,.12);border-radius:12px}.mira-v1-choice input{width:auto}
        .mira-v1-footer{display:flex;justify-content:space-between;gap:10px;margin-top:18px}.mira-v1-brand{font-size:.78rem;letter-spacing:.14em;text-transform:uppercase;opacity:.65}
        .mira-v1-feature-default{padding:10px 12px;border-radius:10px;background:rgba(74,222,128,.08);border:1px solid rgba(74,222,128,.24);font-size:.9rem}
        .mira-v1-update{position:fixed;right:16px;bottom:16px;z-index:5000;width:min(390px,calc(100vw - 32px));padding:14px;border-radius:16px;background:#111827;color:#f9fafb;border:1px solid rgba(255,255,255,.16);box-shadow:0 18px 55px rgba(0,0,0,.45)}
        .mira-v1-update[hidden]{display:none}.mira-v1-update .actions{margin-top:10px}.mira-v1-settings-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:10px}.mira-v1-settings-grid label{padding:10px;border:1px solid color-mix(in srgb, CanvasText 14%, transparent);border-radius:10px}
        .mira-v1-tutorial{width:100%;height:auto;border-radius:16px;border:1px solid rgba(148,163,184,.18);background:#0b0f17}
        .mira-v1-identity-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:12px}.mira-v1-identity-box{padding:12px;border:1px solid color-mix(in srgb, CanvasText 14%, transparent);border-radius:12px}
      `;
      document.head.append(style);
    }
  }

  function enforceFeatureStudioDefaults() {
    document.querySelectorAll(".mira-checkboxes").forEach((checks) => {
      const replacement = node("div", {
        class: "mira-v1-feature-default",
        text: "Every feature targets web, Windows, Linux and Android automatically. Platform-specific exceptions are an engineering decision, not a setup checkbox."
      });
      checks.replaceWith(replacement);
    });
  }

  async function patchSettings(settings) {
    return apiJson("/v1/settings", {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ settings }),
    });
  }

  function settingCheckbox(key, label, value) {
    const input = node("input", { type: "checkbox", "data-setting": key });
    input.checked = Boolean(value);
    return node("label", { class: "mira-v1-choice" }, [input, node("span", { text: label })]);
  }

  async function loadSettingsIntoPanel() {
    const host = document.getElementById("miraV1SettingsGrid");
    if (!host || !apiBase()) return;
    const result = await apiJson("/v1/settings");
    const settings = result.settings || {};
    host.replaceChildren(
      settingCheckbox("providers.google", "Google Workspace", settings["providers.google"]),
      settingCheckbox("providers.microsoft", "Microsoft 365", settings["providers.microsoft"]),
      settingCheckbox("source_control.enabled", "GitHub source control for custom code", settings["source_control.enabled"]),
      settingCheckbox("updates.safe_automatic", "Safe automatic updates", settings["updates.safe_automatic"]),
      settingCheckbox("features.inventory", "Inventory", settings["features.inventory"]),
      settingCheckbox("features.receipts", "Receipt capture", settings["features.receipts"]),
      settingCheckbox("features.orders", "Order tracking", settings["features.orders"]),
      settingCheckbox("features.home_assistant", "Home Assistant", settings["features.home_assistant"]),
      settingCheckbox("features.rfid_nfc", "RFID / NFC", settings["features.rfid_nfc"]),
      settingCheckbox("features.ble_proximity", "BLE proximity", settings["features.ble_proximity"]),
      settingCheckbox("features.uwb_ranging", "UWB precise ranging", settings["features.uwb_ranging"]),
      settingCheckbox("notifications.spoken_reminders", "Spoken reminders", settings["notifications.spoken_reminders"])
    );
  }

  async function saveSettingsPanel() {
    const values = {};
    document.querySelectorAll("#miraV1SettingsGrid [data-setting]").forEach((input) => { values[input.dataset.setting] = input.checked; });
    await patchSettings(values);
    setStatus("Settings saved to MIRROR. ChatGPT and attached clients use the same settings authority for this deployment.");
  }

  function buildSettingsPanel() {
    const nav = document.querySelector("header nav");
    if (!nav || nav.querySelector("[data-tab='setup']")) return;
    const tab = node("button", { "data-tab": "setup", "aria-selected": "false", text: "Setup & Settings" });
    tab.addEventListener("click", () => switchTab("setup"));
    nav.append(tab);

    const panel = node("section", { id: "panel-setup", class: "panel" });
    const intro = node("div", { class: "card wide" }, [
      node("h2", { text: "MIRA // MIRROR 1.0" }),
      node("div", { class: "mira-callout", text: "Stock MIRA can run in ChatGPT with Google Workspace only. A Linux/Docker MIRROR server is an optional deployment, not a normal-user requirement." }),
      node("div", { id: "miraV1SettingsGrid", class: "mira-v1-settings-grid" }),
    ]);
    const save = node("button", { class: "primary-action", text: "Save settings" });
    save.addEventListener("click", () => saveSettingsPanel().catch(showError));
    intro.append(save);

    const source = node("div", { class: "card" }, [
      node("h2", { text: "GitHub for custom source" }),
      node("p", { class: "muted", text: "You do not need GitHub for stock inventory, receipts, Google or settings. Git becomes necessary only when Feature Studio creates executable/custom source that must survive upgrades." }),
      tutorialGraphic("tutorial-github.svg", "GitHub is optional until custom source is first needed")
    ]);
    const create = node("button", { text: "Create GitHub account" });
    create.addEventListener("click", () => openExternal("https://github.com/signup"));
    const connect = node("button", { text: "Connect GitHub" });
    connect.addEventListener("click", async () => {
      try {
        const result = await apiJson("/v1/integrations/github/status");
        if (result.install_url) openExternal(result.install_url);
        else setStatus("The MIRA GitHub App installation URL has not been configured for this hosted MIRROR deployment yet.");
      } catch (error) { showError(error); }
    });
    source.append(node("div", { class: "actions" }, [create, connect]));

    const updates = node("div", { class: "card" }, [
      node("h2", { text: "Updates" }),
      node("p", { class: "muted", text: "Safe updates are automatic by default. Custom-source collisions pause the update and get a plain-language conflict report instead of overwriting user work." }),
      tutorialGraphic("tutorial-conflict.svg", "MIRA update conflict recovery flow")
    ]);
    const check = node("button", { text: "Check for update" });
    check.addEventListener("click", () => checkForUpdates(true).catch(showError));
    updates.append(check);

    const rerunSetup = node("div", { class: "card" }, [node("h2", { text: "Guided setup" }), node("p", { class: "muted", text: "Run the first-use walkthrough again at any time." })]);
    const rerun = node("button", { text: "Run setup walkthrough" });
    rerun.addEventListener("click", () => showOnboarding(true));
    rerunSetup.append(rerun);

    panel.append(intro, source, updates, rerunSetup);
    document.querySelector("main")?.append(panel);
  }

  function wizardStep(title, text, body = []) {
    return node("div", { class: "step" }, [node("h3", { text: title }), node("p", { class: "muted", text }), ...body]);
  }

  function providerButton(text, provider, capabilities) {
    const button = node("button", { text });
    button.addEventListener("click", () => connectProvider(provider, capabilities));
    return button;
  }

  function showOnboarding(force = false) {
    if (!force && localStorage.getItem(LOCAL_ONBOARDING_KEY) === "true") return;
    if (document.getElementById("miraV1Onboarding")) return;

    const overlay = node("div", { id: "miraV1Onboarding", class: "mira-v1-overlay" });
    const dialog = node("div", { class: "mira-v1-dialog" });
    dialog.append(node("div", { class: "mira-v1-brand", text: "MIRA // MIRROR 1.0" }), node("h2", { text: "Set up MIRA" }), node("p", { text: "A guided setup for normal humans. Everything can be changed later in Setup & Settings." }));

    const mode = node("select", { id: "onboardMode" });
    [["personal","Personal"],["family","Family"],["institutional-pilot","Institutional pilot"]].forEach(([value,label]) => mode.add(new Option(label, value)));

    const googleButtons = node("div", { class: "actions" }, [
      providerButton("Continue with Google", "google", "identity"),
      providerButton("Enable Drive + Sheets + Calendar", "google", "drive,sheets,calendar"),
      providerButton("Enable Gmail receipt/order reading", "google", "gmail_read"),
    ]);

    const githubButtons = node("div", { class: "actions" });
    const signup = node("button", { text: "Create GitHub account" });
    signup.addEventListener("click", () => openExternal("https://github.com/signup"));
    const skipGithub = node("span", { class: "muted", text: "No custom source yet? Skip this. MIRA will bring you back when Git is actually needed." });
    githubButtons.append(signup, skipGithub);

    const steps = [
      wizardStep("Welcome", "MIRA is the assistant. MIRROR is the reality layer that keeps identity, evidence, settings and provenance consistent."),
      wizardStep("Use MIRA in ChatGPT", "The recommended stock setup is ChatGPT + your connected Google Workspace. You do not need Linux, Docker, a server or an OpenAI API key. The standalone MIRROR service is optional for native/offline/self-hosted deployments.", [tutorialGraphic("tutorial-google.svg", "ChatGPT and Google-native MIRA setup")]),
      wizardStep("Connect Google", "Start with Google identity, then enable only the Google surfaces you want. Drive stores reality/evidence; Gmail powers user-approved receipt/order workflows; Calendar powers appointments. The actual permission screen is Google's real authorization page.", [tutorialGraphic("tutorial-google.svg", "Google permission walkthrough"), googleButtons]),
      wizardStep("Choose your profile", "This sets sensible defaults; it does not lock you into a mode.", [mode]),
      wizardStep("Choose capabilities", "Turn on only what you intend to use. You can enable the rest later.", [
        settingCheckbox("features.rfid_nfc", "RFID / NFC inventory", false),
        settingCheckbox("features.home_assistant", "Home Assistant", false),
        settingCheckbox("features.ble_proximity", "BLE proximity tracking", false),
        settingCheckbox("features.uwb_ranging", "UWB precise ranging", false),
        settingCheckbox("notifications.spoken_reminders", "Spoken reminders", true),
      ]),
      wizardStep("Understand inventory identity", "Every physical thing gets one immutable UUID. Serial numbers, retailer SKUs, UPC/GTIN, model/part numbers, QR labels, NFC/HF tags, UHF EPC tags and BLE identities are aliases that can change without changing the asset.", [
        node("div", { class: "mira-v1-identity-grid" }, [
          node("div", { class: "mira-v1-identity-box", html: "<strong>Phone-readable</strong><br><span class='muted'>QR/barcode, camera, NFC/HF tag</span>" }),
          node("div", { class: "mira-v1-identity-box", html: "<strong>External reader</strong><br><span class='muted'>UHF EPC Gen2 / other RFID hardware</span>" }),
          node("div", { class: "mira-v1-identity-box", html: "<strong>Typed identity</strong><br><span class='muted'>serial, MPN, model, retailer SKU</span>" })
        ])
      ]),
      wizardStep("Organize locations", "A tote, case or bin can be both a physical asset and a location. Items inside point to the tote; moving the tote changes its parent shelf, so the full location path follows automatically.", [tutorialGraphic("tutorial-hierarchy.svg", "Hierarchical shelf and tote location example")]),
      wizardStep("GitHub only when needed", "Stock MIRA does not require GitHub. If Feature Studio creates executable/custom source, MIRA explains Git, opens signup if needed, and then requests scoped repository access.", [tutorialGraphic("tutorial-github.svg", "GitHub optional custom-source setup"), githubButtons]),
      wizardStep("Updates protect your custom work", "Clean updates reconcile automatically. If upstream MIRA and your custom source change the same thing incompatibly, the update pauses, keeps your current version intact, and walks you through the decision in plain English.", [tutorialGraphic("tutorial-conflict.svg", "Update conflict recovery")]),
      wizardStep("Ready", "Use Inventory to add/query things, Scan to bind codes or move items, Files & photos for evidence, Receipts for purchase reconciliation, Feature Studio to extend MIRA, and Setup & Settings whenever you want to change options."),
    ];

    steps.forEach((step) => dialog.append(step));
    let index = 0;
    const back = node("button", { text: "Back" });
    const next = node("button", { class: "primary-action", text: "Next" });
    const render = () => { steps.forEach((step,i)=>step.classList.toggle("active", i===index)); back.disabled=index===0; next.textContent=index===steps.length-1?"Finish setup":"Next"; };
    back.addEventListener("click",()=>{ if(index>0){index-=1;render();} });
    next.addEventListener("click", async () => {
      if (index < steps.length - 1) { index += 1; render(); return; }
      localStorage.setItem(LOCAL_ONBOARDING_KEY, "true");
      if (apiBase()) {
        const updates = { "profile.mode": mode.value, "onboarding.completed": true };
        dialog.querySelectorAll("[data-setting]").forEach((input)=>{ updates[input.dataset.setting]=input.checked; });
        try { await patchSettings(updates); await apiJson("/v1/onboarding/complete", { method: "POST" }); } catch (_) { /* local completion is retained and sync can occur later */ }
      }
      overlay.remove();
      loadSettingsIntoPanel().catch(()=>{});
    });
    dialog.append(node("div", { class: "mira-v1-footer" }, [back,next]));
    overlay.append(dialog); document.body.append(overlay); render();
  }

  function installNfcEnrollment() {
    const observer = new MutationObserver(() => {
      const input = document.getElementById("rfidTagId");
      if (!input || document.getElementById("scanNfcTag")) return;
      const button = node("button", { id: "scanNfcTag", text: "Tap NFC tag with this phone" });
      button.disabled = !globalThis.MirrorNative?.scanNfcTag;
      button.title = button.disabled ? "Native Android NFC is required for tap enrollment." : "Read the physical NFC/HF tag UID and bind it to the selected asset.";
      button.addEventListener("click", () => globalThis.MirrorNative.scanNfcTag());
      input.parentElement?.append(button);
    });
    observer.observe(document.documentElement, { childList: true, subtree: true });
    globalThis.onMirrorNativeNfcResult = async (uid, technologies) => {
      try {
        if (!state.selectedAsset) throw new Error("Select the asset first, then tap its NFC tag.");
        const result = await apiJson("/v1/rfid/tags/bind", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ asset_uuid: state.selectedAsset.uuid, protocol: "nfc_uid", tag_id: uid, metadata: { technologies } }),
        });
        const input = document.getElementById("rfidTagId"); if (input) input.value = uid;
        setStatus(`NFC tag ${result.tag_value} enrolled to ${state.selectedAsset.name} (${state.selectedAsset.uuid}).`);
        await selectAsset(state.selectedAsset.uuid);
      } catch (error) { showError(error); }
    };
    globalThis.onMirrorNativeNfcError = (message) => showError(new Error(message));
  }

  function installAssetIdentityTools() {
    const observer = new MutationObserver(() => {
      if (document.getElementById("miraIdentityTools")) return;
      const assetResult = document.getElementById("assetResult");
      const host = assetResult?.closest(".card");
      if (!host) return;

      const box = node("div", { id: "miraIdentityTools", class: "row" });
      box.append(node("h3", { text: "Identity & physical container" }));
      const serialRow = node("div", { class: "split" });
      const serial = node("input", { id: "miraSerial", placeholder: "Serial number" });
      const manufacturer = node("input", { id: "miraSerialManufacturer", placeholder: "Manufacturer (optional)" });
      serialRow.append(serial, manufacturer);
      const actions = node("div", { class: "actions" });
      const addSerial = node("button", { text: "Add serial number" });
      addSerial.addEventListener("click", async () => {
        try {
          if (!state.selectedAsset) throw new Error("Select an asset first.");
          const value = serial.value.trim(); if (!value) throw new Error("Enter the serial number.");
          await apiJson(`/v1/assets/${encodeURIComponent(state.selectedAsset.uuid)}/serials`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ serial: value, manufacturer: manufacturer.value.trim() }) });
          serial.value = ""; await selectAsset(state.selectedAsset.uuid); setStatus("Serial number bound to the immutable asset UUID.");
        } catch (error) { showError(error); }
      });
      const makeContainer = node("button", { text: "Make this a container location" });
      makeContainer.addEventListener("click", async () => {
        try {
          if (!state.selectedAsset) throw new Error("Select the tote/bin/case asset first.");
          const result = await apiJson(`/v1/assets/${encodeURIComponent(state.selectedAsset.uuid)}/container-location`, { method: "POST", headers: { "Content-Type": "application/json" }, body: "{}" });
          setStatus(`${state.selectedAsset.name} is now also a location. Resolved path: ${(result.path || []).map((item) => item.name).join(" > ")}`);
        } catch (error) { showError(error); }
      });
      const where = node("button", { text: "Where is this?" });
      const whereResult = node("div", { id: "miraWhereResult", class: "mira-callout", text: "Select an asset, then ask where it is." });
      where.addEventListener("click", async () => {
        try {
          if (!state.selectedAsset) throw new Error("Select an asset first.");
          const result = await apiJson(`/v1/assets/${encodeURIComponent(state.selectedAsset.uuid)}/where`);
          whereResult.textContent = result.display_path ? `${result.asset_name}: ${result.display_path}` : `${result.asset_name}: no location assigned yet.`;
        } catch (error) { showError(error); }
      });
      actions.append(addSerial, makeContainer, where);
      box.append(serialRow, actions, whereResult);
      host.insertBefore(box, assetResult);
    });
    observer.observe(document.documentElement, { childList: true, subtree: true });
  }

  function installLocationMoveFlow() {
    const originalNativeScan = globalThis.onMirrorNativeScanResult;
    globalThis.onMirrorNativeScanResult = (value, symbology) => {
      const raw = String(value || "").trim();
      if (!raw.toUpperCase().startsWith("MIRROR:LOCATION:")) return originalNativeScan?.(value, symbology);
      (async () => {
        if (!state.selectedAsset) throw new Error("Select or scan the asset first, then scan the location.");
        const result = await apiJson(`/v1/locations/resolve-code?value=${encodeURIComponent(raw)}`);
        const moved = await mutate("inventory.asset.relocate", { asset_uuid: state.selectedAsset.uuid, location_uuid: result.location.uuid });
        renderSelected(moved.asset); await loadAssets();
        const where = await apiJson(`/v1/assets/${encodeURIComponent(moved.asset.uuid)}/where`).catch(() => null);
        setStatus(`Moved ${moved.asset.name} to ${where?.display_path || result.location.name}.`);
      })().catch(showError);
    };
  }

  async function checkForUpdates(showNoUpdate = false) {
    if (!apiBase()) return;
    const result = await apiJson(`/v1/updates/status?client_version=${encodeURIComponent(CLIENT_VERSION)}&platform=${encodeURIComponent(currentPlatform())}`);
    const banner = document.getElementById("miraV1UpdateBanner");
    if (!banner) return;
    if (result.update_available) {
      banner.hidden = false;
      banner.querySelector("strong").textContent = `MIRA ${result.latest_version} is ready`;
      banner.querySelector("p").textContent = "This release is newer than the installed client. Safe source reconciliation happens before custom features are replaced.";
      banner.dataset.releaseUrl = result.release_url || "";
    } else {
      banner.hidden = true;
      if (showNoUpdate) setStatus(result.error || `MIRA ${CLIENT_VERSION} is current for the configured release channel.`);
    }
  }

  function installUpdateHandling() {
    const banner = node("div", { id: "miraV1UpdateBanner", class: "mira-v1-update", hidden: true }, [
      node("strong", { text: "MIRA update available" }),
      node("p", { text: "A newer release is available." }),
    ]);
    const install = node("button", { class: "primary-action", text: "Update MIRA" });
    install.addEventListener("click", () => openExternal(banner.dataset.releaseUrl));
    const later = node("button", { text: "Later" }); later.addEventListener("click",()=>{ banner.hidden=true; });
    banner.append(node("div", { class: "actions" }, [install,later])); document.body.append(banner);

    const original = authorizedFetch;
    authorizedFetch = async function v1AuthorizedFetch(url, options = {}) {
      const response = await original(url, options);
      if (response.status === 426) {
        banner.hidden = false;
        banner.querySelector("strong").textContent = "MIRA needs an update";
        banner.querySelector("p").textContent = "This MIRROR authority requires a newer client. MIRA will open the verified update/reconciliation flow before changing data.";
        checkForUpdates(false).catch(()=>{});
      }
      return response;
    };
    setTimeout(() => checkForUpdates(false).catch(()=>{}), 2500);
    setInterval(() => checkForUpdates(false).catch(()=>{}), 6 * 60 * 60 * 1000);
  }

  function initializeV1() {
    installBranding();
    buildSettingsPanel();
    installNfcEnrollment();
    installAssetIdentityTools();
    installLocationMoveFlow();
    installUpdateHandling();
    const featureObserver = new MutationObserver(enforceFeatureStudioDefaults);
    featureObserver.observe(document.documentElement, { childList: true, subtree: true });
    enforceFeatureStudioDefaults();
    loadSettingsIntoPanel().catch(()=>{});
    setTimeout(() => showOnboarding(false), 450);
  }

  document.addEventListener("DOMContentLoaded", initializeV1);
  globalThis.MiraV1 = { showOnboarding: () => showOnboarding(true), checkForUpdates, supportedSurfaces: ALL_SURFACES };
})();
