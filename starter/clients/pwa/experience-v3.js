"use strict";

(() => {
  const PRIMARY_ONBOARDING_KEY = "mira.onboarding.1.0.completed";
  const PERSONALIZE_KEY = "mira.onboarding.personalize-v3.completed";
  const LOCAL_PREFS_KEY = "mira.preferences.v3";
  let wakeLock = null;

  const defaults = {
    "features.meal_planning": true,
    "health.enabled": false,
    "health.goal": "none",
    "health.current_weight": null,
    "health.goal_weight": null,
    "health.weight_unit": "lb",
    "health.age": null,
    "health.sex": "prefer_not_to_say",
    "health.exercise": "none",
    "health.connected_sources": [],
    "recipes.collection_sources": [],
    "weather.display": "off",
    "weather.location": "",
    "weather.source": "automatic",
    "notifications.push_enabled": false,
    "kiosk.enabled": false,
    "kiosk.keep_awake": true,
    "shopping.purchase_insights": false,
    "shopping.sales_coupons": false,
  };

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

  function apiReady() {
    try { return typeof apiBase === "function" && Boolean(apiBase()); } catch (_) { return false; }
  }

  function localPrefs() {
    try { return { ...defaults, ...JSON.parse(localStorage.getItem(LOCAL_PREFS_KEY) || "{}") }; }
    catch (_) { return { ...defaults }; }
  }

  function saveLocal(patch) {
    localStorage.setItem(LOCAL_PREFS_KEY, JSON.stringify({ ...localPrefs(), ...patch }));
  }

  async function loadPreferences() {
    const local = localPrefs();
    if (!apiReady()) return local;
    try {
      const result = await apiJson("/v1/preferences");
      const merged = { ...local, ...(result.preferences || {}) };
      saveLocal(merged);
      return merged;
    } catch (_) {
      return local;
    }
  }

  async function savePreferences(patch) {
    saveLocal(patch);
    if (!apiReady()) {
      globalThis.MiraActionAudit?.announce?.("Saved on this device. Finish setup to sync these choices through MIRROR.");
      return localPrefs();
    }
    const result = await apiJson("/v1/preferences", {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ preferences: patch }),
    });
    saveLocal(result.preferences || patch);
    globalThis.MiraActionAudit?.announce?.("Preferences saved.");
    return result.preferences || patch;
  }

  function field(label, input) {
    return el("label", { class: "mira-pref-field" }, [el("span", { text: label }), input]);
  }

  function select(options, value = "") {
    const node = document.createElement("select");
    options.forEach(([v, label]) => node.add(new Option(label, v)));
    node.value = value;
    return node;
  }

  function checkbox(label, checked = false) {
    const input = el("input", { type: "checkbox", checked });
    return { input, wrapper: el("label", { class: "mira-pref-check" }, [input, el("span", { text: label })]) };
  }

  function explainMiraMirror() {
    document.querySelectorAll("#miraV1Onboarding .step").forEach((step, index) => {
      if (index !== 0) return;
      const heading = step.querySelector("h3");
      const paragraph = step.querySelector("p");
      if (heading) heading.textContent = "Meet MIRA";
      if (paragraph) paragraph.textContent = "MIRA is the assistant you talk to. MIRROR is the private data and evidence underneath MIRA. The MIRA app is mainly a dashboard and capture tool for that system.";
      if (!step.querySelector(".mira-simple-explainer")) {
        step.append(el("div", { class: "mira-simple-explainer", html: "<strong>MIRA</strong><span>Assistant</span><strong>MIRROR</strong><span>Your private data &amp; evidence</span><strong>MIRA app</strong><span>Display &amp; capture</span>" }));
      }
    });
    document.querySelectorAll(".mira-v1-brand").forEach((brand) => { brand.textContent = "MIRA • MIRROR keeps the facts"; });
  }

  function splitSources(value) {
    return [...new Set(String(value || "").split(/[,\n]/).map((item) => item.trim()).filter(Boolean))].slice(0, 50);
  }

  async function showPersonalize(force = false) {
    if (!force && localStorage.getItem(PERSONALIZE_KEY) === "true") return;
    if (document.getElementById("miraPersonalizeV3")) return;
    const prefs = await loadPreferences();

    const overlay = el("div", { id: "miraPersonalizeV3", class: "mira-v1-overlay" });
    const dialog = el("div", { class: "mira-v1-dialog mira-personalize-dialog" });
    const logo = el("img", { src: "brand-wordmark.svg", alt: "MIRA", class: "mira-personalize-logo" });
    dialog.append(
      logo,
      el("h2", { text: "Optional MIRA preferences" }),
      el("p", { class: "muted", text: "The app stays a dashboard and capture tool. These choices simply tell the wider MIRA/MIRROR system what it may display or use." })
    );

    const meal = checkbox("Use meal planning in MIRA", prefs["features.meal_planning"] !== false);
    const recipeSources = el("textarea", { rows: "2", placeholder: "Optional recipe collections, one per line or comma-separated" });
    recipeSources.value = (prefs["recipes.collection_sources"] || []).join("\n");

    const health = checkbox("I want MIRA to use health or nutrition goals", Boolean(prefs["health.enabled"]));
    const healthFields = el("div", { class: "mira-health-fields", hidden: !health.input.checked });
    const goal = select([["none","No specific goal"],["maintain","Maintain weight"],["lose","Lose weight"],["gain","Gain weight"],["general_nutrition","Improve nutrition"]], prefs["health.goal"] || "none");
    const weightUnit = select([["lb","lb"],["kg","kg"]], prefs["health.weight_unit"] || "lb");
    const currentWeight = el("input", { type: "number", min: "20", max: "1500", step: "0.1", placeholder: "Optional" });
    const goalWeight = el("input", { type: "number", min: "20", max: "1500", step: "0.1", placeholder: "Optional" });
    const age = el("input", { type: "number", min: "0", max: "130", placeholder: "Optional" });
    currentWeight.value = prefs["health.current_weight"] ?? "";
    goalWeight.value = prefs["health.goal_weight"] ?? "";
    age.value = prefs["health.age"] ?? "";
    const sex = select([["prefer_not_to_say","Prefer not to say"],["female","Female"],["male","Male"],["intersex","Intersex"],["self_describe","Self describe later"]], prefs["health.sex"] || "prefer_not_to_say");
    const exercise = select([["none","No regular exercise"],["cardio","Cardio"],["strength","Strength"],["both","Cardio + strength"],["other","Other"]], prefs["health.exercise"] || "none");
    const tracker = el("input", { placeholder: "Optional connected tracker or calorie app" });
    tracker.value = (prefs["health.connected_sources"] || []).join(", ");
    healthFields.append(
      field("Goal", goal),
      el("div", { class: "split" }, [field("Current weight", currentWeight), field("Goal weight", goalWeight), field("Units", weightUnit)]),
      el("div", { class: "split" }, [field("Age", age), field("Sex (optional)", sex), field("Exercise", exercise)]),
      field("Connected health source", tracker)
    );
    health.input.addEventListener("change", () => { healthFields.hidden = !health.input.checked; });

    const weatherMode = select([["off","No weather"],["morning","Morning only"],["all_day","Show all day"]], prefs["weather.display"] || "off");
    const weatherLocation = el("input", { placeholder: "City, ZIP/postcode, or saved location" });
    weatherLocation.value = prefs["weather.location"] || "";
    const weatherSource = select([["automatic","Automatic"],["nws","National Weather Service"],["weather_channel","The Weather Channel"],["accuweather","AccuWeather"]], prefs["weather.source"] || "automatic");

    const notifications = checkbox("Allow notifications on this installed device", Boolean(prefs["notifications.push_enabled"]));
    const kiosk = checkbox("Use this device as an always-on wall / fridge display", Boolean(prefs["kiosk.enabled"]));
    const purchaseInsights = checkbox("Use opted-in purchase history to learn what and where I buy", Boolean(prefs["shopping.purchase_insights"]));
    const coupons = checkbox("Use those opted-in shopping patterns to look for relevant sales/coupons", Boolean(prefs["shopping.sales_coupons"]));

    dialog.append(
      el("div", { class: "mira-pref-section" }, [el("h3", { text: "Meals" }), meal.wrapper, field("Recipe collections", recipeSources)]),
      el("div", { class: "mira-pref-section" }, [el("h3", { text: "Health (optional)" }), health.wrapper, healthFields, el("p", { class: "muted", text: "Weight, age, sex and exercise are optional and only used when this feature is on." })]),
      el("div", { class: "mira-pref-section" }, [el("h3", { text: "Dashboard" }), field("Weather", weatherMode), field("Weather location", weatherLocation), field("Weather source", weatherSource), kiosk.wrapper, notifications.wrapper]),
      el("div", { class: "mira-pref-section" }, [el("h3", { text: "Shopping (opt-in)" }), purchaseInsights.wrapper, coupons.wrapper, el("p", { class: "muted", text: "No advertising profile and no sale of shopping history." })])
    );

    const cancel = el("button", { type: "button", text: "Not now" });
    const save = el("button", { type: "button", class: "primary-action", text: "Save preferences" });
    cancel.addEventListener("click", () => { localStorage.setItem(PERSONALIZE_KEY, "true"); overlay.remove(); });
    save.addEventListener("click", async () => {
      const healthOn = health.input.checked;
      const purchaseOn = purchaseInsights.input.checked;
      const patch = {
        "features.meal_planning": meal.input.checked,
        "recipes.collection_sources": splitSources(recipeSources.value),
        "health.enabled": healthOn,
        "health.goal": healthOn ? goal.value : "none",
        "health.current_weight": healthOn && currentWeight.value ? Number(currentWeight.value) : null,
        "health.goal_weight": healthOn && goalWeight.value ? Number(goalWeight.value) : null,
        "health.weight_unit": weightUnit.value,
        "health.age": healthOn && age.value ? Number(age.value) : null,
        "health.sex": healthOn ? sex.value : "prefer_not_to_say",
        "health.exercise": healthOn ? exercise.value : "none",
        "health.connected_sources": healthOn ? splitSources(tracker.value) : [],
        "weather.display": weatherMode.value,
        "weather.location": weatherLocation.value.trim(),
        "weather.source": weatherSource.value,
        "notifications.push_enabled": notifications.input.checked,
        "kiosk.enabled": kiosk.input.checked,
        "shopping.purchase_insights": purchaseOn,
        "shopping.sales_coupons": purchaseOn && coupons.input.checked,
      };
      try {
        await savePreferences(patch);
        localStorage.setItem(PERSONALIZE_KEY, "true");
        overlay.remove();
        if (patch["notifications.push_enabled"]) await requestNotifications();
        if (patch["kiosk.enabled"]) await enableKiosk(false); else await disableKiosk(false);
        await refreshExperience();
      } catch (error) {
        globalThis.MiraActionAudit?.announce?.(error);
      }
    });
    dialog.append(el("div", { class: "mira-v1-footer" }, [cancel, save]));
    overlay.append(dialog);
    document.body.append(overlay);
  }

  function maybeStartPersonalize() {
    if (localStorage.getItem(PRIMARY_ONBOARDING_KEY) !== "true" || localStorage.getItem(PERSONALIZE_KEY) === "true") return;
    if (document.getElementById("miraV1Onboarding")) return;
    showPersonalize(false).catch(() => {});
  }

  async function requestNotifications() {
    if (!("Notification" in globalThis)) {
      globalThis.MiraActionAudit?.announce?.("This browser cannot provide web notifications. The installed Android client can still use native reminders.");
      return false;
    }
    const permission = Notification.permission === "granted" ? "granted" : await Notification.requestPermission();
    if (permission !== "granted") {
      await savePreferences({ "notifications.push_enabled": false });
      return false;
    }
    await savePreferences({ "notifications.push_enabled": true });
    return true;
  }

  async function acquireWakeLock() {
    if (!document.documentElement.classList.contains("mira-kiosk")) return;
    const prefs = localPrefs();
    if (!prefs["kiosk.keep_awake"] || !("wakeLock" in navigator)) return;
    try {
      wakeLock = await navigator.wakeLock.request("screen");
      wakeLock.addEventListener("release", () => { wakeLock = null; });
    } catch (_) { /* optional platform feature */ }
  }

  async function enableKiosk(requestFullscreen = true) {
    document.documentElement.classList.add("mira-kiosk");
    await savePreferences({ "kiosk.enabled": true });
    await acquireWakeLock();
    if (requestFullscreen && document.documentElement.requestFullscreen) {
      try { await document.documentElement.requestFullscreen(); } catch (_) { /* optional */ }
    }
    installKioskExit();
  }

  async function disableKiosk(saveState = true) {
    document.documentElement.classList.remove("mira-kiosk");
    if (wakeLock) { try { await wakeLock.release(); } catch (_) {} wakeLock = null; }
    if (document.fullscreenElement && document.exitFullscreen) { try { await document.exitFullscreen(); } catch (_) {} }
    if (saveState) await savePreferences({ "kiosk.enabled": false });
    document.getElementById("miraKioskExit")?.remove();
  }

  function installKioskExit() {
    if (document.getElementById("miraKioskExit")) return;
    const button = el("button", { id: "miraKioskExit", type: "button", text: "Exit wall display" });
    button.addEventListener("click", () => disableKiosk(true).catch((error) => globalThis.MiraActionAudit?.announce?.(error)));
    document.body.append(button);
  }

  function installSetupCard() {
    const panel = document.getElementById("panel-setup");
    if (!panel || document.getElementById("miraExperienceSettings")) return;
    const card = el("div", { id: "miraExperienceSettings", class: "card" }, [
      el("h2", { text: "Display & optional preferences" }),
      el("p", { class: "muted", text: "The app remains a dashboard and capture tool. Change weather, wall-display, meal, health and shopping opt-ins here." })
    ]);
    const personalize = el("button", { type: "button", text: "Change optional preferences" });
    personalize.addEventListener("click", () => showPersonalize(true).catch((error) => globalThis.MiraActionAudit?.announce?.(error)));
    const wall = el("button", { type: "button", text: "Start wall / fridge display" });
    wall.addEventListener("click", () => enableKiosk(true).catch((error) => globalThis.MiraActionAudit?.announce?.(error)));
    card.append(el("div", { class: "actions" }, [personalize, wall]));
    panel.append(card);
  }

  function installWeatherCard(prefs) {
    let card = document.getElementById("miraWeatherCard");
    if (prefs["weather.display"] === "off") { card?.remove(); return; }
    const home = document.getElementById("panel-home");
    if (!home) return;
    if (!card) {
      card = el("div", { id: "miraWeatherCard", class: "card mira-weather-card" });
      home.append(card);
    }
    const provider = { automatic: "Automatic", nws: "National Weather Service", weather_channel: "The Weather Channel", accuweather: "AccuWeather" }[prefs["weather.source"]] || "Automatic";
    card.replaceChildren(
      el("div", { class: "mira-section-head" }, [el("h2", { text: "Weather" }), el("span", { class: "muted", text: prefs["weather.display"] === "morning" ? "Morning" : "All day" })]),
      el("strong", { text: prefs["weather.location"] || "Choose a location" }),
      el("p", { class: "muted", text: `Preferred source: ${provider}. Verified conditions appear here when that source is connected.` })
    );
  }

  async function refreshExperience() {
    const prefs = await loadPreferences();
    installSetupCard();
    installWeatherCard(prefs);
    if (prefs["kiosk.enabled"]) {
      document.documentElement.classList.add("mira-kiosk");
      installKioskExit();
      await acquireWakeLock();
    }
  }

  function initialize() {
    explainMiraMirror();
    installSetupCard();
    refreshExperience().catch(() => {});
    setTimeout(maybeStartPersonalize, 700);
    const observer = new MutationObserver(() => {
      explainMiraMirror();
      installSetupCard();
      if (!document.getElementById("miraV1Onboarding")) setTimeout(maybeStartPersonalize, 120);
    });
    observer.observe(document.documentElement, { childList: true, subtree: true });
    document.addEventListener("visibilitychange", () => {
      if (!document.hidden && document.documentElement.classList.contains("mira-kiosk")) acquireWakeLock().catch(() => {});
    });
  }

  globalThis.MiraExperienceV3 = { loadPreferences, savePreferences, refreshExperience, showPersonalize, enableKiosk, disableKiosk };
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", () => setTimeout(initialize, 120)); else setTimeout(initialize, 120);
})();
