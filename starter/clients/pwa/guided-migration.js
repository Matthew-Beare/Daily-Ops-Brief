"use strict";

(() => {
  let stagedSnapshotUuid = null;

  async function previewMagic(snapshotUuid) {
    const result = await apiJson(`/v1/migrations/${encodeURIComponent(snapshotUuid)}/magic`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ apply: false }),
    });
    const host = document.getElementById("migrationMagicResult");
    if (host) host.textContent = JSON.stringify(result.plan, null, 2);
    const apply = document.getElementById("migrationMagicApply");
    if (apply) {
      apply.disabled = !result.plan?.safe_to_apply;
      apply.textContent = result.plan?.fully_automatic ? "4. Import everything safely" : "4. Import safe rows + keep ambiguous rows for review";
    }
    return result;
  }

  async function applyMagic() {
    if (!stagedSnapshotUuid) throw new Error("Preview a staged spreadsheet first.");
    const result = await apiJson(`/v1/migrations/${encodeURIComponent(stagedSnapshotUuid)}/magic`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ apply: true }),
    });
    const host = document.getElementById("migrationMagicResult");
    if (host) host.textContent = JSON.stringify(result, null, 2);
    const needs = result.result?.needs_review?.length || 0;
    const unknown = result.result?.unknown_sheets?.length || 0;
    if (needs || unknown) setStatus(`Migration applied every unambiguous row. ${needs + unknown} item(s) remain for review; MIRA did not guess.`);
    else setStatus("Migration applied in one verified transaction. UUID identity was preserved or generated where legacy data had no UUID.");
  }

  function hookStageButton(stageButton) {
    if (stageButton.dataset.magicHook === "true") return;
    stageButton.dataset.magicHook = "true";
    stageButton.addEventListener("click", () => {
      const resultPre = document.getElementById("migrationResult");
      let tries = 0;
      const poll = setInterval(() => {
        tries += 1;
        try {
          const payload = JSON.parse(resultPre?.textContent || "{}");
          if (payload.snapshot_uuid) {
            clearInterval(poll);
            stagedSnapshotUuid = payload.snapshot_uuid;
            previewMagic(stagedSnapshotUuid).catch(showError);
          }
        } catch (_) { /* wait for staged JSON */ }
        if (tries > 40) clearInterval(poll);
      }, 250);
    });
  }

  function improveMigrationPanel() {
    const panel = document.getElementById("panel-migration");
    if (!panel || panel.dataset.guided === "true") return;
    const select = document.getElementById("googleSheetSelect");
    const stageButton = select?.nextElementSibling;
    const buttons = select?.previousElementSibling;
    if (!select || !buttons || !stageButton) return;

    panel.dataset.guided = "true";
    hookStageButton(stageButton);
    const googleCard = select.closest(".card");
    if (googleCard) {
      const heading = googleCard.querySelector("h2");
      if (heading) heading.textContent = "Bring in existing Google Sheets";
      const warning = googleCard.querySelector(".mira-warning");
      if (warning) warning.textContent = "Safe preview first: MIRA requests separate read-only Google access, makes a provenance snapshot, and does not change MIRROR while you are choosing or reviewing a spreadsheet.";
      const buttonList = buttons.querySelectorAll("button");
      if (buttonList[0]) buttonList[0].textContent = "1. Continue with Google (read-only)";
      if (buttonList[1]) buttonList[1].textContent = "2. Find my spreadsheets";
      stageButton.textContent = "3. Preview selected spreadsheet";
      const note = document.createElement("div");
      note.className = "mira-callout";
      note.textContent = "Previewing is not importing. The magic import applies only rows whose identity/mapping is unambiguous; uncertain rows remain reviewable instead of being guessed.";
      googleCard.append(note);
    }

    const intro = document.createElement("div");
    intro.className = "card wide";
    intro.innerHTML = `
      <h2>Guided migration</h2>
      <div class="mira-metric-grid">
        <div class="mira-metric"><strong>1. Connect</strong><small>Google grants read-only migration access.</small></div>
        <div class="mira-metric"><strong>2. Find</strong><small>MIRA lists spreadsheets you can read.</small></div>
        <div class="mira-metric"><strong>3. Preview</strong><small>MIRROR hashes and stages a safe snapshot.</small></div>
        <div class="mira-metric"><strong>4. Import</strong><small>One press applies safe rows and leaves only ambiguity for review.</small></div>
      </div>`;
    panel.prepend(intro);

    const magic = document.createElement("div");
    magic.className = "card wide";
    magic.innerHTML = `<h2>Magic import</h2><p class="muted">UUID and strong-identifier matches are preserved. Names alone never merge two assets.</p><button id="migrationMagicApply" class="primary-action" disabled>4. Import safely</button><details><summary>Migration plan and review queue</summary><pre id="migrationMagicResult" class="mira-code">Preview a spreadsheet first.</pre></details>`;
    magic.querySelector("button").addEventListener("click", () => applyMagic().catch(showError));
    panel.append(magic);

    [...panel.querySelectorAll(".card")].forEach((card) => {
      const title = card.querySelector("h2")?.textContent || "";
      if (title === "Stage JSON / legacy export") {
        const details = document.createElement("details");
        const summary = document.createElement("summary");
        summary.textContent = "Advanced: stage a JSON export";
        details.append(summary);
        [...card.children].slice(1).forEach((child) => details.append(child));
        card.append(details);
      }
      if (title === "Migration result") {
        const pre = card.querySelector("pre");
        if (pre) {
          const details = document.createElement("details");
          const summary = document.createElement("summary");
          summary.textContent = "Technical snapshot details";
          details.append(summary, pre);
          card.append(details);
        }
      }
    });
  }

  const observer = new MutationObserver(improveMigrationPanel);
  observer.observe(document.documentElement, { childList: true, subtree: true });
  improveMigrationPanel();
})();
