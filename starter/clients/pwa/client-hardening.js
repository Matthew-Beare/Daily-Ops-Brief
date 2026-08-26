"use strict";

(() => {
  submitCommand = async function submitReplaySafeCommand(command) {
    if (!state.mutationAllowed && command.command_type !== "capture.barcode_qr_scan") await preflight();
    const response = await authorizedFetch(apiUrl("/v1/commands"), {
      method: "POST",
      headers: { "Content-Type": "application/json", "Idempotency-Key": command.idempotency_key },
      body: JSON.stringify(command),
    });
    const result = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(result.detail || `API returned HTTP ${response.status}.`);
    if (result?.readback_verified === false) throw new Error("Server did not verify canonical readback.");
    return result;
  };

  async function signedResource(resource, ttlSeconds = 300) {
    return apiJson(`/v1/access-link?resource=${encodeURIComponent(resource)}&ttl_seconds=${encodeURIComponent(ttlSeconds)}`);
  }

  renderSelected = function renderSecureSelectedAsset(asset) {
    state.selectedAsset = asset;
    byId("editAssetName").value = asset.name || "";
    byId("editAssetDescription").value = asset.description || "";
    byId("editAssetCategory").value = asset.category_uuid || "";
    byId("editAssetLocation").value = asset.location_uuid || "";
    byId("editAssetMetadata").value = JSON.stringify(asset.metadata || {}, null, 2);
    byId("assetResult").textContent = JSON.stringify(asset, null, 2);
    const identifiers = byId("assetIdentifiers"); identifiers.replaceChildren();
    (asset.identifiers || []).forEach((row) => { const span=document.createElement("span"); span.className="pill"; span.textContent=`${row.namespace}: ${row.value}`; identifiers.appendChild(span); });
    const evidence = byId("evidenceList"); evidence.replaceChildren();
    (asset.evidence || []).forEach((row) => { const p=document.createElement("p"); const link=document.createElement("a"); link.href="#"; link.textContent=`${row.role}: ${row.filename}`; link.addEventListener("click",(event)=>{event.preventDefault(); signedResource(`evidence:${row.evidence_uuid}`,300).then((result)=>{ if(globalThis.MirrorNative?.openExternal) globalThis.MirrorNative.openExternal(result.url); else window.open(result.url,"_blank","noopener"); }).catch(showError);}); p.appendChild(link); evidence.appendChild(p); });
    const gallery = byId("assetPhotos"); gallery.replaceChildren();
    (asset.photo_evidence || []).forEach((photo) => { const image=document.createElement("img"); image.alt=photo.filename||photo.media_role||"Item photo"; image.loading="lazy"; gallery.appendChild(image); signedResource(`evidence:${photo.evidence_uuid}`,900).then((result)=>{image.src=result.url;}).catch(()=>{image.alt=`${image.alt} (preview unavailable)`;}); });
  };

  printLabel = function printProtectedLabel(kind) {
    if (!state.selectedAsset) { showError(new Error("Select an item first.")); return; }
    signedResource(`label:${state.selectedAsset.uuid}:${kind}`,300).then((result)=>{ if(globalThis.MirrorNative?.openExternal) globalThis.MirrorNative.openExternal(result.url); else window.open(result.url,"_blank","noopener"); }).catch(showError);
  };

  loadProviders = async function loadProviderReadiness() {
    const configured = await apiJson("/v1/auth/providers");
    let health = null; try { health = await apiJson("/v1/integrations/provider-health"); } catch (error) { health={error:error.message}; }
    byId("providerStatus").textContent = JSON.stringify({configured,health},null,2);
  };

  function loadScriptOnce(src, datasetKey, onload = null) {
    if (document.querySelector(`script[data-${datasetKey}]`)) { if (onload) onload(); return; }
    const script=document.createElement("script"); script.src=src; script.setAttribute(`data-${datasetKey}`,"true"); if (onload) script.onload=onload; document.head.append(script);
  }

  function loadStyleOnce(href, datasetKey) {
    if (document.querySelector(`link[data-${datasetKey}]`)) return;
    const css=document.createElement("link"); css.rel="stylesheet"; css.href=href; css.setAttribute(`data-${datasetKey}`,"true"); document.head.append(css);
  }

  function loadCommercialShell() {
    loadStyleOnce("commercial.css","mira-commercial");
    loadStyleOnce("sleek-shell.css","mira-sleek-shell");
    loadScriptOnce("platform-ui.js","mira-platform-ui",()=>globalThis.MirrorPlatformUI?.initialize());
    loadScriptOnce("smart-capture.js","mira-smart-capture");
    loadScriptOnce("guided-migration.js","mira-guided-migration");
    loadScriptOnce("ble-proximity.js","mira-ble-proximity");
    loadScriptOnce("receipt-v1.js","mira-receipt-v1");
    loadScriptOnce("native-updater.js","mira-native-updater");
    loadScriptOnce("integrations-v1.js","mira-integrations-v1");
    loadScriptOnce("sleek-shell.js","mira-sleek-shell-script",()=>globalThis.MiraSleekShell?.initialize());
  }

  document.addEventListener("DOMContentLoaded", loadCommercialShell);
  document.addEventListener("visibilitychange",()=>{ if(!document.hidden&&apiBase()) { loadProviders().catch(()=>{}); globalThis.MiraSleekShell?.refreshHome?.().catch(()=>{}); } });
})();
