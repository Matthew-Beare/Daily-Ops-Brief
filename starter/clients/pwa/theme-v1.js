"use strict";

(() => {
  const KEY = "mira.appearance";
  const VALID = new Set(["system", "dark", "light"]);
  const media = globalThis.matchMedia?.("(prefers-color-scheme: dark)");

  function preference() {
    const value = localStorage.getItem(KEY) || "system";
    return VALID.has(value) ? value : "system";
  }

  function effective(value = preference()) {
    if (value === "system") return media?.matches ? "dark" : "light";
    return value;
  }

  function updateNative(theme) {
    try {
      if (globalThis.MirrorNative?.setAppearance) globalThis.MirrorNative.setAppearance(theme);
    } catch (_) {}
  }

  function updateControls() {
    const selected = preference();
    document.querySelectorAll("[data-mira-appearance]").forEach((button) => {
      button.setAttribute("aria-pressed", String(button.dataset.miraAppearance === selected));
    });
    const toggle = document.getElementById("miraThemeToggle");
    if (toggle) {
      const current = effective(selected);
      toggle.textContent = current === "dark" ? "☀" : "☾";
      toggle.title = current === "dark" ? "Use light mode" : "Use dark mode";
      toggle.setAttribute("aria-label", toggle.title);
    }
  }

  function apply(value, persist = true) {
    const selected = VALID.has(value) ? value : "system";
    if (persist) localStorage.setItem(KEY, selected);
    const theme = effective(selected);
    document.documentElement.dataset.miraTheme = theme;
    document.documentElement.dataset.miraThemePreference = selected;
    const meta = document.querySelector('meta[name="theme-color"]');
    if (meta) meta.content = theme === "dark" ? "#07101d" : "#f3f6fb";
    updateNative(theme);
    updateControls();
    globalThis.dispatchEvent(new CustomEvent("mira:appearance", { detail: { preference: selected, theme } }));
  }

  function button(value, label) {
    const item = document.createElement("button");
    item.type = "button";
    item.dataset.miraAppearance = value;
    item.textContent = label;
    item.addEventListener("click", () => apply(value));
    return item;
  }

  function installHeaderToggle() {
    const shell = document.querySelector(".mira-shell-head");
    if (!shell || document.getElementById("miraThemeToggle")) return false;
    let actions = shell.querySelector(".mira-shell-actions");
    const account = shell.querySelector(".mira-account-dot");
    if (!actions) {
      actions = document.createElement("div");
      actions.className = "mira-shell-actions";
      if (account) {
        shell.insertBefore(actions, account);
        actions.append(account);
      } else shell.append(actions);
    }
    const toggle = document.createElement("button");
    toggle.type = "button";
    toggle.id = "miraThemeToggle";
    toggle.className = "mira-theme-toggle";
    toggle.addEventListener("click", () => apply(effective() === "dark" ? "light" : "dark"));
    actions.insertBefore(toggle, actions.firstChild);
    updateControls();
    return true;
  }

  function installSettingsCard() {
    const panel = document.getElementById("panel-system");
    if (!panel || document.getElementById("miraAppearanceCard")) return false;
    const card = document.createElement("div");
    card.className = "card mira-appearance-card";
    card.id = "miraAppearanceCard";
    const title = document.createElement("h2");
    title.textContent = "Appearance";
    const copy = document.createElement("p");
    copy.className = "muted";
    copy.textContent = "Choose how MIRA looks on this device.";
    const options = document.createElement("div");
    options.className = "mira-appearance-options";
    options.append(button("system", "Use device setting"), button("dark", "Dark"), button("light", "Light"));
    card.append(title, copy, options);
    panel.prepend(card);
    updateControls();
    return true;
  }

  function install() {
    apply(preference(), false);
    installHeaderToggle();
    installSettingsCard();
    const observer = new MutationObserver(() => {
      const a = installHeaderToggle();
      const b = installSettingsCard();
      if (a || b) updateControls();
    });
    observer.observe(document.documentElement, { childList: true, subtree: true });
  }

  if (media?.addEventListener) media.addEventListener("change", () => { if (preference() === "system") apply("system", false); });
  document.addEventListener("DOMContentLoaded", () => setTimeout(install, 90));
  globalThis.MiraAppearance = { apply, preference, effective };
})();
