"use strict";

(() => {
  function rewritePlainLanguage(root) {
    if (!root) return;
    const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
    const nodes = [];
    while (walker.nextNode()) nodes.push(walker.currentNode);
    nodes.forEach((text) => {
      const parent = text.parentElement;
      if (!parent || parent.closest("details.mira-advanced, pre, code")) return;
      text.nodeValue = text.nodeValue
        .replace(/immutable UUID/gi, "permanent item identity")
        .replace(/immutable asset UUID/gi, "permanent item identity")
        .replace(/UUID identity/gi, "item identity")
        .replace(/UUIDs/gi, "item identities")
        .replace(/\bUUID\b/g, "item ID");
    });
  }

  function polishWizard() {
    const dialog = document.querySelector("#miraV1Onboarding .mira-v1-dialog");
    if (!dialog || dialog.dataset.brandPolished === "true") return;
    dialog.dataset.brandPolished = "true";
    const brand = dialog.querySelector(".mira-v1-brand");
    if (brand) {
      brand.replaceChildren();
      const row = document.createElement("div");
      row.className = "mira-brand-left";
      const image = document.createElement("img");
      image.className = "mira-brand-mark";
      image.src = "brand-mark.svg";
      image.alt = "MIRA";
      const words = document.createElement("div");
      words.className = "mira-wordmark";
      const name = document.createElement("strong"); name.textContent = "MIRA";
      const mirror = document.createElement("small"); mirror.textContent = "MIRROR • Reflecting reality";
      words.append(name, mirror); row.append(image, words); brand.append(row);
    }
    rewritePlainLanguage(dialog);
  }

  function installSetupBridge() {
    if (!globalThis.MiraSleekShell || globalThis.MiraSleekShell._setupBridge) return;
    const fallback = globalThis.MiraSleekShell.showSetup;
    globalThis.MiraSleekShell.showSetup = () => {
      if (globalThis.MiraV1?.showOnboarding) return globalThis.MiraV1.showOnboarding();
      return fallback?.();
    };
    globalThis.MiraSleekShell._setupBridge = true;
  }

  const observer = new MutationObserver(() => { polishWizard(); installSetupBridge(); });
  observer.observe(document.documentElement, { childList: true, subtree: true });
  polishWizard(); installSetupBridge();
})();
