"use strict";

(() => {
  const ONBOARDING_KEY = "mira.onboarding.1.0.completed";
  const TODO_KEY = "dashboard.todo_items";
  let todoItems = [];
  let toastTimer = null;

  const icons = {
    home: '<path d="M3 11.5 12 4l9 7.5v8a1.5 1.5 0 0 1-1.5 1.5h-15A1.5 1.5 0 0 1 3 19.5z"/><path d="M9 21v-6h6v6"/>',
    box: '<path d="m4 7 8-4 8 4-8 4z"/><path d="M4 7v10l8 4 8-4V7"/><path d="M12 11v10"/>',
    scan: '<path d="M4 8V5a1 1 0 0 1 1-1h3M16 4h3a1 1 0 0 1 1 1v3M20 16v3a1 1 0 0 1-1 1h-3M8 20H5a1 1 0 0 1-1-1v-3"/><path d="M7 12h10"/>',
    more: '<circle cx="5" cy="12" r="1"/><circle cx="12" cy="12" r="1"/><circle cx="19" cy="12" r="1"/>',
    receipt: '<path d="M6 3h12v18l-3-2-3 2-3-2-3 2z"/><path d="M9 8h6M9 12h6M9 16h4"/>',
    settings: '<circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.7 1.7 0 0 0 .34 1.88l.06.06-2.83 2.83-.06-.06a1.7 1.7 0 0 0-1.88-.34 1.7 1.7 0 0 0-1.03 1.56V21h-4v-.09A1.7 1.7 0 0 0 9 19.36a1.7 1.7 0 0 0-1.88.34l-.06.06-2.83-2.83.06-.06A1.7 1.7 0 0 0 4.63 15 1.7 1.7 0 0 0 3.08 14H3v-4h.09A1.7 1.7 0 0 0 4.64 9a1.7 1.7 0 0 0-.34-1.88l-.06-.06 2.83-2.83.06.06A1.7 1.7 0 0 0 9 4.63h.01A1.7 1.7 0 0 0 10 3.08V3h4v.09A1.7 1.7 0 0 0 15 4.64a1.7 1.7 0 0 0 1.88-.34l.06-.06 2.83 2.83-.06.06A1.7 1.7 0 0 0 19.37 9v.01A1.7 1.7 0 0 0 20.92 10H21v4h-.09A1.7 1.7 0 0 0 19.4 15Z"/>',
    migrate: '<path d="M4 7h11M12 4l3 3-3 3M20 17H9M12 14l-3 3 3 3"/>',
    plug: '<path d="M8 12h8M9 3v5M15 3v5M7 8h10v3a5 5 0 0 1-10 0zM12 16v5"/>',
    spark: '<path d="m12 3 1.6 4.4L18 9l-4.4 1.6L12 15l-1.6-4.4L6 9l4.4-1.6z"/><path d="m18.5 15 .8 2.2 2.2.8-2.2.8-.8 2.2-.8-2.2-2.2-.8 2.2-.8z"/>',
    folders: '<path d="M3 7h7l2 2h9v10H3z"/><path d="M3 7V5h6l2 2"/>',
    camera: '<path d="M4 7h4l2-2h4l2 2h4v12H4z"/><circle cx="12" cy="13" r="3"/>',
    chevron: '<path d="m9 18 6-6-6-6"/>'
  };

  function svg(name) {
    const wrap = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    wrap.setAttribute("viewBox", "0 0 24 24");
    wrap.setAttribute("aria-hidden", "true");
    wrap.innerHTML = icons[name] || icons.more;
    return wrap;
  }

  function el(tag, className, text) {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (text !== undefined) node.textContent = text;
    return node;
  }

  function friendlyText(value) {
    return String(value || "")
      .replace(/immutable asset UUID/gi, "permanent item identity")
      .replace(/UUID identities/gi, "item identities")
      .replace(/UUID identity/gi, "item identity")
      .replace(/\bUUID\b/gi, "record ID")
      .replace(/\bJSON\b/g, "advanced data")
      .replace(/canonical MIRROR/gi, "MIRA")
      .replace(/MIRROR authority/gi, "MIRA data");
  }

  function installToast() {
    if (document.getElementById("miraToast")) return;
    const toast = el("div", "", "");
    toast.id = "miraToast";
    document.body.append(toast);
    if (typeof setStatus === "function") {
      const original = setStatus;
      setStatus = function sleekStatus(message) {
        const friendly = friendlyText(message);
        original(friendly);
        toast.textContent = friendly;
        toast.classList.add("show");
        clearTimeout(toastTimer);
        toastTimer = setTimeout(() => toast.classList.remove("show"), 3200);
      };
    }
  }

  function installBrandHeader() {
    const header = document.querySelector("header");
    if (!header || header.querySelector(".mira-shell-head")) return;
    const shell = el("div", "mira-shell-head");
    const logo = document.createElement("img");
    logo.src = "brand-wordmark.svg";
    logo.alt = "MIRA — Reflecting reality";
    logo.className = "mira-brand-lockup";
    const account = el("button", "mira-account-dot", "ME");
    account.type = "button";
    account.setAttribute("aria-label", "Open setup and settings");
    account.addEventListener("click", () => go("setup"));
    shell.append(logo, account);
    header.prepend(shell);
  }

  function navButton(name, label, iconName) {
    const button = document.createElement("button");
    button.type = "button";
    button.dataset.primary = name;
    button.append(svg(iconName), el("span", "nav-label", label));
    button.addEventListener("click", () => go(name));
    return button;
  }

  function installPrimaryNav() {
    if (document.querySelector(".mira-primary-nav")) return;
    const nav = el("nav", "mira-primary-nav");
    nav.setAttribute("aria-label", "Main navigation");
    nav.append(
      navButton("home", "Home", "home"),
      navButton("inventory", "Inventory", "box"),
      navButton("scan", "Scan", "scan"),
      navButton("more", "More", "more")
    );
    const main = document.querySelector("main");
    main?.before(nav);
  }

  function setPrimarySelected(name) {
    document.querySelectorAll(".mira-primary-nav [data-primary]").forEach((button) => {
      button.setAttribute("aria-selected", String(button.dataset.primary === name));
    });
  }

  function go(name) {
    if (name === "home" || name === "more") {
      document.querySelectorAll(".panel").forEach((panel) => panel.classList.toggle("active", panel.id === `panel-${name}`));
      setPrimarySelected(name);
      window.scrollTo({ top: 0, behavior: "smooth" });
      if (name === "home") refreshHome().catch(() => {});
      return;
    }
    if (typeof switchTab === "function") switchTab(name);
    setPrimarySelected(name === "inventory" || name === "scan" ? name : "more");
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  function quickAction(label, iconName, action) {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "mira-quick-action";
    button.append(svg(iconName), el("span", "", label));
    button.addEventListener("click", action);
    return button;
  }

  function onboardingComplete() {
    return localStorage.getItem(ONBOARDING_KEY) === "true";
  }

  function showSetup() {
    if (globalThis.MiraV1?.showOnboarding) globalThis.MiraV1.showOnboarding();
    else go("setup");
  }

  async function readSettings() {
    if (typeof apiBase !== "function" || !apiBase()) return {};
    try {
      const result = await apiJson("/v1/settings");
      return result.settings || {};
    } catch (_) {
      return {};
    }
  }

  async function writeTodo() {
    if (typeof apiBase !== "function" || !apiBase()) throw new Error("Finish setup before adding shared tasks.");
    await apiJson("/v1/settings", {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ settings: { [TODO_KEY]: todoItems } })
    });
  }

  function renderTodo() {
    const host = document.getElementById("miraTodoList");
    if (!host) return;
    host.replaceChildren();
    if (!todoItems.length) {
      const empty = el("div", "muted", onboardingComplete() ? "Nothing waiting. Add something below." : "Finish setup first. Your shared list will live here.");
      host.append(empty);
      return;
    }
    todoItems.forEach((item, index) => {
      const row = el("label", `mira-todo-item${item.done ? " done" : ""}`);
      const checkbox = document.createElement("input");
      checkbox.type = "checkbox";
      checkbox.checked = Boolean(item.done);
      checkbox.addEventListener("change", async () => {
        item.done = checkbox.checked;
        renderTodo();
        try { await writeTodo(); } catch (error) { showError(error); }
      });
      const text = el("span", "", item.text);
      const remove = el("button", "", "×");
      remove.type = "button";
      remove.setAttribute("aria-label", `Remove ${item.text}`);
      remove.style.minHeight = "34px";
      remove.style.width = "34px";
      remove.style.padding = "0";
      remove.addEventListener("click", async (event) => {
        event.preventDefault();
        todoItems.splice(index, 1);
        renderTodo();
        try { await writeTodo(); } catch (error) { showError(error); }
      });
      row.append(checkbox, text, remove);
      host.append(row);
    });
  }

  async function addTodo() {
    const input = document.getElementById("miraTodoInput");
    const text = input?.value.trim();
    if (!text) return;
    if (!onboardingComplete() || !apiBase()) {
      showSetup();
      throw new Error("Finish setup first so your list is saved with MIRA instead of only on this device.");
    }
    todoItems.unshift({ text, done: false, created_at: new Date().toISOString() });
    input.value = "";
    renderTodo();
    await writeTodo();
    setStatus("Added to your list.");
  }

  function buildHome() {
    if (document.getElementById("panel-home")) return;
    const panel = el("section", "panel");
    panel.id = "panel-home";

    const hero = el("div", "mira-home-hero");
    hero.append(el("div", "mira-home-eyebrow", "Upcoming"));
    const heroTitle = el("h2", "", "Your day, at a glance.");
    heroTitle.id = "miraHeroTitle";
    const heroText = el("p", "", "Appointments, reminders, deliveries, maintenance, tasks and anything else MIRA thinks deserves your attention land here.");
    heroText.id = "miraHeroText";
    const heroAction = el("button", "mira-hero-action", "View upcoming");
    heroAction.id = "miraHeroAction";
    heroAction.type = "button";
    heroAction.addEventListener("click", () => {
      if (!onboardingComplete()) showSetup();
      else document.getElementById("miraUpcomingCard")?.scrollIntoView({ behavior: "smooth", block: "center" });
    });
    hero.append(heroTitle, heroText, heroAction);

    const quick = el("div", "mira-quick-grid");
    quick.append(
      quickAction("Scan", "scan", () => go("scan")),
      quickAction("Add item", "box", () => { go("inventory"); setTimeout(() => openAddItem(), 80); }),
      quickAction("Receipt", "receipt", () => go("receipts"))
    );

    const todo = el("div", "card mira-todo-card");
    const todoHead = el("div", "mira-section-head");
    todoHead.append(el("h2", "", "To-do"), el("span", "muted", "Shared with MIRA"));
    const todoList = el("div", "mira-todo-list");
    todoList.id = "miraTodoList";
    const addRow = el("div", "mira-add-row");
    const input = document.createElement("input");
    input.id = "miraTodoInput";
    input.placeholder = "Add something…";
    input.addEventListener("keydown", (event) => { if (event.key === "Enter") addTodo().catch(showError); });
    const add = el("button", "primary-action", "Add");
    add.type = "button";
    add.addEventListener("click", () => addTodo().catch(showError));
    addRow.append(input, add);
    todo.append(todoHead, todoList, addRow);

    const upcoming = el("div", "card mira-glance-card");
    upcoming.id = "miraUpcomingCard";
    upcoming.append(el("h2", "", "Next up"));
    const list = el("div", "mira-upcoming-list");
    list.id = "miraUpcomingList";
    upcoming.append(list);

    panel.append(hero, quick, todo, upcoming);
    document.querySelector("main")?.prepend(panel);
  }

  function renderUpcoming(settings) {
    const list = document.getElementById("miraUpcomingList");
    if (!list) return;
    list.replaceChildren();
    if (!onboardingComplete()) {
      const item = el("div", "mira-upcoming-item");
      item.append(el("strong", "", "Finish setting up MIRA"), el("small", "", "Connect Google and choose what you want MIRA to watch."));
      list.append(item);
      return;
    }
    const rows = Array.isArray(settings["dashboard.upcoming_items"]) ? settings["dashboard.upcoming_items"] : [];
    if (!rows.length) {
      const item = el("div", "mira-upcoming-item");
      item.append(el("strong", "", "Nothing urgent"), el("small", "", "Appointments, reminders, deliveries and maintenance will appear here as integrations populate them."));
      list.append(item);
      return;
    }
    rows.slice(0, 5).forEach((row) => {
      const item = el("div", "mira-upcoming-item");
      item.append(el("strong", "", row.title || "Upcoming"), el("small", "", row.when || row.detail || ""));
      list.append(item);
    });
  }

  async function refreshHome() {
    const settings = await readSettings();
    todoItems = Array.isArray(settings[TODO_KEY]) ? settings[TODO_KEY] : [];
    renderTodo();
    renderUpcoming(settings);
    const title = document.getElementById("miraHeroTitle");
    const text = document.getElementById("miraHeroText");
    const action = document.getElementById("miraHeroAction");
    if (!onboardingComplete()) {
      if (title) title.textContent = "Finish setup.";
      if (text) text.textContent = "Connect Google once, choose what matters to you, and MIRA will start turning this screen into your daily command center.";
      if (action) action.textContent = "Finish setup";
    } else {
      if (title) title.textContent = "Your day, at a glance.";
      if (text) text.textContent = "The important stuff first. Everything else stays out of your way until you need it.";
      if (action) action.textContent = "View upcoming";
    }
  }

  function menuItem(label, description, iconName, target) {
    const button = el("button", "mira-menu-item");
    button.type = "button";
    const copy = el("span", "");
    copy.append(el("strong", "", label), el("small", "", description));
    button.append(svg(iconName), copy, el("span", "mira-chevron", "›"));
    button.addEventListener("click", () => go(target));
    return button;
  }

  function buildMore() {
    if (document.getElementById("panel-more")) return;
    const panel = el("section", "panel");
    panel.id = "panel-more";
    const groups = el("div", "mira-more-groups");

    const everyday = el("div", "mira-more-group");
    everyday.append(el("h2", "", "Everyday"));
    const everydayList = el("div", "mira-menu-list");
    everydayList.append(
      menuItem("Receipts", "Photograph, reconcile and attach purchases", "receipt", "receipts"),
      menuItem("Organize", "Categories, shelves, totes and locations", "folders", "organize"),
      menuItem("Photos & files", "Pictures, manuals and supporting evidence", "camera", "evidence")
    );
    everyday.append(everydayList);

    const system = el("div", "mira-more-group");
    system.append(el("h2", "", "Build & connect"));
    const systemList = el("div", "mira-menu-list");
    systemList.append(
      menuItem("Integrations", "Google and optional local services", "plug", "integrations"),
      menuItem("Bring in existing data", "Guided Google migration and imports", "migrate", "migration"),
      menuItem("Feature Studio", "Describe what you want MIRA to learn next", "spark", "features"),
      menuItem("Setup & settings", "Preferences, updates and advanced options", "settings", "setup")
    );
    system.append(systemList);
    groups.append(everyday, system);
    panel.append(groups);
    document.querySelector("main")?.append(panel);
  }

  function wrapAdvanced(nodeToWrap, label = "Advanced") {
    if (!nodeToWrap || nodeToWrap.closest("details")) return;
    const details = document.createElement("details");
    details.className = "mira-technical-details";
    const summary = document.createElement("summary");
    summary.textContent = label;
    nodeToWrap.parentNode?.insertBefore(details, nodeToWrap);
    details.append(summary, nodeToWrap);
  }

  function openAddItem() {
    const card = document.querySelector("#panel-inventory .mira-create-collapsed");
    card?.classList.add("mira-open");
    document.getElementById("newAssetName")?.focus();
    card?.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  function simplifyInventory() {
    const panel = document.getElementById("panel-inventory");
    if (!panel || panel.dataset.sleek === "true") return;
    panel.dataset.sleek = "true";
    const cards = [...panel.querySelectorAll(":scope > .card")];
    if (cards.length < 3) return;
    const [searchCard, createCard, selectedCard] = cards;

    const toolbar = el("div", "mira-inventory-toolbar");
    toolbar.append(el("h2", "", "Inventory"));
    const add = el("button", "primary-action", "+ Add item");
    add.type = "button";
    add.addEventListener("click", openAddItem);
    toolbar.append(add);
    panel.prepend(toolbar);

    searchCard.querySelector("h2")?.remove();
    const search = document.getElementById("assetSearch");
    if (search) {
      search.placeholder = "Search your stuff";
      let timer;
      search.addEventListener("input", () => {
        clearTimeout(timer);
        timer = setTimeout(() => { if (typeof loadAssets === "function") loadAssets().catch(showError); }, 260);
      });
    }
    const category = document.getElementById("filterCategory");
    const location = document.getElementById("filterLocation");
    if (category && location) {
      const details = document.createElement("details");
      details.className = "mira-filter-details";
      const summary = document.createElement("summary");
      summary.textContent = "Filters";
      category.parentNode?.insertBefore(details, category);
      details.append(summary, category, location);
      category.addEventListener("change", () => loadAssets().catch(showError));
      location.addEventListener("change", () => loadAssets().catch(showError));
    }

    createCard.classList.add("mira-create-collapsed");
    const createHeading = createCard.querySelector("h2");
    if (createHeading) createHeading.textContent = "Add item";
    const name = document.getElementById("newAssetName"); if (name) name.placeholder = "What is it?";
    const desc = document.getElementById("newAssetDescription"); if (desc) desc.placeholder = "Model, notes or anything useful";
    const create = document.getElementById("createAsset"); if (create) create.textContent = "Save item";
    const metadata = document.getElementById("newAssetMetadata");
    if (metadata) {
      metadata.placeholder = "Optional advanced fields";
      const details = document.createElement("details");
      const summary = document.createElement("summary");
      summary.textContent = "Advanced details";
      metadata.parentNode?.insertBefore(details, metadata);
      details.append(summary, metadata);
    }
    const cancel = el("button", "", "Cancel");
    cancel.type = "button";
    cancel.addEventListener("click", () => createCard.classList.remove("mira-open"));
    createCard.querySelector(".row")?.append(cancel);

    const selectedHeading = selectedCard.querySelector("h2");
    if (selectedHeading) selectedHeading.textContent = "Item details";
    const editMetadata = document.getElementById("editAssetMetadata");
    if (editMetadata) {
      const label = editMetadata.closest("label");
      if (label) {
        label.firstChild.textContent = "Advanced details";
        wrapAdvanced(label, "Advanced details");
      }
    }
    const raw = document.getElementById("assetResult");
    if (raw) wrapAdvanced(raw, "Technical record");
  }

  function hideTechnicalCopy() {
    document.querySelectorAll("input[placeholder], textarea[placeholder]").forEach((input) => {
      input.placeholder = friendlyText(input.placeholder)
        .replace(/Search name, description or record ID/i, "Search your stuff")
        .replace(/Optional metadata advanced data, e\.g\..*/i, "Optional advanced details");
    });
    document.querySelectorAll("button,summary,h2,h3,p,small,label").forEach((node) => {
      if (node.childElementCount === 0 && /UUID|JSON/.test(node.textContent || "")) node.textContent = friendlyText(node.textContent);
    });
    ["providerStatus", "treeResult", "platformCapabilityStatus", "migrationResult", "migrationMagicResult"].forEach((id) => {
      const item = document.getElementById(id);
      if (item) wrapAdvanced(item, "Technical details");
    });
  }

  function installMutationObserver() {
    const observer = new MutationObserver(() => {
      simplifyInventory();
      hideTechnicalCopy();
    });
    observer.observe(document.documentElement, { childList: true, subtree: true });
  }

  function initializeSleekShell() {
    installToast();
    installBrandHeader();
    installPrimaryNav();
    buildHome();
    buildMore();
    simplifyInventory();
    hideTechnicalCopy();
    installMutationObserver();
    go("home");
    refreshHome().catch(() => {});
  }

  document.addEventListener("DOMContentLoaded", () => setTimeout(initializeSleekShell, 40));
  globalThis.MiraShell = { go, refreshHome, openAddItem };
})();
