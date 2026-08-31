"use strict";

(() => {
  const SETUP_MESSAGE = "Finish setup first so MIRA knows where your MIRROR data lives.";
  const MODE_KEY = "mira.deployment.mode.v1";

  function deploymentMode() { return localStorage.getItem(MODE_KEY) || "cloud"; }
  function currentApiBase() { try { return typeof apiBase === "function" ? apiBase() : ""; } catch (_) { return ""; } }
  function cloudMode() { const mode = deploymentMode(); return mode === "cloud" || mode === "cloud_local"; }
  function cloudConnected() { return globalThis.MiraProviderConnect?.isCloudConnected?.() === true; }
  function selfHostedConnected() { const base = currentApiBase(); return Boolean(base && !String(base).startsWith("mira-authority://")); }
  function hasAuthorityConnection() { return cloudMode() ? cloudConnected() : selfHostedConnected(); }

  function friendlyError(error) {
    const raw = error?.message || String(error || "Something went wrong.");
    return raw
      .replace(/No API base URL configured\.?/i, SETUP_MESSAGE)
      .replace(/immutable UUID/gi, "permanent item identity")
      .replace(/\bUUID\b/g, "record ID")
      .replace(/\bJSON\b/g, "advanced data")
      .replace(/canonical authority/gi, "MIRROR data");
  }

  function announce(message) {
    const text = friendlyError(message);
    try { if (typeof setStatus === "function") setStatus(text); } catch (_) { }
    const toast = document.getElementById("miraToast");
    if (toast) {
      toast.textContent = text;
      toast.classList.add("show");
      clearTimeout(toast.__miraTimer);
      toast.__miraTimer = setTimeout(() => toast.classList.remove("show"), 4200);
    }
    return text;
  }

  function openSetup(message = SETUP_MESSAGE) {
    announce(message);
    if (globalThis.MiraReleaseOnboarding?.show) { globalThis.MiraReleaseOnboarding.show(true); return; }
    if (globalThis.MiraV1?.showOnboarding) { globalThis.MiraV1.showOnboarding(); return; }
    if (globalThis.MiraShell?.go && document.getElementById("panel-setup")) { globalThis.MiraShell.go("setup"); return; }
    if (typeof switchTab === "function" && document.getElementById("panel-system")) switchTab("system");
  }

  function applySetupState(allowed, reason = "") {
    const ready = Boolean(allowed) || hasAuthorityConnection();
    if (!ready) {
      document.querySelectorAll("[data-mutation]").forEach((button) => {
        button.disabled = false;
        button.setAttribute("aria-disabled", "true");
        button.dataset.needsSetup = "true";
        button.title = "Finish setup to use this action";
      });
      if (reason) announce(reason);
      return;
    }
    document.querySelectorAll("[data-needs-setup]").forEach((button) => {
      delete button.dataset.needsSetup;
      button.removeAttribute("aria-disabled");
      button.removeAttribute("title");
    });
  }

  if (typeof globalThis.setMutationAllowed === "function") {
    const originalSetMutationAllowed = globalThis.setMutationAllowed;
    globalThis.setMutationAllowed = function auditedMutationState(allowed, reason = "") {
      originalSetMutationAllowed(allowed, reason);
      applySetupState(Boolean(allowed), reason);
    };
  }

  function labelFor(button) { return (button.getAttribute("aria-label") || button.textContent || button.id || "action").trim().replace(/\s+/g, " "); }

  function markButtons(root = document) {
    root.querySelectorAll?.("button").forEach((button, index) => {
      if (!button.type) button.type = button.closest("form") ? "submit" : "button";
      if (!button.dataset.actionAudit) button.dataset.actionAudit = button.id || `${labelFor(button).toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/(^-|-$)/g, "") || "button"}-${index}`;
      if (!hasAuthorityConnection() && button.hasAttribute("data-mutation")) {
        button.disabled = false;
        button.setAttribute("aria-disabled", "true");
        button.dataset.needsSetup = "true";
        button.title = "Finish setup to use this action";
      }
    });
  }

  document.addEventListener("click", (event) => {
    const button = event.target.closest("button");
    if (!button) return;
    const label = labelFor(button);
    const providerAction = /continue with google|connect google|enable drive|enable gmail|use microsoft|connect microsoft|onedrive|add account|calendar access/i.test(label);
    if (providerAction) return;
    if (button.dataset.needsSetup === "true" || (button.hasAttribute("data-mutation") && !hasAuthorityConnection())) {
      event.preventDefault();
      event.stopImmediatePropagation();
      if (cloudMode()) openSetup("Connect Google or Microsoft before saving. MIRA needs MIRROR to keep your data consistent.");
      else openSetup("Connect this device to your self-hosted MIRROR before saving.");
    }
  }, true);

  window.addEventListener("error", (event) => {
    if (!event.error && !event.message) return;
    announce(`That action hit an error: ${friendlyError(event.error || event.message)}`);
  });
  window.addEventListener("unhandledrejection", (event) => announce(`That action did not finish: ${friendlyError(event.reason)}`));
  document.addEventListener("mira:provider-state", () => applySetupState(hasAuthorityConnection()));

  markButtons();
  applySetupState(hasAuthorityConnection(), hasAuthorityConnection() ? "" : SETUP_MESSAGE);
  const observer = new MutationObserver((mutations) => {
    for (const mutation of mutations) mutation.addedNodes.forEach((node) => { if (node.nodeType === Node.ELEMENT_NODE) markButtons(node); });
  });
  observer.observe(document.documentElement, { childList: true, subtree: true });

  globalThis.MiraActionAudit = { announce, openSetup, markButtons, applySetupState, hasAuthorityConnection };
})();