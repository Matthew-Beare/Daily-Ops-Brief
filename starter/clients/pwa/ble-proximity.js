"use strict";

(() => {
  const observations = new Map();

  function proximityLabel(rssi) {
    if (rssi >= -50) return "very close";
    if (rssi >= -65) return "close";
    if (rssi >= -78) return "nearby";
    return "farther away";
  }

  function render() {
    const host = document.getElementById("miraBleResults");
    if (!host) return;
    host.replaceChildren();
    const rows = [...observations.values()].sort((a, b) => Number(b.rssi || -999) - Number(a.rssi || -999));
    if (!rows.length) {
      host.textContent = "No BLE advertisements seen yet.";
      return;
    }
    for (const item of rows) {
      const row = document.createElement("div");
      row.className = "mira-list-item";
      const title = document.createElement("strong");
      title.textContent = item.name || item.stable_identifier_hint || item.address || "BLE device";
      const detail = document.createElement("small");
      detail.textContent = `${item.rssi} dBm • ${proximityLabel(Number(item.rssi))}${item.stable_identifier_hint ? " • stable advertised identity available" : " • address may rotate"}`;
      row.append(title, detail);
      if (item.stable_identifier_hint) {
        const bind = document.createElement("button");
        bind.textContent = "Bind advertised ID to selected asset";
        bind.addEventListener("click", async () => {
          try {
            if (!state.selectedAsset) throw new Error("Select an asset first, then bind the BLE tag.");
            const result = await apiJson("/v1/rfid/tags/bind", {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({
                asset_uuid: state.selectedAsset.uuid,
                protocol: "ble_advertisement",
                tag_id: item.stable_identifier_hint,
                metadata: { last_address: item.address, last_rssi: item.rssi, name: item.name || null },
              }),
            });
            setStatus(`BLE advertised identity bound to ${state.selectedAsset.name} (${result.asset_uuid}).`);
            await selectAsset(state.selectedAsset.uuid);
          } catch (error) { showError(error); }
        });
        row.append(bind);
      }
      host.append(row);
    }
  }

  function installCard() {
    const panel = document.getElementById("panel-integrations");
    if (!panel || document.getElementById("miraBleCard")) return;
    const card = document.createElement("div");
    card.className = "card wide";
    card.id = "miraBleCard";
    const h2 = document.createElement("h2");
    h2.textContent = "BLE proximity finder";
    const info = document.createElement("div");
    info.className = "mira-callout";
    info.textContent = "Android can rank nearby BLE tags by signal strength for a warmer/colder search. RSSI is not a tape measure. MIRA only offers asset binding when the advertisement contains a stable service/manufacturer identity; rotating Bluetooth addresses are not treated as permanent asset identity.";
    const actions = document.createElement("div");
    actions.className = "actions";
    const start = document.createElement("button");
    start.className = "primary-action";
    start.textContent = "Scan BLE tags for 10 seconds";
    start.disabled = !globalThis.MirrorNative?.scanBleTags;
    if (start.disabled) start.title = "BLE proximity scanning currently uses the native Android companion.";
    start.addEventListener("click", () => {
      observations.clear(); render(); globalThis.MirrorNative.scanBleTags();
    });
    const stop = document.createElement("button");
    stop.textContent = "Stop scan";
    stop.disabled = !globalThis.MirrorNative?.stopBleTags;
    stop.addEventListener("click", () => globalThis.MirrorNative.stopBleTags());
    actions.append(start, stop);
    const status = document.createElement("p"); status.id = "miraBleStatus"; status.className = "muted"; status.textContent = "Idle.";
    const results = document.createElement("div"); results.id = "miraBleResults"; results.className = "mira-list";
    card.append(h2, info, actions, status, results);
    panel.append(card);
    render();
  }

  globalThis.onMirrorNativeBleObservation = (raw) => {
    try {
      const item = typeof raw === "string" ? JSON.parse(raw) : raw;
      const key = item.stable_identifier_hint || item.address;
      if (!key) return;
      observations.set(key, item);
      render();
    } catch (_) { }
  };
  globalThis.onMirrorNativeBleState = (message) => {
    const host = document.getElementById("miraBleStatus"); if (host) host.textContent = message;
  };
  globalThis.onMirrorNativeBleError = (message) => {
    const host = document.getElementById("miraBleStatus"); if (host) host.textContent = message;
    showError(new Error(message));
  };

  const observer = new MutationObserver(installCard);
  observer.observe(document.documentElement, { childList: true, subtree: true });
  installCard();
})();
