"use strict";

(() => {
  function cloudMode() { return globalThis.MiraAuthorityCompat?.cloudMode?.() === true; }

  async function saveCloudCorrection(event) {
    if (!cloudMode() || !globalThis.MiraCloudReconciliation?.recordCorrection) return;
    event.preventDefault();
    event.stopImmediatePropagation();
    const entityType = document.getElementById("miraCorrectionType")?.value.trim();
    const entityUuid = document.getElementById("miraCorrectionId")?.value.trim();
    const field = document.getElementById("miraCorrectionField")?.value.trim();
    const value = document.getElementById("miraCorrectionValue")?.value;
    if (!entityType || !entityUuid || !field) {
      showError(new Error("Choose the record, record ID, and field you are correcting."));
      return;
    }
    try {
      const result = await globalThis.MiraCloudReconciliation.recordCorrection({
        entity_type: entityType,
        entity_uuid: entityUuid,
        field_name: field,
        confirmed_value: value,
        reason: "Corrected in MIRA app"
      });
      if (!result?.readback_verified) throw new Error("MIRROR did not verify your correction.");
      await globalThis.MiraCloudReconciliation.queueWork({
        feature_namespace: "corrections",
        source_type: entityType,
        source_uuid: entityUuid,
        work_type: "correction.verify",
        priority: 40,
        allowed_mutations: [],
        confidence_threshold: 1
      });
      setStatus(result.applied_to_record
        ? "Correction saved and read back as user-confirmed truth. AI cannot silently overwrite it."
        : "Correction was preserved as user-confirmed truth. This field will be applied during cleanup because it is not a directly editable field in this client.");
      globalThis.MiraReconciliationUI?.refresh?.().catch(() => {});
    } catch (error) { showError(error); }
  }

  function attach() {
    document.querySelectorAll("button").forEach((button) => {
      if (button.dataset.miraCorrectionBridge === "true") return;
      if (String(button.textContent || "").trim() !== "Save my correction") return;
      button.dataset.miraCorrectionBridge = "true";
      button.addEventListener("click", saveCloudCorrection, true);
    });
  }

  document.addEventListener("DOMContentLoaded", () => {
    attach();
    const observer = new MutationObserver(attach);
    observer.observe(document.documentElement, { childList: true, subtree: true });
  });
})();
