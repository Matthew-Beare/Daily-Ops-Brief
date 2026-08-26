"use strict";

(() => {
  const STATE_KEY = "mira.provider.connection.v3";

  function announce(message, isError = false) {
    const text = String(message || "");
    if (globalThis.MiraActionAudit?.announce) globalThis.MiraActionAudit.announce(text);
    else if (typeof setStatus === "function") setStatus(text);
    if (isError) console.error(text);
  }

  function hostedBase() {
    try {
      const base = typeof apiBase === "function" ? apiBase() : "";
      return String(base || "").startsWith("mira-authority://") ? "" : base;
    } catch (_) { return ""; }
  }

  function renderFriendlyStatus(state = readState()) {
    const host = document.getElementById("miraProviderFriendlyStatus");
    if (!host) return;
    host.classList.remove("connected", "error");
    if (state.status === "connected" && state.mirror_verified === true) {
      host.classList.add("connected");
      host.textContent = state.provider === "microsoft_365"
        ? "Microsoft 365 and MIRROR are connected."
        : "Google and MIRROR are connected.";
    } else if (state.status === "connected") {
      host.textContent = "Account approved. MIRA is opening and verifying MIRROR…";
    } else if (state.status === "release_configuration_missing" || state.status === "error") {
      host.classList.add("error");
      host.textContent = state.error || "Account connection did not finish.";
    } else if (state.status === "connecting") {
      host.textContent = "Waiting for account permission…";
    } else {
      host.textContent = "No cloud account connected yet.";
    }
  }

  function saveState(update) {
    const previous = readState();
    const next = { ...previous, ...update, updated_at: new Date().toISOString() };
    localStorage.setItem(STATE_KEY, JSON.stringify(next));
    renderFriendlyStatus(next);
    document.dispatchEvent(new CustomEvent("mira:provider-state", { detail: next }));
    return next;
  }

  function readState() {
    try { return JSON.parse(localStorage.getItem(STATE_KEY) || "{}"); } catch (_) { return {}; }
  }

  function hostedOAuth(provider, capabilities) {
    const base = hostedBase();
    if (!base) return false;
    const returnTo = `${base.replace(/\/+$/, "")}/`;
    const url = `${base.replace(/\/+$/, "")}/v1/auth/${encodeURIComponent(provider)}/start?return_to=${encodeURIComponent(returnTo)}&capabilities=${encodeURIComponent(capabilities || "identity")}`;
    if (globalThis.MirrorNative?.openExternal) globalThis.MirrorNative.openExternal(url);
    else location.assign(url);
    announce(`Opening ${provider === "google" ? "Google" : "Microsoft"}…`);
    return true;
  }

  function nativeGoogle(capabilities) {
    if (!globalThis.MirrorNative?.authorizeGoogle) return false;
    let requested = String(capabilities || "identity");
    if (requested === "identity") requested = "identity,drive,sheets";
    else {
      const parts = new Set(requested.split(",").map((item) => item.trim()).filter(Boolean));
      parts.add("identity"); parts.add("drive"); parts.add("sheets");
      requested = [...parts].join(",");
    }
    saveState({ provider: "google_workspace", status: "connecting", mirror_verified: false, requested_capabilities: requested, error: null });
    globalThis.MirrorNative.authorizeGoogle(requested);
    announce("Opening Google. Choose the account you want MIRA to use and approve the requested access.");
    return true;
  }

  function managedCloud(provider, capabilities) {
    if (!globalThis.MiraCloudConnect?.start) return false;
    globalThis.MiraCloudConnect.start(provider, capabilities || "identity");
    return true;
  }

  function missingRegistration(provider) {
    const friendly = provider === "google" ? "Google" : "Microsoft";
    const message = `${friendly} connection is missing from this build. That is a MIRA release problem, not your account. This build cannot finish cloud setup until its ${friendly} connection is registered.`;
    announce(message, true);
    saveState({ provider: provider === "google" ? "google_workspace" : "microsoft_365", status: "release_configuration_missing", mirror_verified: false, error: message });
    return false;
  }

  async function connect(provider, capabilities = "identity") {
    try {
      if (provider === "google") {
        if (nativeGoogle(capabilities)) return true;
        if (managedCloud(provider, capabilities)) return true;
        if (hostedOAuth(provider, capabilities)) return true;
        return missingRegistration(provider);
      }
      if (provider === "microsoft") {
        if (managedCloud(provider, capabilities)) return true;
        if (hostedOAuth(provider, capabilities)) return true;
        return missingRegistration(provider);
      }
      announce("That account provider is not supported by this MIRA build.", true);
      return false;
    } catch (error) {
      announce(`Could not start account connection: ${error?.message || error}`, true);
      return false;
    }
  }

  function isCloudConnected() {
    const state = readState();
    return state.status === "connected" && state.mirror_verified === true;
  }

  function providerLabel() {
    const state = readState();
    if (!isCloudConnected()) return "Not connected";
    return state.provider === "microsoft_365" ? "Microsoft 365 connected" : "Google connected";
  }

  globalThis.onMirrorNativeGoogleAuthResult = function onGoogleAuthResult(payloadJson) {
    try {
      const payload = typeof payloadJson === "string" ? JSON.parse(payloadJson) : payloadJson;
      if (!payload?.connected) throw new Error("Google did not complete authorization.");
      const authorized = saveState({
        provider: "google_workspace",
        status: "connected",
        mirror_verified: false,
        granted_scopes: payload.granted_scopes || [],
        token_expires_at: payload.expires_at || null,
        error: null
      });
      announce("Google approved access. MIRA is verifying MIRROR before setup is marked complete.");
      Promise.resolve(globalThis.MiraGoogleAuthority?.bootstrap?.(true))
        .then(async () => {
          const connected = saveState({ ...authorized, status: "connected", mirror_verified: true, error: null });
          announce("Google and MIRROR are connected and verified.");
          globalThis.MiraReleaseOnboarding?.refreshConnection?.(connected);
          if (typeof initializeData === "function") await initializeData();
          globalThis.MiraShell?.refreshHome?.().catch(() => {});
        })
        .catch((error) => {
          const failed = saveState({ ...authorized, status: "error", mirror_verified: false, error: `Google connected, but MIRROR could not be verified: ${error?.message || error}` });
          announce(failed.error, true);
          globalThis.MiraReleaseOnboarding?.refreshConnection?.(failed);
        });
    } catch (error) {
      globalThis.onMirrorNativeGoogleAuthError(error?.message || String(error));
    }
  };

  globalThis.onMirrorNativeGoogleAuthError = function onGoogleAuthError(message) {
    saveState({ provider: "google_workspace", status: "error", mirror_verified: false, error: String(message || "Google connection failed") });
    announce(`Google connection did not finish: ${message || "unknown error"}`, true);
    globalThis.MiraReleaseOnboarding?.refreshConnection?.(readState());
  };

  document.addEventListener("DOMContentLoaded", () => renderFriendlyStatus(readState()));
  globalThis.connectProvider = (provider, capabilities) => connect(provider, capabilities);
  globalThis.MiraProviderConnect = { connect, state: readState, isCloudConnected, providerLabel, renderFriendlyStatus };
})();