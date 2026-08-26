"use strict";

(() => {
  function el(tag, attrs = {}, children = []) {
    const item = document.createElement(tag);
    Object.entries(attrs).forEach(([key, value]) => {
      if (key === "text") item.textContent = value;
      else if (key === "class") item.className = value;
      else if (["checked", "disabled", "hidden"].includes(key)) item[key] = Boolean(value);
      else item.setAttribute(key, value);
    });
    children.forEach((child) => item.append(child));
    return item;
  }

  let currentReceipt = null;

  async function uploadReceipt() {
    const file = document.getElementById("receiptPhoto")?.files?.[0];
    if (!file) throw new Error("Take or choose a receipt photo first.");
    const form = new FormData(); form.set("file", file, file.name || "receipt.jpg");
    const response = await authorizedFetch(apiUrl("/v1/receipts/upload"), { method: "POST", body: form });
    const result = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(result.detail || `Receipt upload returned HTTP ${response.status}.`);
    currentReceipt = result.receipt;
    renderReceipt();
    setStatus(`Receipt ${currentReceipt.receipt_uuid} captured. Original evidence is retained before parsing.`);
  }

  async function parseReceiptText() {
    const raw = document.getElementById("receiptRawText")?.value.trim();
    if (!raw) throw new Error("Paste extracted receipt text first.");
    const result = await apiJson("/v1/receipts/parse-text", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ raw_text: raw, merchant_hint: document.getElementById("receiptMerchantHint")?.value.trim() || "" }),
    });
    currentReceipt = result.receipt;
    renderReceipt();
    setStatus(`Parsed ${currentReceipt.lines?.length || 0} candidate receipt lines. External product matches are still evidence candidates, not canonical items.`);
  }

  async function refreshReceipt() {
    if (!currentReceipt?.receipt_uuid) throw new Error("Capture or parse a receipt first.");
    const result = await apiJson(`/v1/receipts/${encodeURIComponent(currentReceipt.receipt_uuid)}`);
    currentReceipt = result.receipt;
    renderReceipt();
  }

  async function openResearchPlan() {
    if (!currentReceipt?.receipt_uuid) throw new Error("Capture or parse a receipt first.");
    const result = await apiJson(`/v1/receipts/${encodeURIComponent(currentReceipt.receipt_uuid)}/retailer-search-plan`);
    const host = document.getElementById("receiptResearch"); host.replaceChildren();
    (result.search_plan || []).forEach((plan) => {
      const box = el("div", { class: "mira-list-item" });
      box.append(el("strong", { text: plan.official_domain ? `Official-site research: ${plan.official_domain}` : "Retailer research" }));
      box.append(el("div", { class: "muted", text: plan.official_query }));
      const search = el("button", { text: "Open this search" });
      search.addEventListener("click", () => {
        const url = `https://www.google.com/search?q=${encodeURIComponent(plan.official_query)}`;
        if (globalThis.MirrorNative?.openExternal) globalThis.MirrorNative.openExternal(url); else window.open(url, "_blank", "noopener");
      });
      box.append(search); host.append(box);
    });
  }

  async function reconcileKnownCandidates() {
    if (!currentReceipt?.receipt_uuid) throw new Error("Capture or parse a receipt first.");
    const result = await apiJson(`/v1/receipts/${encodeURIComponent(currentReceipt.receipt_uuid)}/reconcile`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ auto_apply_high_confidence: true }),
    });
    currentReceipt = result.receipt;
    renderReceipt();
    const needs = result.needs_review?.length || 0;
    setStatus(needs ? `Applied ${result.applied?.length || 0} verified lines; ${needs} line(s) still need research/review.` : "Receipt reconciliation completed and read back.");
  }

  function renderReceipt() {
    const host = document.getElementById("receiptResult");
    if (!host) return;
    host.textContent = currentReceipt ? JSON.stringify(currentReceipt, null, 2) : "No receipt captured yet.";
  }

  function buildReceiptPanel() {
    const nav = document.querySelector("header nav");
    if (!nav || nav.querySelector("[data-tab='receipts']")) return;
    const button = el("button", { "data-tab": "receipts", "aria-selected": "false", text: "Receipts" });
    button.addEventListener("click", () => switchTab("receipts")); nav.append(button);

    const panel = el("section", { id: "panel-receipts", class: "panel" });
    const chat = el("div", { class: "card wide" }, [
      el("h2", { text: "Reconcile a receipt" }),
      el("div", { class: "mira-callout", text: "Fastest path: in MIRA inside ChatGPT, attach the receipt and ask ‘Reconcile this receipt.’ ChatGPT can read the image, search the official retailer site first, preserve provenance, auto-apply unique high-confidence matches and ask only about ambiguous lines." }),
      el("p", { class: "muted", text: "The standalone client can also capture the original receipt and parse extracted text. It never fabricates product metadata when no research source is available." })
    ]);

    const capture = el("div", { class: "card" }, [el("h2", { text: "Capture original" })]);
    const photo = el("input", { id: "receiptPhoto", type: "file", accept: "image/*,application/pdf", capture: "environment" });
    const upload = el("button", { class: "primary-action", text: "Capture receipt" });
    upload.addEventListener("click", () => uploadReceipt().catch(showError));
    capture.append(photo, upload);

    const parse = el("div", { class: "card" }, [el("h2", { text: "Parse receipt text" })]);
    const merchant = el("input", { id: "receiptMerchantHint", placeholder: "Merchant hint (optional)" });
    const raw = el("textarea", { id: "receiptRawText", placeholder: "Paste OCR/extracted receipt text here" });
    const parseButton = el("button", { text: "Parse receipt lines" });
    parseButton.addEventListener("click", () => parseReceiptText().catch(showError));
    parse.append(merchant, raw, parseButton);

    const research = el("div", { class: "card wide" }, [el("h2", { text: "Retailer research" }), el("p", { class: "muted", text: "MIRA searches the official retailer domain first using SKU/item number + receipt wording. Hosted clients can open the same research queries; ChatGPT-native MIRA can perform the research directly." })]);
    const planButton = el("button", { text: "Build official-site search plan" });
    planButton.addEventListener("click", () => openResearchPlan().catch(showError));
    const reconcileButton = el("button", { class: "primary-action", text: "Apply verified high-confidence matches" });
    reconcileButton.addEventListener("click", () => reconcileKnownCandidates().catch(showError));
    const refresh = el("button", { text: "Refresh receipt" }); refresh.addEventListener("click", () => refreshReceipt().catch(showError));
    research.append(el("div", { class: "actions" }, [planButton, reconcileButton, refresh]), el("div", { id: "receiptResearch", class: "mira-list" }));

    const result = el("div", { class: "card wide" }, [el("h2", { text: "Receipt record" }), el("pre", { id: "receiptResult", class: "mira-code" })]);
    panel.append(chat, capture, parse, research, result);
    document.querySelector("main")?.append(panel);
    renderReceipt();
  }

  document.addEventListener("DOMContentLoaded", buildReceiptPanel);
})();
