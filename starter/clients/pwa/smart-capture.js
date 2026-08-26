"use strict";

(() => {
  const ASSET_SYMBOLOGIES = new Set(["UPC_A", "EAN_13", "EAN_8"]);
  const LOCATION_PREFIX = "MIRROR:LOCATION:";

  async function relocateFromLocationCode(raw) {
    if (!state.selectedAsset) throw new Error("Select or scan the item first, then scan the location label.");
    const result = await apiJson(`/v1/locations/resolve-code?value=${encodeURIComponent(raw)}`);
    const moved = await mutate("inventory.asset.relocate", {
      asset_uuid: state.selectedAsset.uuid,
      location_uuid: result.location.uuid,
    });
    renderSelected(moved.asset);
    await loadAssets();
    setStatus(`Moved ${moved.asset.name} to ${result.location.name}.`);
    switchTab("inventory");
    return moved.asset;
  }

  function renderLookupCandidate(result, raw, symbology) {
    const host = byId("lastScan");
    if (!host || !state.lastScan || state.lastScan.value !== raw) return;
    if (!result?.found || !result.candidate) {
      const note = document.createElement("span");
      note.className = "muted";
      note.textContent = result?.configured === false
        ? " Product lookup is not configured on this MIRROR server. The scan is still retained and can be assigned manually."
        : " No product candidate was returned. The scan can be assigned manually.";
      host.append(document.createElement("br"), note);
      return;
    }

    const candidate = result.candidate;
    const card = document.createElement("div");
    card.className = "mira-callout";
    const title = document.createElement("strong");
    title.textContent = candidate.name || `Product ${raw}`;
    const detail = document.createElement("div");
    detail.className = "muted";
    detail.textContent = [candidate.brand, candidate.category, `source: ${result.source}`].filter(Boolean).join(" • ");
    const button = document.createElement("button");
    button.className = "primary-action";
    button.textContent = "Create asset from this suggestion";
    button.addEventListener("click", async () => {
      try {
        if (!state.lastScan || state.lastScan.value !== raw) throw new Error("Scan another code or refresh the candidate.");
        const created = await mutate("inventory.asset.create", {
          name: candidate.name || `Product ${raw}`,
          description: "Created from a product lookup candidate. Verify details before relying on them.",
          category_uuid: null,
          location_uuid: null,
          metadata: {
            product_lookup_source: result.source,
            product_lookup_candidate: candidate,
            product_lookup_gtin: raw,
            product_lookup_verified: false,
          },
        });
        renderSelected(created.asset);
        const assigned = await mutate("inventory.identifier.assign", {
          asset_uuid: created.asset.uuid,
          namespace: String(symbology || "gtin").toLowerCase(),
          value: raw,
        });
        state.lastScan = null;
        renderSelected(assigned.asset);
        await loadAssets();
        host.textContent = `Created ${assigned.asset.name}. Internet product metadata remains marked unverified until confirmed.`;
        setStatus(`Created and tagged ${assigned.asset.name} with immutable UUID ${assigned.asset.uuid}.`);
      } catch (error) { showError(error); }
    });
    card.append(title, detail, button);
    host.append(document.createElement("br"), card);
  }

  async function enrichUnmatched(raw, symbology) {
    if (!ASSET_SYMBOLOGIES.has(String(symbology || "").toUpperCase())) return;
    try {
      const result = await apiJson(`/v1/enrichment/gtin/${encodeURIComponent(raw)}`);
      renderLookupCandidate(result, raw, symbology);
    } catch (error) {
      const host = byId("lastScan");
      if (host && state.lastScan?.value === raw) {
        const note = document.createElement("span");
        note.className = "muted";
        note.textContent = ` Product lookup unavailable: ${error.message}`;
        host.append(document.createElement("br"), note);
      }
    }
  }

  const baseCapture = capture;
  capture = async function smartCapture(rawValue, symbology) {
    const raw = String(rawValue || "").trim();
    if (!raw) return;
    if (raw.toUpperCase().startsWith(LOCATION_PREFIX)) {
      await relocateFromLocationCode(raw);
      byId("scanValue").value = "";
      return;
    }
    await baseCapture(raw, symbology);
    if (state.lastScan?.value === raw) enrichUnmatched(raw, symbology).catch(() => {});
  };
})();
