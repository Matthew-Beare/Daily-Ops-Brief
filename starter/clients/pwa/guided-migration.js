"use strict";

(() => {
  let stagedSnapshotId = null;
  let googleConnected = false;

  async function connectionState() {
    if (typeof apiBase !== "function" || !apiBase()) return false;
    try {
      const result = await apiJson("/v1/integrations/provider-health");
      return Boolean(result.google_workspace?.connected);
    } catch (_) {
      return false;
    }
  }

  function connectGoogle() {
    if (typeof apiBase !== "function" || !apiBase()) {
      setStatus("Finish setup first. MIRA needs a Google connection before it can import your spreadsheets.");
      globalThis.MiraV1?.showOnboarding?.();
      return;
    }
    const returnTo = `${apiBase()}/`;
    const url = apiUrl(`/v1/migrations/google/auth/start?return_to=${encodeURIComponent(returnTo)}`);
    if (globalThis.MirrorNative?.openExternal) globalThis.MirrorNative.openExternal(url);
    else location.href = url;
  }

  function requireGoogle() {
    if (googleConnected) return true;
    setStatus("Connect Google first. MIRA will request read-only spreadsheet access and bring you back here.");
    connectGoogle();
    return false;
  }

  async function discover() {
    if (!requireGoogle()) return;
    const result = await apiJson("/v1/migrations/google/discover?page_size=250");
    const select = document.getElementById("googleSheetSelect");
    select.replaceChildren(new Option("Choose a spreadsheet", ""));
    for (const sheet of result.spreadsheets || []) {
      select.add(new Option(`${sheet.name}${sheet.modifiedTime ? ` • ${sheet.modifiedTime.slice(0, 10)}` : ""}`, sheet.id));
    }
    setStatus(`Found ${(result.spreadsheets || []).length} spreadsheet${(result.spreadsheets || []).length === 1 ? "" : "s"}. Choose one to preview.`);
    updateSteps();
  }

  async function previewSelected() {
    if (!requireGoogle()) return;
    const select = document.getElementById("googleSheetSelect");
    const fileId = select?.value;
    if (!fileId) {
      setStatus("Choose a spreadsheet first.");
      select?.focus();
      return;
    }
    const staged = await apiJson("/v1/migrations/google/stage-sheet", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ file_id: fileId }),
    });
    stagedSnapshotId = staged.snapshot_uuid;
    const result = await apiJson(`/v1/migrations/${encodeURIComponent(stagedSnapshotId)}/magic`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ apply: false }),
    });
    const technical = document.getElementById("migrationMagicResult");
    if (technical) technical.textContent = JSON.stringify(result.plan || result, null, 2);
    const summary = document.getElementById("migrationPlanSummary");
    if (summary) summary.textContent = "Preview ready. Nothing has been imported yet. MIRA will only apply records it can match safely.";
    setStatus("Preview ready. Nothing has been imported yet.");
    updateSteps();
  }

  async function applyMagic() {
    if (!requireGoogle()) return;
    if (!stagedSnapshotId) {
      setStatus("Preview a spreadsheet before importing it.");
      return;
    }
    const result = await apiJson(`/v1/migrations/${encodeURIComponent(stagedSnapshotId)}/magic`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ apply: true }),
    });
    const unresolved = (result.result?.needs_review?.length || 0) + (result.result?.unknown_sheets?.length || 0);
    setStatus(unresolved
      ? `Imported everything MIRA could prove safely. ${unresolved} item${unresolved === 1 ? "" : "s"} still need your decision.`
      : "Import complete. MIRA verified the new records and preserved existing item identities.");
    const technical = document.getElementById("migrationMagicResult");
    if (technical) technical.textContent = JSON.stringify(result, null, 2);
    updateSteps(true);
  }

  function makeStep(number, title, copy, buttonText, action) {
    const row = document.createElement("div");
    row.className = "mira-migration-step";
    row.dataset.step = String(number);
    const n = document.createElement("div"); n.className = "step-number"; n.textContent = String(number);
    const body = document.createElement("div");
    const strong = document.createElement("strong"); strong.textContent = title;
    const small = document.createElement("small"); small.textContent = copy;
    body.append(strong, small);
    const button = document.createElement("button"); button.type = "button"; button.textContent = buttonText;
    button.addEventListener("click", () => Promise.resolve(action()).catch((error) => setStatus(error?.message || String(error))));
    row.append(n, body, button);
    return row;
  }

  function updateSteps(imported = false) {
    const select = document.getElementById("googleSheetSelect");
    let current = 1;
    if (googleConnected) current = 2;
    if (googleConnected && select?.options.length > 1) current = 3;
    if (stagedSnapshotId) current = 4;
    document.querySelectorAll(".mira-migration-step").forEach((row) => {
      const number = Number(row.dataset.step);
      row.classList.toggle("current", number === current);
      row.classList.toggle("locked", number > current);
      if (imported && number === 4) row.classList.add("current");
    });
    const connection = document.getElementById("migrationConnectionState");
    if (connection) connection.textContent = googleConnected ? "Google connected" : "Google is not connected yet";
  }

  async function improve() {
    const panel = document.getElementById("panel-migration");
    if (!panel || panel.dataset.progressive === "true") return;
    const select = document.getElementById("googleSheetSelect");
    if (!select) return;
    panel.dataset.progressive = "true";
    googleConnected = await connectionState();

    const oldCards = [...panel.querySelectorAll(":scope > .card")];
    oldCards.forEach((card) => card.remove());

    const card = document.createElement("div");
    card.className = "card wide";
    const title = document.createElement("h2"); title.textContent = "Bring in your Google data";
    const intro = document.createElement("p"); intro.className = "muted"; intro.textContent = "One step at a time. MIRA previews first and does not change your inventory until you press Import.";
    const connection = document.createElement("div"); connection.id = "migrationConnectionState"; connection.className = "mira-callout";
    const flow = document.createElement("div"); flow.className = "mira-migration-flow";
    flow.append(
      makeStep(1, "Connect Google", "One-time read-only access for finding and previewing spreadsheets.", googleConnected ? "Connected" : "Connect Google", () => googleConnected ? setStatus("Google is already connected.") : connectGoogle()),
      makeStep(2, "Find your spreadsheets", "MIRA lists the spreadsheets your Google account can read.", "Find spreadsheets", discover),
      makeStep(3, "Choose and preview", "Pick one below. Previewing still does not import anything.", "Preview", previewSelected),
      makeStep(4, "Import what is safe", "MIRA applies unambiguous records and leaves uncertain matches alone.", "Import safely", applyMagic)
    );

    const picker = document.createElement("div"); picker.className = "row"; picker.append(select);
    const plan = document.createElement("div"); plan.id = "migrationPlanSummary"; plan.className = "mira-callout"; plan.textContent = "Start by connecting Google. If you skipped onboarding, MIRA will take you to the missing step.";
    const advanced = document.createElement("details");
    const advancedSummary = document.createElement("summary"); advancedSummary.textContent = "Advanced migration details";
    const technical = document.createElement("pre"); technical.id = "migrationMagicResult"; technical.className = "mira-code"; technical.textContent = "No preview yet.";
    advanced.append(advancedSummary, technical);
    card.append(title, intro, connection, flow, picker, plan, advanced);
    panel.append(card);
    select.addEventListener("change", updateSteps);
    updateSteps();
  }

  const observer = new MutationObserver(() => improve().catch(() => {}));
  observer.observe(document.documentElement, { childList: true, subtree: true });
  document.addEventListener("DOMContentLoaded", () => setTimeout(() => improve().catch(() => {}), 100));
})();
