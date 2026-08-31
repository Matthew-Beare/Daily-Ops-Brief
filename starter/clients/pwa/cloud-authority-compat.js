"use strict";

(() => {
  const MODE_KEY = "mira.deployment.mode.v1";
  const PSEUDO_BASE = "mira-authority://";
  const originalApiBase = typeof apiBase === "function" ? apiBase : null;
  const authorityApiUrl = typeof apiUrl === "function" ? apiUrl : null;
  const originalInitializeData = typeof initializeData === "function" ? initializeData : null;

  function mode() { return localStorage.getItem(MODE_KEY) || "cloud"; }
  function cloudMode() { return mode() === "cloud" || mode() === "cloud_local"; }
  function cloudConnected() { return globalThis.MiraProviderConnect?.isCloudConnected?.() === true; }

  if (originalApiBase) {
    apiBase = function mirrorAuthorityBase() {
      if (cloudMode()) return PSEUDO_BASE;
      return originalApiBase();
    };
  }

  if (authorityApiUrl) {
    apiUrl = function mirrorAuthorityUrl(path) {
      if (cloudMode()) return `mira-authority://${String(path || "").replace(/^\//, "")}`;
      return authorityApiUrl(path);
    };
  }

  if (originalInitializeData) {
    initializeData = async function initializeSelectedAuthority() {
      if (!cloudMode()) return originalInitializeData();
      if (!cloudConnected()) {
        setMutationAllowed(false, "Connect Google or Microsoft before saving. MIRA needs MIRROR to keep your data consistent.");
        return;
      }
      await preflight();
      await Promise.all([loadTree(), loadAssets()]);
      try { globalThis.MiraProviderConnect?.renderFriendlyStatus?.(); } catch (_) { }
    };
  }

  document.addEventListener("mira:provider-state", (event) => {
    if (!cloudMode() || event.detail?.mirror_verified !== true) return;
    Promise.resolve(typeof initializeData === "function" ? initializeData() : null)
      .then(() => globalThis.MiraShell?.refreshHome?.())
      .catch((error) => globalThis.MiraActionAudit?.announce?.(error?.message || String(error)));
  });

  globalThis.MiraAuthorityCompat = { cloudMode, cloudConnected, pseudoBase: PSEUDO_BASE };
})();