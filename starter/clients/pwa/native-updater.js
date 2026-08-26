"use strict";

(() => {
  function installNativeUpdaterBridge() {
    const invoke = globalThis.__TAURI__?.core?.invoke;
    if (!invoke) return;

    const observer = new MutationObserver(() => {
      const banner = document.getElementById("miraV1UpdateBanner");
      const button = banner?.querySelector("button.primary-action");
      if (!button || button.dataset.nativeUpdater === "true") return;
      button.dataset.nativeUpdater = "true";
      button.textContent = "Update MIRA now";
      button.addEventListener("click", async (event) => {
        event.preventDefault();
        event.stopImmediatePropagation();
        button.disabled = true;
        const previous = button.textContent;
        button.textContent = "Verifying signed update…";
        try {
          const result = await invoke("install_verified_update");
          if (result === "current") {
            setStatus("This signed desktop build is already current.");
            banner.hidden = true;
            button.disabled = false;
            button.textContent = previous;
          }
        } catch (error) {
          button.disabled = false;
          button.textContent = previous;
          showError(new Error(`Signed desktop update could not be installed: ${error}. The current version remains unchanged.`));
        }
      }, true);
    });
    observer.observe(document.documentElement, { childList: true, subtree: true });

    invoke("updater_channel_status").then((status) => {
      if (!status?.configured) setStatus("This desktop build is not attached to a production signed-update channel yet.");
    }).catch(() => {});
  }

  document.addEventListener("DOMContentLoaded", installNativeUpdaterBridge);
})();
