"use strict";

(() => {
  function syncNativeKiosk() {
    if (!globalThis.MirrorNative?.setWallDisplay) return;
    try { globalThis.MirrorNative.setWallDisplay(document.documentElement.classList.contains("mira-kiosk")); }
    catch (error) { globalThis.MiraActionAudit?.announce?.(`Android wall display could not change: ${error?.message || error}`); }
  }

  const observer = new MutationObserver((mutations) => {
    if (mutations.some((mutation) => mutation.type === "attributes" && mutation.attributeName === "class")) syncNativeKiosk();
  });
  observer.observe(document.documentElement, { attributes: true, attributeFilter: ["class"] });
  document.addEventListener("DOMContentLoaded", syncNativeKiosk);
  document.addEventListener("visibilitychange", () => { if (!document.hidden) syncNativeKiosk(); });
  globalThis.MiraNativeKioskBridge = { sync: syncNativeKiosk };
})();
