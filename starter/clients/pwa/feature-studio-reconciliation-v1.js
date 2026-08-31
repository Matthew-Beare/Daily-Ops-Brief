"use strict";

(() => {
  let pendingSubmission = null;

  function el(tag, attrs = {}, children = []) {
    const node = document.createElement(tag);
    for (const [key, value] of Object.entries(attrs)) {
      if (key === "class") node.className = value;
      else if (key === "text") node.textContent = value;
      else if (key === "checked") node.checked = Boolean(value);
      else node.setAttribute(key, value);
    }
    children.forEach((child) => node.append(child));
    return node;
  }

  function cloudMode() { return globalThis.MiraAuthorityCompat?.cloudMode?.() === true; }

  function installControls() {
    const form = document.querySelector("#panel-features .row");
    const submit = document.getElementById("submitFeatureRequest");
    if (!form || !submit || document.getElementById("featureNeedsCleanup")) return false;

    const box = el("div", { class: "mira-callout" });
    const label = el("label");
    const check = el("input", { id: "featureNeedsCleanup", type: "checkbox", checked: true });
    label.append(check, document.createTextNode(" MIRA may need to organize new information later"));
    const copy = el("p", { class: "muted", text: "Keep this on when new information may need MIRA to identify, categorize, match, summarize, or check it later. This joins Daily Cleanup instead of creating another scheduled task." });
    const freshness = el("select", { id: "featureCleanupFreshness" });
    for (const [value, text] of [
      ["next_daily_cleanup", "Next Daily Cleanup"],
      ["within_a_few_hours", "Within a few hours"],
      ["as_soon_as_possible", "As soon as possible"],
      ["only_when_asked", "Only when I ask"]
    ]) freshness.add(new Option(text, value));
    const freshnessLabel = el("label", {}, [document.createTextNode("How soon should MIRA handle it?"), freshness]);
    check.addEventListener("change", () => { freshnessLabel.hidden = !check.checked; });
    box.append(label, copy, freshnessLabel);
    form.insertBefore(box, submit);

    submit.addEventListener("click", () => {
      pendingSubmission = {
        title: document.getElementById("featureTitle")?.value.trim() || "",
        enabled: check.checked,
        freshness: freshness.value,
        capturedAt: Date.now()
      };
      if (!pendingSubmission.title) return;
      setTimeout(() => attachPolicy().catch(() => {}), 500);
    }, true);
    return true;
  }

  async function attachPolicy() {
    if (!pendingSubmission?.title) return;
    const snapshot = pendingSubmission;
    let result;
    try { result = await apiJson("/v1/features/requests?limit=20"); }
    catch (_) { return; }
    const matches = (result.feature_requests || []).filter((item) => item.title === snapshot.title);
    if (!matches.length) {
      if (Date.now() - snapshot.capturedAt < 8000) setTimeout(() => attachPolicy().catch(() => {}), 500);
      return;
    }
    const request = matches[0];
    const policy = {
      enabled: snapshot.enabled,
      processing_mode: snapshot.enabled ? "deferred_reconciliation" : "manual_only",
      freshness: snapshot.freshness,
      capabilities: snapshot.enabled ? ["text_reasoning"] : [],
      allowed_mutations: [],
      confidence_threshold: 0.90
    };
    if (cloudMode() && globalThis.MiraCloudReconciliation?.setFeaturePolicy) {
      await globalThis.MiraCloudReconciliation.setFeaturePolicy(request.request_uuid, policy);
    } else {
      await apiJson(`/v1/features/${encodeURIComponent(request.request_uuid)}/processing-policy`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(policy)
      });
    }
    pendingSubmission = null;
    if (snapshot.enabled && typeof setStatus === "function") setStatus("Feature queued. New information for it will join Daily Cleanup without consuming a feature-specific scheduled task.");
  }

  function install() {
    installControls();
    const observer = new MutationObserver(installControls);
    observer.observe(document.documentElement, { childList: true, subtree: true });
  }

  document.addEventListener("DOMContentLoaded", () => setTimeout(install, 120));
})();
