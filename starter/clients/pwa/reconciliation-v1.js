"use strict";

(() => {
  const CHATGPT_URL = "https://chatgpt.com/";
  const CLEANUP_PROMPT = "Process my pending MIRA Daily Cleanup work from MIRROR. Work oldest-first unless something is time-sensitive. Use deterministic/known MIRROR mappings before external research, preserve original evidence, do not overwrite user-confirmed values, write verified results back to MIRROR, and leave low-confidence items in Needs review.";
  const BRIEF_PROMPT = "Set up my MIRA Daily Briefs. Ask me one simple question at a time about when I want briefs and what should be included. Store the finished preferences in MIRROR. Include Daily Cleanup before the brief when possible and consolidate recurring work into the fewest ChatGPT scheduled tasks rather than creating one task per feature.";
  const DEFAULT_PREFS = {
    "daily_cleanup.enabled": true,
    "daily_cleanup.times": ["00:01"],
    "daily_cleanup.timezone_mode": "local",
    "daily_cleanup.attach_to_existing_cycle": true,
    "daily_briefs.configured": false,
    "scheduler.max_chatgpt_slots": 5,
    "scheduler.prefer_consolidation": true,
    "ai.monthly_budget": null,
    "ai.budget_hard_stop": false,
    "ai.warning_thresholds": [50, 75, 90]
  };

  let lastSummary = null;
  let preferences = { ...DEFAULT_PREFS };

  function el(tag, attrs = {}, children = []) {
    const node = document.createElement(tag);
    for (const [key, value] of Object.entries(attrs)) {
      if (key === "class") node.className = value;
      else if (key === "text") node.textContent = value;
      else if (key === "html") node.innerHTML = value;
      else if (["checked", "disabled", "hidden"].includes(key)) node[key] = Boolean(value);
      else node.setAttribute(key, value);
    }
    children.forEach((child) => node.append(child));
    return node;
  }

  function cloudMode() { return globalThis.MiraAuthorityCompat?.cloudMode?.() === true; }
  function connected() {
    if (cloudMode()) return globalThis.MiraProviderConnect?.isCloudConnected?.() === true;
    return typeof apiBase === "function" && Boolean(apiBase());
  }

  async function summary() {
    if (cloudMode() && globalThis.MiraCloudReconciliation?.summary) return globalThis.MiraCloudReconciliation.summary();
    return apiJson("/v1/reconciliation/summary");
  }

  async function work(status = "") {
    if (cloudMode() && globalThis.MiraCloudReconciliation?.listWork) return globalThis.MiraCloudReconciliation.listWork(status);
    return apiJson(`/v1/reconciliation/work${status ? `?status=${encodeURIComponent(status)}` : ""}`);
  }

  async function readPreferences() {
    if (cloudMode()) {
      const result = await apiJson("/v1/settings");
      const settings = result.settings || {};
      preferences = { ...DEFAULT_PREFS };
      Object.keys(DEFAULT_PREFS).forEach((key) => { if (key in settings) preferences[key] = settings[key]; });
      return preferences;
    }
    const result = await apiJson("/v1/automation/preferences");
    preferences = { ...DEFAULT_PREFS, ...(result.preferences || {}) };
    return preferences;
  }

  async function writePreferences(updates) {
    if (cloudMode()) {
      const result = await apiJson("/v1/settings", { method: "PATCH", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ settings: updates }) });
      Object.assign(preferences, updates);
      return result;
    }
    const result = await apiJson("/v1/automation/preferences", { method: "PATCH", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ preferences: updates }) });
    preferences = { ...preferences, ...(result.preferences || {}) };
    return result;
  }

  async function copyAndOpenChat(prompt, label) {
    try { await navigator.clipboard.writeText(prompt); } catch (_) {}
    if (globalThis.MirrorNative?.openExternal) globalThis.MirrorNative.openExternal(CHATGPT_URL);
    else window.open(CHATGPT_URL, "_blank", "noopener");
    const message = `${label} request copied. MIRA will read the pending work from MIRROR; the app is not making an OpenAI API call.`;
    if (typeof setStatus === "function") setStatus(message);
    else globalThis.MiraActionAudit?.announce?.(message);
  }

  function formatMoney(value) {
    const number = Number(value || 0);
    return new Intl.NumberFormat(undefined, { style: "currency", currency: "USD", minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(number);
  }

  function friendlyWork(row) {
    const type = String(row.work_type || "cleanup").replace(/[._-]+/g, " ");
    if (row.source_type === "receipt") return `Receipt ${row.source_uuid?.slice(0, 8) || ""}`;
    if (row.source_type === "asset") return `Item ${row.source_uuid?.slice(0, 8) || ""}`;
    return type.charAt(0).toUpperCase() + type.slice(1);
  }

  function ensureStyles() {
    if (document.getElementById("miraReconciliationStyles")) return;
    const style = document.createElement("style");
    style.id = "miraReconciliationStyles";
    style.textContent = `
      .mira-cleanup-card{display:grid;gap:14px}.mira-cleanup-top{display:flex;align-items:flex-start;justify-content:space-between;gap:16px}.mira-cleanup-count{font-size:2rem;font-weight:800;line-height:1}.mira-cleanup-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(130px,1fr));gap:10px}.mira-cleanup-stat{padding:12px;border:1px solid var(--border,#d7dde6);border-radius:14px}.mira-cleanup-stat strong{display:block;font-size:1.25rem}.mira-cost-callout{padding:14px;border-radius:14px;border:1px solid var(--border,#d7dde6)}.mira-review-group{display:grid;gap:9px}.mira-review-row{display:grid;gap:4px;padding:12px;border:1px solid var(--border,#d7dde6);border-radius:14px}.mira-review-row small{opacity:.72}.mira-settings-grid{display:grid;gap:12px}.mira-settings-grid label{display:grid;gap:5px}.mira-cleanup-note{font-size:.92rem;opacity:.78}.mira-attention-badge{display:inline-flex;align-items:center;justify-content:center;min-width:28px;height:28px;padding:0 9px;border-radius:999px;font-weight:700;border:1px solid var(--border,#d7dde6)}
    `;
    document.head.append(style);
  }

  function openPanel(name) {
    if (typeof switchTab === "function") switchTab(name);
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  function ensureHiddenLegacyTab(name) {
    const nav = document.querySelector("header nav");
    if (!nav || nav.querySelector(`[data-tab='${name}']`)) return;
    const button = el("button", { "data-tab": name, hidden: true, text: name });
    nav.append(button);
  }

  function buildHomeCard() {
    const panel = document.getElementById("panel-home");
    if (!panel || document.getElementById("miraCleanupCard")) return false;
    const card = el("div", { class: "card mira-cleanup-card", id: "miraCleanupCard" });
    const top = el("div", { class: "mira-cleanup-top" });
    const copy = el("div");
    copy.append(el("h2", { text: "Needs your attention" }), el("p", { class: "mira-cleanup-note", text: "New files and receipts are saved immediately. AI organization normally happens during Daily Cleanup, not the instant you add something." }));
    const badge = el("span", { class: "mira-attention-badge", id: "miraAttentionBadge", text: "0" });
    top.append(copy, badge);
    const grid = el("div", { class: "mira-cleanup-grid" });
    grid.append(
      el("div", { class: "mira-cleanup-stat", html: "<strong id='miraWaitingCount'>0</strong><span>waiting for cleanup</span>" }),
      el("div", { class: "mira-cleanup-stat", html: "<strong id='miraReviewCount'>0</strong><span>need your review</span>" }),
      el("div", { class: "mira-cleanup-stat", html: "<strong id='miraCleanupTime'>12:01 AM</strong><span>next cleanup window</span>" })
    );
    const cost = el("div", { class: "mira-cost-callout", id: "miraApiCost", hidden: true });
    const actions = el("div", { class: "actions" });
    const review = el("button", { text: "Review" });
    review.addEventListener("click", () => openPanel("review"));
    const clean = el("button", { class: "primary-action", text: "Clean up now" });
    clean.addEventListener("click", () => copyAndOpenChat(CLEANUP_PROMPT, "Daily Cleanup").catch(showError));
    actions.append(review, clean);
    card.append(top, grid, cost, actions);
    const upcoming = document.getElementById("miraUpcomingCard");
    if (upcoming) panel.insertBefore(card, upcoming); else panel.append(card);
    return true;
  }

  function buildReviewPanel() {
    if (document.getElementById("panel-review")) return false;
    ensureHiddenLegacyTab("review");
    const panel = el("section", { id: "panel-review", class: "panel" });
    const head = el("div", { class: "card wide" });
    head.append(el("h2", { text: "Review" }), el("p", { class: "muted", text: "MIRA only asks you about things it cannot resolve confidently. Your corrections outrank AI suggestions and are remembered as MIRROR knowledge." }));
    const refresh = el("button", { text: "Refresh" });
    refresh.addEventListener("click", () => refreshReview().catch(showError));
    head.append(refresh);
    panel.append(head);
    for (const [id, title, copy] of [
      ["miraReviewNeeds", "Needs your answer", "Ambiguous matches and conflicts that MIRA will not guess about."],
      ["miraReviewWaiting", "Waiting for Daily Cleanup", "Safely stored information that has not been interpreted yet."],
      ["miraReviewProblems", "Problems", "Work that failed repeatedly or needs intervention."],
      ["miraReviewResolved", "Recently resolved", "A short history of completed cleanup work."]
    ]) {
      const card = el("div", { class: "card wide" });
      card.append(el("h2", { text: title }), el("p", { class: "muted", text: copy }), el("div", { id, class: "mira-review-group" }));
      panel.append(card);
    }
    const correction = el("details", { class: "card wide" });
    const summaryNode = el("summary", { text: "Correct a MIRROR value" });
    const form = el("div", { class: "mira-settings-grid" });
    form.append(
      el("label", {}, [document.createTextNode("Record type"), el("input", { id: "miraCorrectionType", placeholder: "receipt or asset" })]),
      el("label", {}, [document.createTextNode("Record ID"), el("input", { id: "miraCorrectionId", placeholder: "MIRROR record ID" })]),
      el("label", {}, [document.createTextNode("Field"), el("input", { id: "miraCorrectionField", placeholder: "e.g. merchant, model, name" })]),
      el("label", {}, [document.createTextNode("Correct value"), el("input", { id: "miraCorrectionValue", placeholder: "What it should be" })])
    );
    const save = el("button", { class: "primary-action", text: "Save my correction" });
    save.addEventListener("click", () => saveCorrection().catch(showError));
    form.append(save);
    correction.append(summaryNode, form);
    panel.append(correction);
    document.querySelector("main")?.append(panel);
    return true;
  }

  function buildSettings() {
    const panel = document.getElementById("panel-system");
    if (!panel || document.getElementById("miraAutomationCard")) return false;
    const card = el("div", { class: "card wide", id: "miraAutomationCard" });
    card.append(el("h2", { text: "MIRA Automation" }), el("p", { class: "muted", text: "Daily Cleanup organizes saved information later. It defaults to 12:01 AM local time and stays out of setup unless you want to change it." }));
    const grid = el("div", { class: "mira-settings-grid" });
    const enabled = el("input", { id: "miraCleanupEnabled", type: "checkbox", checked: true });
    grid.append(el("label", {}, [enabled, document.createTextNode(" Daily Cleanup enabled")]));
    const time = el("input", { id: "miraCleanupPrimaryTime", type: "time", value: "00:01" });
    grid.append(el("label", {}, [document.createTextNode("Primary cleanup time"), time]));
    const extra = el("input", { id: "miraCleanupExtraTimes", placeholder: "Optional additional times, e.g. 12:00,18:00" });
    const details = el("details");
    details.append(el("summary", { text: "Additional cleanup windows" }), el("p", { class: "muted", text: "MIRA tries to put multiple daily times on one recurring task. If a genuinely separate ChatGPT task would be required, Scheduler Planner should warn before consuming another of the five task slots." }), extra);
    grid.append(details);
    const save = el("button", { class: "primary-action", text: "Save Daily Cleanup settings" });
    save.addEventListener("click", () => saveAutomationSettings().catch(showError));
    const brief = el("button", { text: "Set up Daily Briefs" });
    brief.addEventListener("click", () => copyAndOpenChat(BRIEF_PROMPT, "Daily Brief setup").catch(showError));
    grid.append(el("div", { class: "actions" }, [save, brief]));
    card.append(grid);

    const ai = el("details", { class: "card wide" });
    ai.append(el("summary", { text: "Advanced AI processing" }));
    ai.append(el("p", { class: "muted", text: "MIRROR can route cleanup across ChatGPT, optional paid APIs, local models, or OpenClaw. Local-only work never silently falls back to cloud processing. Paid API usage is shown on Home." }));
    const budget = el("input", { id: "miraMonthlyAiBudget", type: "number", min: "0", step: "0.01", placeholder: "Optional monthly API budget" });
    const hard = el("input", { id: "miraAiHardStop", type: "checkbox" });
    const saveBudget = el("button", { text: "Save API budget" });
    saveBudget.addEventListener("click", () => saveBudgetSettings().catch(showError));
    ai.append(el("label", {}, [document.createTextNode("Monthly API budget"), budget]), el("label", {}, [hard, document.createTextNode(" Stop paid processing at the budget")]), saveBudget);
    panel.prepend(ai);
    panel.prepend(card);
    return true;
  }

  function addMoreMenuItem() {
    const list = document.querySelector("#panel-more .mira-more-group .mira-menu-list");
    if (!list || document.getElementById("miraReviewMenuItem")) return false;
    const button = el("button", { class: "mira-menu-item", id: "miraReviewMenuItem" });
    button.type = "button";
    const copy = el("span");
    copy.append(el("strong", { text: "Review" }), el("small", { text: "See what MIRA is waiting on or unsure about" }));
    button.append(copy, el("span", { class: "mira-chevron", text: "›" }));
    button.addEventListener("click", () => openPanel("review"));
    list.prepend(button);
    return true;
  }

  function renderGroup(hostId, rows, emptyCopy) {
    const host = document.getElementById(hostId);
    if (!host) return;
    host.replaceChildren();
    if (!rows.length) { host.append(el("div", { class: "muted", text: emptyCopy })); return; }
    rows.slice(0, 50).forEach((row) => {
      const item = el("div", { class: "mira-review-row" });
      item.append(el("strong", { text: friendlyWork(row) }), el("small", { text: `${String(row.status || "").replace(/_/g, " ")} • ${row.feature_namespace || "MIRA"}` }));
      if (row.last_error) item.append(el("small", { text: row.last_error }));
      host.append(item);
    });
  }

  async function refreshReview() {
    if (!connected()) return;
    const result = await work();
    const rows = result.items || [];
    renderGroup("miraReviewNeeds", rows.filter((row) => row.status === "needs_review"), "Nothing needs your answer.");
    renderGroup("miraReviewWaiting", rows.filter((row) => ["queued", "processing", "failed_retryable"].includes(row.status)), "Nothing is waiting for cleanup.");
    renderGroup("miraReviewProblems", rows.filter((row) => row.status === "quarantined"), "No cleanup problems.");
    renderGroup("miraReviewResolved", rows.filter((row) => row.status === "complete").slice(-20).reverse(), "No recently resolved work yet.");
  }

  async function saveCorrection() {
    const entityType = document.getElementById("miraCorrectionType")?.value.trim();
    const entityUuid = document.getElementById("miraCorrectionId")?.value.trim();
    const field = document.getElementById("miraCorrectionField")?.value.trim();
    const value = document.getElementById("miraCorrectionValue")?.value;
    if (!entityType || !entityUuid || !field) throw new Error("Choose the record, record ID, and field you are correcting.");
    if (cloudMode()) {
      const key = `user_correction.${entityType}.${entityUuid}.${field}`;
      await apiJson("/v1/settings", { method: "PATCH", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ settings: { [key]: { value, authority: "user_confirmed", corrected_at: new Date().toISOString() } } }) });
      await globalThis.MiraCloudReconciliation?.queueWork?.({ feature_namespace: "corrections", source_type: entityType, source_uuid: entityUuid, work_type: "correction.apply", priority: 40, allowed_mutations: [field], confidence_threshold: 1 });
    } else {
      await apiJson("/v1/reconciliation/corrections", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ entity_type: entityType, entity_uuid: entityUuid, field_name: field, confirmed_value: value, reason: "Corrected in MIRA app" }) });
    }
    setStatus("Correction saved as user-confirmed truth. Future AI suggestions cannot silently overwrite it.");
    await refreshReview();
  }

  async function saveAutomationSettings() {
    const enabled = Boolean(document.getElementById("miraCleanupEnabled")?.checked);
    const primary = document.getElementById("miraCleanupPrimaryTime")?.value || "00:01";
    const extras = String(document.getElementById("miraCleanupExtraTimes")?.value || "").split(",").map((item) => item.trim()).filter(Boolean);
    const times = [...new Set([primary, ...extras])].sort();
    await writePreferences({ "daily_cleanup.enabled": enabled, "daily_cleanup.times": times });
    setStatus(times.length > 1 ? "Daily Cleanup windows saved. Scheduler Planner should consolidate these into one recurring MIRA task whenever possible." : "Daily Cleanup settings saved to MIRROR.");
    await refresh();
  }

  async function saveBudgetSettings() {
    const raw = document.getElementById("miraMonthlyAiBudget")?.value;
    const budget = raw === "" ? null : Number(raw);
    if (budget !== null && (!Number.isFinite(budget) || budget < 0)) throw new Error("Monthly budget must be zero or greater.");
    await writePreferences({ "ai.monthly_budget": budget, "ai.budget_hard_stop": Boolean(document.getElementById("miraAiHardStop")?.checked) });
    setStatus("AI budget settings saved to MIRROR.");
    await refresh();
  }

  function displayTime(value) {
    const [hour, minute] = String(value || "00:01").split(":").map(Number);
    const date = new Date(); date.setHours(hour || 0, minute || 0, 0, 0);
    return date.toLocaleTimeString([], { hour: "numeric", minute: "2-digit" });
  }

  function populateSettings() {
    const times = Array.isArray(preferences["daily_cleanup.times"]) && preferences["daily_cleanup.times"].length ? preferences["daily_cleanup.times"] : ["00:01"];
    const enabled = document.getElementById("miraCleanupEnabled"); if (enabled) enabled.checked = preferences["daily_cleanup.enabled"] !== false;
    const primary = document.getElementById("miraCleanupPrimaryTime"); if (primary) primary.value = times[0];
    const extra = document.getElementById("miraCleanupExtraTimes"); if (extra) extra.value = times.slice(1).join(",");
    const budget = document.getElementById("miraMonthlyAiBudget"); if (budget) budget.value = preferences["ai.monthly_budget"] == null ? "" : String(preferences["ai.monthly_budget"]);
    const hard = document.getElementById("miraAiHardStop"); if (hard) hard.checked = Boolean(preferences["ai.budget_hard_stop"]);
    const homeTime = document.getElementById("miraCleanupTime"); if (homeTime) homeTime.textContent = displayTime(times[0]);
  }

  function renderSummary(result) {
    lastSummary = result;
    const waiting = Number(result?.waiting || 0), review = Number(result?.needs_review || 0);
    const badge = document.getElementById("miraAttentionBadge"); if (badge) badge.textContent = String(waiting + review);
    const waitingNode = document.getElementById("miraWaitingCount"); if (waitingNode) waitingNode.textContent = String(waiting);
    const reviewNode = document.getElementById("miraReviewCount"); if (reviewNode) reviewNode.textContent = String(review);
    const cost = document.getElementById("miraApiCost");
    if (cost) {
      const api = result?.api_cost || {};
      const show = Boolean(api.metered_processors_enabled) || Number(api.today || 0) > 0 || Number(api.month || 0) > 0;
      cost.hidden = !show;
      if (show) cost.innerHTML = `<strong>Paid AI usage</strong><div>Today: ${formatMoney(api.today)} &nbsp; • &nbsp; This month: ${formatMoney(api.month)}</div>${preferences["ai.monthly_budget"] != null ? `<small>Monthly budget: ${formatMoney(preferences["ai.monthly_budget"])}</small>` : ""}`;
    }
  }

  async function refresh() {
    buildHomeCard(); buildReviewPanel(); buildSettings(); addMoreMenuItem();
    if (!connected()) return;
    try { await readPreferences(); populateSettings(); } catch (_) {}
    try { renderSummary(await summary()); } catch (_) {}
    if (document.getElementById("panel-review")?.classList.contains("active")) refreshReview().catch(() => {});
  }

  function install() {
    ensureStyles();
    buildHomeCard(); buildReviewPanel(); buildSettings(); addMoreMenuItem();
    const observer = new MutationObserver(() => { buildHomeCard(); buildReviewPanel(); buildSettings(); addMoreMenuItem(); });
    observer.observe(document.documentElement, { childList: true, subtree: true });
    setTimeout(() => refresh().catch(() => {}), 250);
  }

  document.addEventListener("DOMContentLoaded", install);
  document.addEventListener("mira:provider-state", () => setTimeout(() => refresh().catch(() => {}), 300));
  globalThis.MiraReconciliationUI = { refresh, refreshReview, cleanupPrompt: CLEANUP_PROMPT, briefSetupPrompt: BRIEF_PROMPT };
})();
