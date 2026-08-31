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
  let processing = null;

  function cloudMode() { return globalThis.MiraAuthorityCompat?.cloudMode?.() === true; }

  async function queueCapturedReceipt() {
    if (!currentReceipt?.receipt_uuid) return null;
    if (cloudMode()) {
      if (globalThis.MiraReceiptQueue?.queueReceipt) {
        const result = await globalThis.MiraReceiptQueue.queueReceipt(currentReceipt);
        processing = result.processing || null;
      }
      if (globalThis.MiraCloudReconciliation?.queueWork) {
        await globalThis.MiraCloudReconciliation.queueWork({
          feature_namespace: "receipts",
          source_type: "receipt",
          source_uuid: currentReceipt.receipt_uuid,
          work_type: "receipt.reconcile",
          processing_mode: "deferred_reconciliation",
          priority: 20,
          freshness_minutes: 1440,
          capabilities: ["text_reasoning"],
          allowed_mutations: ["receipt_fields", "receipt_lines", "merchant", "merchant_location", "inventory_suggestions"],
          confidence_threshold: 0.90
        });
      }
      return processing;
    }
    try {
      const result = await apiJson(`/v1/receipt-processing/${encodeURIComponent(currentReceipt.receipt_uuid)}`);
      processing = result.processing || null;
    } catch (_) {
      processing = null;
    }
    return processing;
  }

  async function uploadReceipt() {
    const file = document.getElementById("receiptPhoto")?.files?.[0];
    if (!file) throw new Error("Take or choose a receipt photo first.");
    setStatus("Saving the original receipt to MIRROR…");
    const form = new FormData();
    form.set("file", file, file.name || "receipt.jpg");
    const response = await authorizedFetch(apiUrl("/v1/receipts/upload"), { method: "POST", body: form });
    const result = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(result.detail || `Receipt capture returned HTTP ${response.status}.`);
    currentReceipt = result.receipt;
    await queueCapturedReceipt();
    renderReceipt();
    setStatus("Saved to MIRROR. MIRA will organize this during Daily Cleanup unless you ask it to clean up now.");
    globalThis.MiraReconciliationUI?.refresh?.().catch(() => {});
  }

  async function parseReceiptText() {
    if (cloudMode()) throw new Error("Cloud receipts are processed from the saved MIRROR receipt. You do not need to paste receipt text here.");
    if (!currentReceipt?.receipt_uuid) throw new Error("Capture the receipt first.");
    const raw = document.getElementById("receiptRawText")?.value.trim();
    if (!raw) throw new Error("Paste extracted receipt text first.");
    const result = await apiJson(`/v1/receipt-processing/${encodeURIComponent(currentReceipt.receipt_uuid)}/extracted-text`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ raw_text: raw, source: "user_supplied_text", merchant_hint: document.getElementById("receiptMerchantHint")?.value.trim() || "" })
    });
    processing = result.processing || null;
    await refreshReceipt(false);
    setStatus(`Receipt text parsed. ${result.parsed_line_count || 0} line(s) are ready for Daily Cleanup or Review.`);
  }

  async function refreshReceipt(showMessage = true) {
    if (!currentReceipt?.receipt_uuid) throw new Error("Capture a receipt first.");
    const result = await apiJson(`/v1/receipts/${encodeURIComponent(currentReceipt.receipt_uuid)}`);
    currentReceipt = result.receipt;
    await queueCapturedReceipt();
    renderReceipt();
    if (showMessage) setStatus("Receipt refreshed from MIRROR.");
  }

  async function openResearchPlan() {
    if (!currentReceipt?.receipt_uuid) throw new Error("Capture a receipt first.");
    if (cloudMode()) {
      setStatus("MIRA handles retailer research from the shared MIRROR receipt during Daily Cleanup. No OpenAI API key is required.");
      return;
    }
    const result = await apiJson(`/v1/receipts/${encodeURIComponent(currentReceipt.receipt_uuid)}/retailer-search-plan`);
    const host = document.getElementById("receiptResearch"); host.replaceChildren();
    (result.search_plan || []).forEach((plan) => {
      const box = el("div", { class: "mira-list-item" });
      box.append(el("strong", { text: plan.official_domain ? `Official retailer: ${plan.official_domain}` : "Retailer research" }));
      box.append(el("div", { class: "muted", text: plan.official_query }));
      const search = el("button", { text: "Open search" });
      search.addEventListener("click", () => {
        const url = `https://www.google.com/search?q=${encodeURIComponent(plan.official_query)}`;
        if (globalThis.MirrorNative?.openExternal) globalThis.MirrorNative.openExternal(url); else window.open(url, "_blank", "noopener");
      });
      box.append(search); host.append(box);
    });
  }

  async function reconcileKnownCandidates() {
    if (!currentReceipt?.receipt_uuid) throw new Error("Capture a receipt first.");
    if (cloudMode()) {
      await finishInMira();
      return;
    }
    const result = await apiJson(`/v1/receipts/${encodeURIComponent(currentReceipt.receipt_uuid)}/reconcile`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ auto_apply_high_confidence: true })
    });
    currentReceipt = result.receipt;
    renderReceipt();
    const needs = result.needs_review?.length || 0;
    setStatus(needs ? `Applied ${result.applied?.length || 0} verified line(s). ${needs} still need review.` : "Receipt reconciliation completed and read back from MIRROR.");
    globalThis.MiraReconciliationUI?.refresh?.().catch(() => {});
  }

  async function finishInMira() {
    if (!currentReceipt?.receipt_uuid) throw new Error("Capture a receipt first.");
    const prompt = `Process the pending MIRROR reconciliation work for receipt ${currentReceipt.receipt_uuid}. Preserve the original receipt, use known MIRROR mappings first, search official merchant/manufacturer sources when product identity is still unknown, capture merchant store/location when supported by the evidence, never overwrite user-confirmed values, write verified results back to MIRROR, and leave low-confidence fields in Needs review.`;
    try { await navigator.clipboard.writeText(prompt); } catch (_) {}
    if (globalThis.MirrorNative?.openExternal) globalThis.MirrorNative.openExternal("https://chatgpt.com/");
    else window.open("https://chatgpt.com/", "_blank", "noopener");
    setStatus("Receipt cleanup request copied and MIRA opened in ChatGPT. The app did not make an OpenAI API call.");
  }

  function money(value) {
    if (value === null || value === undefined || value === "") return "Not read yet";
    const number = Number(value);
    return Number.isFinite(number) ? new Intl.NumberFormat(undefined, { style: "currency", currency: currentReceipt?.currency || "USD" }).format(number) : String(value);
  }

  function renderReceipt() {
    const host = document.getElementById("receiptResult");
    if (!host) return;
    host.replaceChildren();
    if (!currentReceipt) {
      host.append(el("p", { class: "muted", text: "No receipt captured yet." }));
      return;
    }

    const summary = el("div", { class: "mira-receipt-summary" });
    const merchant = currentReceipt.merchant_display || currentReceipt.merchant || "Waiting for cleanup";
    const storeLocation = currentReceipt.merchant_location_display || currentReceipt.store_location || "";
    const fields = [
      ["Store", storeLocation ? `${merchant} • ${storeLocation}` : merchant],
      ["Date", currentReceipt.purchase_at || "Waiting for cleanup"],
      ["Total", money(currentReceipt.total)],
      ["Items", currentReceipt.lines?.length ? String(currentReceipt.lines.length) : "Waiting for cleanup"],
      ["Status", processing?.status === "queued" ? "Waiting for Daily Cleanup" : processing?.status || currentReceipt.status || "Saved"]
    ];
    fields.forEach(([label, value]) => {
      const card = el("div", { class: "mira-receipt-field" });
      card.append(el("span", { class: "muted", text: label }), el("strong", { text: value }));
      summary.append(card);
    });
    host.append(summary);

    if (currentReceipt.lines?.length) {
      const lines = el("div", { class: "mira-list" });
      currentReceipt.lines.forEach((line) => {
        const row = el("div", { class: "mira-list-item" });
        const identity = [line.retailer_sku ? `SKU ${line.retailer_sku}` : "", line.gtin ? `GTIN ${line.gtin}` : "", line.model ? `Model ${line.model}` : ""].filter(Boolean).join(" • ");
        row.append(el("strong", { text: line.product_name || line.description || "Receipt item" }), el("span", { class: "muted", text: [identity, money(line.amount)].filter(Boolean).join(" • ") }));
        lines.append(row);
      });
      host.append(lines);
    }

    const advanced = el("details");
    advanced.append(el("summary", { text: "Advanced record" }));
    advanced.append(el("pre", { class: "mira-code", text: JSON.stringify({ receipt: currentReceipt, processing }, null, 2) }));
    host.append(advanced);
  }

  function buildReceiptPanel() {
    const nav = document.querySelector("header nav");
    if (!nav || nav.querySelector("[data-tab='receipts']")) return;
    const button = el("button", { "data-tab": "receipts", "aria-selected": "false", text: "Receipts" });
    button.addEventListener("click", () => switchTab("receipts")); nav.append(button);

    const panel = el("section", { id: "panel-receipts", class: "panel" });
    const intro = el("div", { class: "card wide" }, [
      el("h2", { text: "Receipts" }),
      el("div", { class: "mira-callout", text: "Capture it once. The original is saved immediately. MIRA normally identifies the store, line items and products later during Daily Cleanup, so a new receipt may not look fully organized right away." }),
      el("p", { class: "muted", text: "Known UPCs, GTINs, model numbers and retailer SKUs can reuse MIRROR's confirmed product mappings instead of researching the same item again." })
    ]);

    const capture = el("div", { class: "card" }, [el("h2", { text: "Add receipt" })]);
    const photo = el("input", { id: "receiptPhoto", type: "file", accept: "image/*,application/pdf", capture: "environment" });
    const upload = el("button", { class: "primary-action", text: "Save receipt" });
    upload.addEventListener("click", () => uploadReceipt().catch(showError));
    const clean = el("button", { text: "Clean up this receipt now" });
    clean.addEventListener("click", () => finishInMira().catch(showError));
    capture.append(photo, el("div", { class: "actions" }, [upload, clean]));

    const result = el("div", { class: "card wide" }, [el("h2", { text: "Receipt status" }), el("div", { id: "receiptResult" })]);

    const manual = el("details", { class: "card wide" });
    manual.append(el("summary", { text: "Advanced receipt tools" }));
    manual.append(el("p", { class: "muted", text: "Manual extracted-text parsing and retailer research are fallback tools. Normal receipt capture should not require these." }));
    const merchant = el("input", { id: "receiptMerchantHint", placeholder: "Store name (optional)" });
    const raw = el("textarea", { id: "receiptRawText", placeholder: "Paste OCR or extracted receipt text" });
    const parseButton = el("button", { text: "Parse supplied text" });
    parseButton.addEventListener("click", () => parseReceiptText().catch(showError));
    const planButton = el("button", { text: "Build official-source search plan" });
    planButton.addEventListener("click", () => openResearchPlan().catch(showError));
    const reconcileButton = el("button", { text: "Apply verified matches" });
    reconcileButton.addEventListener("click", () => reconcileKnownCandidates().catch(showError));
    const refresh = el("button", { text: "Refresh" });
    refresh.addEventListener("click", () => refreshReceipt().catch(showError));
    manual.append(merchant, raw, el("div", { class: "actions" }, [parseButton, planButton, reconcileButton, refresh]), el("div", { id: "receiptResearch", class: "mira-list" }));

    panel.append(intro, capture, result, manual);
    document.querySelector("main")?.append(panel);
    renderReceipt();
  }

  document.addEventListener("DOMContentLoaded", buildReceiptPanel);
})();
