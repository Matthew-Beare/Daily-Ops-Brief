"use strict";

(() => {
  const LOGO = "mira-logo.png";

  function applyBrand(root = document) {
    root.querySelectorAll?.("img.mira-brand-lockup,img.mira-release-brand").forEach((img) => {
      if (!String(img.getAttribute("src") || "").endsWith(LOGO)) img.src = LOGO;
      img.alt = "MIRA — Reflecting reality";
    });
    const icon = document.querySelector("link[rel='icon']");
    if (icon) { icon.href = LOGO; icon.type = "image/png"; }
    document.title = "MIRA — Reflecting reality";
  }

  function simplifyAssetRows(root = document) {
    root.querySelectorAll?.(".asset-row small").forEach((detail) => {
      const parts = String(detail.textContent || "").split(" | ");
      if (parts.length >= 3) detail.textContent = parts.slice(0, 2).join(" • ");
    });
  }

  function makeTechnicalDetailsPrivate(root = document) {
    ["assetResult", "providerStatus", "treeResult"].forEach((id) => {
      const node = root.getElementById?.(id) || document.getElementById(id);
      if (!node || node.closest("details")) return;
      const details = document.createElement("details");
      details.className = "mira-technical-details";
      const summary = document.createElement("summary");
      summary.textContent = "Advanced";
      node.parentNode?.insertBefore(details, node);
      details.append(summary, node);
    });
  }

  function cleanSetupCopy() {
    const setup = document.getElementById("panel-setup");
    if (!setup) return;
    const firstCard = setup.querySelector(".card.wide");
    const heading = firstCard?.querySelector("h2");
    if (heading) heading.textContent = "MIRA settings";
    const callout = firstCard?.querySelector(".mira-callout");
    if (callout) callout.textContent = "MIRA is the assistant. MIRROR is the private data underneath it. Choose cloud, cloud plus local services, or self-hosted MIRROR. The app and ChatGPT always use the same MIRROR state.";
  }

  function cleanVisibleLanguage(root = document) {
    root.querySelectorAll?.("button,summary,h1,h2,h3,p,small,label,span").forEach((node) => {
      if (node.childElementCount) return;
      let text = String(node.textContent || "");
      text = text
        .replace(/immutable asset UUID/gi, "permanent item identity")
        .replace(/immutable UUID/gi, "permanent item identity")
        .replace(/canonical authority/gi, "MIRROR data")
        .replace(/MIRROR authority/gi, "MIRROR data")
        .replace(/metadata JSON/gi, "advanced details")
        .replace(/\bUUID\b/g, "record ID");
      if (text !== node.textContent) node.textContent = text;
    });
    cleanSetupCopy();
  }

  function apply(root = document) {
    applyBrand(root);
    simplifyAssetRows(root);
    makeTechnicalDetailsPrivate(root);
    cleanVisibleLanguage(root);
  }

  document.addEventListener("DOMContentLoaded", () => {
    setTimeout(() => apply(document), 90);
    const observer = new MutationObserver((mutations) => {
      mutations.forEach((mutation) => mutation.addedNodes.forEach((node) => {
        if (node.nodeType === Node.ELEMENT_NODE) apply(node);
      }));
    });
    observer.observe(document.documentElement, { childList: true, subtree: true });
  });
})();