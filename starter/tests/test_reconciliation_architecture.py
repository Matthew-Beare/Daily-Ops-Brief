from __future__ import annotations

import json
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]


class ReconciliationArchitectureTests(unittest.TestCase):
    def text(self, relative: str) -> str:
        return (ROOT / relative).read_text(encoding="utf-8")

    def load(self, relative: str):
        return json.loads(self.text(relative))

    def test_cleanup_is_generic_and_defaults_to_0001(self) -> None:
        contract = self.load("reconciliation-contract.json")
        planner = self.load("scheduler-planner-contract.json")
        self.assertEqual("00:01", contract["daily_cleanup"]["default_local_time"])
        self.assertTrue(contract["queue"]["generic_across_features"])
        self.assertTrue(planner["consolidation"]["features_never_create_schedules_directly"])
        self.assertEqual(5, planner["chatgpt_task_budget"]["known_plus_task_limit"])

    def test_processor_contract_supports_hybrid_local_cloud_and_openclaw(self) -> None:
        processors = self.load("ai-processor-contract.json")
        routing = self.load("model-routing-policy.json")
        kinds = set(processors["supported_processor_kinds"])
        for expected in ("chatgpt_scheduled_mira", "openai_api", "anthropic_api", "gemini_api", "local_openai_compatible", "ollama", "vllm", "llama_cpp", "openclaw", "manual"):
            self.assertIn(expected, kinds)
        self.assertTrue(routing["hard_invariants"]["local_only_never_falls_back_to_cloud"])
        self.assertTrue(routing["hard_invariants"]["user_confirmed_values_outrank_ai"])
        self.assertTrue(routing["cost"]["record_price_snapshot_per_metered_invocation"])

    def test_google_reconciliation_bootstrap_cannot_recurse_through_append(self) -> None:
        cloud = self.text("clients/pwa/reconciliation-cloud-v1.js")
        self.assertIn("ensureDefaultProcessorsDirect", cloud)
        self.assertIn("appendDirect(info, \"AIProcessors\"", cloud)
        self.assertNotIn('for (const row of defaults) await append("AIProcessors", row)', cloud)
        self.assertIn("let ensurePromise = null", cloud)
        self.assertIn("claimWork", cloud)
        self.assertIn("finishWork", cloud)
        self.assertIn("recordCorrection", cloud)
        self.assertIn("ReceiptMerchantLocationLinks", cloud)

    def test_app_explains_deferred_cleanup_and_exposes_review_and_cost(self) -> None:
        ui = self.text("clients/pwa/reconciliation-v1.js")
        self.assertIn("AI organization normally happens during Daily Cleanup, not the instant you add something", ui)
        self.assertIn("Clean up now", ui)
        self.assertIn("Needs your attention", ui)
        self.assertIn("Paid AI usage", ui)
        self.assertIn("Today:", ui)
        self.assertIn("This month:", ui)
        self.assertIn("Set up Daily Briefs", ui)

    def test_feature_studio_registers_cleanup_policy_not_automation(self) -> None:
        studio = self.text("clients/pwa/feature-studio-reconciliation-v1.js")
        self.assertIn("MIRA may need to organize new information later", studio)
        self.assertIn("This joins Daily Cleanup instead of creating another scheduled task", studio)
        self.assertIn("deferred_reconciliation", studio)
        self.assertNotIn("automations.create", studio)

    def test_google_user_correction_bridge_applies_before_old_handler(self) -> None:
        bridge = self.text("clients/pwa/reconciliation-ui-bridge-v1.js")
        index = self.text("clients/pwa/index.html")
        worker = self.text("clients/pwa/sw.js")
        self.assertIn("recordCorrection", bridge)
        self.assertIn("stopImmediatePropagation", bridge)
        self.assertIn("true);", bridge)
        self.assertIn("reconciliation-ui-bridge-v1.js", index)
        self.assertIn("reconciliation-ui-bridge-v1.js", worker)

    def test_authority_schema_contains_reconciliation_and_store_location_tables(self) -> None:
        schema = self.load("chatgpt-google-native/authority-schema.json")
        self.assertGreaterEqual(schema["schema_version"], 5)
        for table in ("ReconciliationWork", "FeatureProcessingPolicies", "AIProcessors", "AIUsage", "UserCorrections", "RecognitionProfiles", "MerchantLocations", "ReceiptMerchantLocationLinks"):
            self.assertIn(table, schema["tables"])
        rules = schema["reconciliation_rules"]
        self.assertTrue(rules["user_confirmed_values_outrank_ai_suggestions"])
        self.assertTrue(rules["local_only_work_never_silently_falls_back_to_cloud"])
        self.assertEqual("00:01", rules["default_daily_cleanup_local_time"])

    def test_google_skill_contains_no_radio_programming_architecture(self) -> None:
        skill = self.text("chatgpt-google-native/SKILL.md").lower()
        self.assertNotIn("chirp", skill)
        self.assertNotIn("radio programming", skill)
        self.assertIn("daily cleanup", skill)
        self.assertIn("user-confirmed values", skill)
        self.assertIn("openclaw", skill)


if __name__ == "__main__":
    unittest.main()
