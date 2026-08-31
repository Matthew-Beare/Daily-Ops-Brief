"use strict";

(() => {
  const TODO_KEY = "mira.home.todo.drafts.v1";

  function el(tag, attrs = {}, children = []) {
    const item = document.createElement(tag);
    Object.entries(attrs).forEach(([key, value]) => {
      if (key === "class") item.className = value;
      else if (key === "text") item.textContent = value;
      else if (key === "html") item.innerHTML = value;
      else item.setAttribute(key, value);
    });
    children.forEach((child) => item.append(child));
    return item;
  }

  function existingApiBase() {
    try { return typeof apiBase === "function" ? apiBase() : ""; } catch (_) { return ""; }
  }

  function openPanel(name) {
    if (typeof switchTab === "function") switchTab(name);
    document.querySelectorAll(".mira-bottom-nav button[data-shell-tab]").forEach((button) => button.classList.toggle("active", button.dataset.shellTab === name));
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  function installBrand() {
    const header = document.querySelector("header");
    if (!header || header.querySelector(".mira-brandbar")) return;
    const bar = el("div", { class: "mira-brandbar" });
    const left = el("div", { class: "mira-brand-left" }, [
      el("img", { class: "mira-brand-mark", src: "brand-mark.svg", alt: "MIRA" }),
      el("div", { class: "mira-wordmark" }, [el("strong", { text: "MIRA" }), el("small", { text: "MIRROR • Reflecting reality" })]),
    ]);
    const status = el("div", { class: "mira-brand-status" }, [el("span", { class: "mira-brand-dot", id: "miraBrandDot" }), el("span", { id: "miraBrandState", text: "Setup" })]);
    bar.append(left, status);
    header.prepend(bar);
  }

  function loadLocalTodos() {
    try { const rows = JSON.parse(localStorage.getItem(TODO_KEY) || "[]"); return Array.isArray(rows) ? rows : []; } catch (_) { return []; }
  }

  function renderTodos() {
    const host = document.getElementById("miraHomeTodo");
    if (!host) return;
    const rows = loadLocalTodos();
    host.replaceChildren();
    if (!rows.length) {
      host.append(el("div", { class: "mira-empty", text: existingApiBase() ? "No local draft tasks. Connected Google tasks and reminders will appear here as the home feed is enabled." : "Finish setup and connect Google. Your tasks, reminders and upcoming work will live here." }));
      return;
    }
    rows.slice(0, 6).forEach((row, index) => {
      const check = el("button", { class: "mira-check", "aria-label": `Complete ${row.text}` });
      check.addEventListener("click", () => {
        const next = loadLocalTodos(); next.splice(index, 1); localStorage.setItem(TODO_KEY, JSON.stringify(next)); renderTodos();
      });
      host.append(el("div", { class: "mira-todo-item" }, [check, el("div", {}, [el("strong", { text: row.text }), el("small", { class: "muted", text: "Draft task • syncs to the configured authority when task sync is enabled" })]) ]));
    });
  }

  function addDraftTask() {
    const text = prompt("What do you need to do?");
    if (!text?.trim()) return;
    const rows = loadLocalTodos();
    rows.unshift({ text: text.trim(), created_at: new Date().toISOString() });
    localStorage.setItem(TODO_KEY, JSON.stringify(rows.slice(0, 50)));
    renderTodos();
  }

  async function refreshHome() {
    const stateLabel = document.getElementById("miraBrandState");
    const stateDot = document.getElementById("miraBrandDot");
    const upcoming = document.getElementById("miraUpcomingList");
    const heroCopy = document.getElementById("miraHeroCopy");
    const setupAction = document.getElementById("miraHomeSetup");
    if (!upcoming) return;
    upcoming.replaceChildren();
    if (!existingApiBase()) {
      if (stateLabel) stateLabel.textContent = "Setup needed";
      if (stateDot) stateDot.classList.remove("ok");
      if (heroCopy) heroCopy.textContent = "Connect Google to bring appointments, reminders, deliveries and tasks into one view.";
      if (setupAction) setupAction.hidden = false;
      upcoming.append(el("div", { class: "mira-empty", text: "Nothing is wrong. This test app is not connected yet. Finish setup to populate Upcoming." }));
      return;
    }
    if (setupAction) setupAction.hidden = true;
    try {
      const provider = await apiJson("/v1/integrations/provider-health");
      const google = provider.google_workspace || {};
      if (stateLabel) stateLabel.textContent = google.connected ? "Google connected" : "Connect Google";
      if (stateDot) stateDot.classList.toggle("ok", Boolean(google.connected));
      if (heroCopy) heroCopy.textContent = google.connected ? "Your next things, without digging through six screens." : "MIRA is running. Connect Google to populate your personal Upcoming feed.";
      try {
        const result = await apiJson("/v1/home");
        const rows = result.upcoming || [];
        rows.slice(0, 5).forEach((row) => upcoming.append(el("div", { class: "mira-upcoming-item" }, [
          el("div", { class: "mira-upcoming-time", text: row.when_label || row.time || "Soon" }),
          el("div", {}, [el("strong", { text: row.title || "Upcoming item" }), el("small", { text: row.subtitle || row.kind || "MIRA" })]),
          el("span", { class: "mira-badge", text: row.status || "upcoming" }),
        ])));
        if (!rows.length) upcoming.append(el("div", { class: "mira-empty", text: google.connected ? "Nothing urgent is coming up right now." : "Continue with Google to populate Upcoming." }));
      } catch (_) {
        upcoming.append(el("div", { class: "mira-empty", text: google.connected ? "Google is connected. Upcoming aggregation is not enabled on this test backend yet." : "Continue with Google to populate Upcoming." }));
      }
    } catch (_) {
      if (stateLabel) stateLabel.textContent = "Connected";
      if (stateDot) stateDot.classList.add("ok");
      upcoming.append(el("div", { class: "mira-empty", text: "MIRA is connected, but this test backend does not expose the home feed yet." }));
    }
  }

  function buildHome() {
    const main = document.querySelector("main");
    if (!main || document.getElementById("panel-home")) return;
    const panel = el("section", { id: "panel-home", class: "panel" });
    const hero = el("div", { class: "card wide mira-home-hero" }, [
      el("div", { class: "mira-eyebrow", text: "Upcoming" }),
      el("h2", { text: "What matters next" }),
      el("p", { id: "miraHeroCopy", text: "One view for the things that actually need your attention." }),
      el("div", { id: "miraUpcomingList", class: "mira-upcoming-list" }),
    ]);
    const setup = el("button", { id: "miraHomeSetup", class: "primary-action", text: "Finish setup" });
    setup.addEventListener("click", () => globalThis.MiraSleekShell?.showSetup());
    hero.append(setup);

    const quick = el("div", { class: "mira-quick-grid wide" });
    const action = (icon, title, note, fn, primary = false) => {
      const button = el("button", { class: `mira-quick${primary ? " primary" : ""}` }, [el("span", { class: "mira-icon", text: icon }), el("strong", { text: title }), el("small", { text: note })]);
      button.addEventListener("click", fn); quick.append(button);
    };
    action("＋", "Add", "Item, photo or receipt", () => openCaptureSheet(), true);
    action("⌁", "Scan", "QR, barcode or NFC", () => openPanel("scan"));
    action("⌕", "Find", "Search your inventory", () => { openPanel("inventory"); setTimeout(()=>document.getElementById("assetSearch")?.focus(),150); });
    action("•••", "More", "Organize, migrate, settings", () => openMoreSheet());

    const grid = el("div", { class: "mira-home-grid wide" });
    const todo = el("div", { class: "card" }, [el("div", { class: "mira-section-title" }, [el("h2", { text: "To do" })]), el("div", { id: "miraHomeTodo", class: "mira-todo" })]);
    const add = el("button", { class: "mira-text-button", text: "+ Add task" }); add.addEventListener("click", addDraftTask); todo.querySelector(".mira-section-title").append(add);
    const activity = el("div", { class: "card" }, [el("div", { class: "mira-section-title" }, [el("h2", { text: "At a glance" })]), el("div", { class: "mira-metric-grid" }, [
      el("div", { class: "mira-metric", html: "<strong id='miraHomePending'>0</strong><small>captures waiting</small>" }),
      el("div", { class: "mira-metric", html: "<strong id='miraHomeSelected'>—</strong><small>selected item</small>" }),
    ])]);
    grid.append(todo, activity);
    panel.append(hero, quick, grid);
    main.prepend(panel);
    renderTodos();
  }

  function closeSheet() { document.querySelector(".mira-sheet-backdrop")?.remove(); }
  function sheet(title, actions) {
    closeSheet();
    const backdrop = el("div", { class: "mira-sheet-backdrop" });
    const box = el("div", { class: "mira-sheet" }, [el("h2", { text: title })]);
    const host = el("div", { class: "mira-sheet-actions" });
    actions.forEach(([titleText, note, fn]) => {
      const button = el("button", {}, [el("strong", { text: titleText }), el("small", { class: "muted", text: note })]);
      button.addEventListener("click", () => { closeSheet(); fn(); }); host.append(button);
    });
    const close = el("button", { class: "mira-sheet-close", text: "Close" }); close.addEventListener("click", closeSheet);
    box.append(host, close); backdrop.append(box); backdrop.addEventListener("click", (event) => { if (event.target === backdrop) closeSheet(); }); document.body.append(backdrop);
  }

  function openCaptureSheet() {
    sheet("Add to MIRA", [
      ["Add item", "Create a new inventory item", () => openAssetCreate()],
      ["Scan code", "QR or barcode", () => openPanel("scan")],
      ["Take photo", "Attach a picture to an item", () => { openPanel("evidence"); setTimeout(()=>document.getElementById("photoFile")?.click(),150); }],
      ["Add receipt", "Photograph or upload a purchase", () => openPanel(document.getElementById("panel-receipts") ? "receipts" : "evidence")],
    ]);
  }

  function openMoreSheet() {
    const options = [];
    [["Organize","Categories and locations","organize"],["Files & photos","Evidence and manuals","evidence"],["Migration","Bring in existing data","migration"],["Integrations","Google and local services","integrations"],["Feature Studio","Ask MIRA to grow","features"],["Settings","Setup, updates and advanced","setup"]].forEach(([title,note,panel]) => {
      if (document.getElementById(`panel-${panel}`)) options.push([title,note,()=>openPanel(panel)]);
    });
    sheet("More", options);
  }

  function openAssetCreate() {
    openPanel("inventory");
    const details = document.getElementById("miraCreateItemDetails");
    if (details) details.open = true;
    setTimeout(()=>{ document.getElementById("newAssetName")?.focus(); details?.scrollIntoView({ behavior:"smooth", block:"start" }); },150);
  }

  function buildBottomNav() {
    if (document.querySelector(".mira-bottom-nav")) return;
    const nav = el("div", { class: "mira-bottom-nav", role: "navigation", "aria-label": "MIRA" });
    const add = (name, icon, label, fn) => { const button = el("button", { "data-shell-tab": name }, [el("span", { text: icon }), el("span", { text: label })]); button.addEventListener("click", fn); nav.append(button); };
    add("home", "⌂", "Home", () => openPanel("home"));
    add("inventory", "▦", "Inventory", () => openPanel("inventory"));
    add("capture", "＋", "Add", openCaptureSheet);
    add("more", "•••", "More", openMoreSheet);
    document.body.append(nav);
  }

  function makeAdvanced(node, label) {
    if (!node || node.closest("details")) return;
    const details = el("details", { class: "mira-advanced" });
    details.append(el("summary", { text: label }));
    node.before(details); details.append(node);
  }

  function simplifyInventory() {
    const panel = document.getElementById("panel-inventory"); if (!panel || panel.dataset.sleek === "true") return;
    panel.dataset.sleek = "true";
    const cards = [...panel.querySelectorAll(":scope > .card")];
    const find = cards.find((card) => card.querySelector("h2")?.textContent.includes("Find"));
    const create = cards.find((card) => card.querySelector("h2")?.textContent.includes("Create"));
    const selected = cards.find((card) => card.querySelector("h2")?.textContent.includes("Selected"));
    if (find) {
      find.querySelector("h2").textContent = "Inventory";
      const search = document.getElementById("assetSearch"); if (search) { search.placeholder = "Search your things"; let timer; search.addEventListener("input",()=>{clearTimeout(timer);timer=setTimeout(()=>loadAssets().catch(()=>{}),250);}); }
      const category = document.getElementById("filterCategory"), location = document.getElementById("filterLocation");
      if (category && location) {
        const details = el("details", { class: "mira-filter-details" }, [el("summary", { text: "Filters" }), el("div", { class: "mira-filter-body" })]);
        category.before(details); details.querySelector("div").append(category, location);
      }
    }
    if (create) {
      const details = el("details", { id: "miraCreateItemDetails" });
      details.append(el("summary", { text: "＋ Add a new item" }));
      [...create.children].forEach((child) => { if (child.tagName !== "H2") details.append(child); });
      create.replaceChildren(details);
      const name = document.getElementById("newAssetName"); if (name) name.placeholder = "What is it?";
      const desc = document.getElementById("newAssetDescription"); if (desc) desc.placeholder = "Notes (optional)";
      const meta = document.getElementById("newAssetMetadata"); if (meta) { meta.placeholder = "Advanced structured details"; makeAdvanced(meta, "Advanced details"); }
      const button = document.getElementById("createAsset"); if (button) button.textContent = "Add item";
    }
    if (selected) {
      selected.querySelector("h2").textContent = "Item details";
      const editMeta = document.getElementById("editAssetMetadata"); if (editMeta) makeAdvanced(editMeta.parentElement?.tagName === "LABEL" ? editMeta.parentElement : editMeta, "Advanced details");
      const raw = document.getElementById("assetResult"); if (raw) makeAdvanced(raw, "Technical record");
    }
    const oldLoadAssets = globalThis.loadAssets || loadAssets;
    globalThis.loadAssets = loadAssets = async function sleekLoadAssets() {
      const params = new URLSearchParams();
      if (document.getElementById("assetSearch")?.value.trim()) params.set("q", document.getElementById("assetSearch").value.trim());
      if (document.getElementById("filterCategory")?.value) params.set("category_uuid", document.getElementById("filterCategory").value);
      if (document.getElementById("filterLocation")?.value) params.set("location_uuid", document.getElementById("filterLocation").value);
      const result = await apiJson(`/v1/assets?${params}`);
      const list = document.getElementById("assetList"); list.replaceChildren();
      (result.assets || []).forEach((asset) => {
        const button = el("button", { class: "asset-row" }, [el("strong", { text: asset.name }), el("small", { text: `${categoryName(asset.category_uuid)} • ${locationName(asset.location_uuid)}` })]);
        button.addEventListener("click",()=>selectAsset(asset.uuid).catch(showError)); list.append(button);
      });
      if (!(result.assets || []).length) list.append(el("div", { class: "mira-empty", text: "No matching items." }));
    };
    void oldLoadAssets;
  }

  function plainLanguage() {
    const replacements = new Map([
      ["Files & photos","Photos & files"],["Cloud providers","Connections"],["Portable MIRROR export","Back up or move MIRA"],
      ["Create category","Add category"],["Create location","Add location"],["Hierarchy","Where things live"],
    ]);
    document.querySelectorAll("h2").forEach((heading)=>{ if(replacements.has(heading.textContent.trim())) heading.textContent=replacements.get(heading.textContent.trim()); });
    document.querySelectorAll("p,small,.muted").forEach((node)=>{
      if (node.children.length) return;
      node.textContent = node.textContent.replace(/immutable asset UUID/gi,"permanent item record").replace(/UUID identities/gi,"item identities").replace(/canonical UUIDs/gi,"item identities");
    });
  }

  function guardDisconnectedActions() {
    document.addEventListener("click", (event) => {
      const target = event.target.closest("#panel-migration button,#panel-providers button");
      if (!target || existingApiBase()) return;
      event.preventDefault(); event.stopImmediatePropagation();
      if (typeof setStatus === "function") setStatus("This action needs setup first. Connect MIRA and Google, then come back here.");
      showSetup();
    }, true);
  }

  function showSetup() {
    if (typeof globalThis.showOnboarding === "function") globalThis.showOnboarding(true);
    else if (document.getElementById("panel-setup")) openPanel("setup");
    else { openPanel("system"); document.getElementById("apiBase")?.focus(); }
  }

  function updateAtGlance() {
    const pendingNode = document.getElementById("miraHomePending"); if (pendingNode && typeof pending === "function") pendingNode.textContent = String(pending().length);
    const selected = document.getElementById("miraHomeSelected"); if (selected) selected.textContent = state?.selectedAsset?.name || "None";
  }

  function initialize() {
    installBrand(); buildHome(); buildBottomNav(); simplifyInventory(); plainLanguage(); guardDisconnectedActions();
    document.querySelectorAll(".panel").forEach((panel)=>panel.classList.remove("active"));
    openPanel("home");
    refreshHome().catch(()=>{}); updateAtGlance();
    const observer = new MutationObserver(()=>{ simplifyInventory(); plainLanguage(); updateAtGlance(); });
    observer.observe(document.querySelector("main") || document.body,{childList:true,subtree:true});
  }

  globalThis.MiraSleekShell = { initialize, refreshHome, showSetup, openPanel, openCaptureSheet, openMoreSheet };
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", initialize); else initialize();
})();
