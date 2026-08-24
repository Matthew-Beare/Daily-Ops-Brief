from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools" / "onboarding_profile_router.py"
SPEC = importlib.util.spec_from_file_location("onboarding_profile_router", MODULE_PATH)
assert SPEC and SPEC.loader
router = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(router)


class OnboardingProfileRouterTests(unittest.TestCase):
    def test_retired_parent_style_profile_bypasses_work_mode_and_surfaces_appointments(self) -> None:
        result = router.resolve({
            "employment_status": "retired",
            "profile_alias": "Dad",
            "appointment_tracking": True,
            "briefs_enabled": True,
        })
        self.assertEqual("retired_nonworking", result["life_profile"])
        self.assertEqual("Dad", result["profile_alias"])
        self.assertEqual("private-mutable-state", result["profile_alias_storage"])
        self.assertEqual("bypassed", result["context"]["status"])
        self.assertIn("appointments", result["brief_focus"])

    def test_long_haul_trucker_recommends_home_road_but_does_not_silently_select(self) -> None:
        result = router.resolve({
            "employment_status": "working",
            "job_title": "long-haul truck driver",
            "works_away_from_home": True,
        })
        self.assertEqual("recommended", result["context"]["status"])
        self.assertEqual(["HOME", "ROAD"], result["context"]["primary_modes"])
        self.assertIn(["HOME", "TRUCK"], result["context"]["alternatives"])
        self.assertIn("require user confirmation", result["context"]["reason"])

    def test_office_worker_explicitly_not_away_bypasses_context_modes(self) -> None:
        result = router.resolve({
            "employment_status": "working",
            "job_title": "systems administrator",
            "works_away_from_home": False,
        })
        self.assertEqual("bypassed", result["context"]["status"])
        self.assertEqual([], result["context"]["primary_modes"])

    def test_field_role_without_away_answer_requires_confirmation(self) -> None:
        result = router.resolve({
            "employment_status": "working",
            "job_title": "field service technician",
        })
        self.assertEqual("needs_confirmation", result["context"]["status"])
        self.assertEqual(["HOME", "FIELD"], result["context"]["primary_modes"])

    def test_custom_context_labels_outrank_role_recommendation(self) -> None:
        result = router.resolve({
            "employment_status": "working",
            "job_title": "truck driver",
            "works_away_from_home": True,
            "context_mode_names": ["house", "tractor"],
        })
        self.assertEqual("selected", result["context"]["status"])
        self.assertEqual(["HOUSE", "TRACTOR"], result["context"]["primary_modes"])

    def test_stock_services_are_provisioned_but_never_silently_enabled(self) -> None:
        result = router.resolve({"employment_status": "working"})
        for service in ("briefs", "order_lifecycle", "recipe_library"):
            self.assertTrue(result["stock_services"][service]["provisioned"])
            self.assertEqual("unresolved", result["stock_services"][service]["activation"])

        explicit = router.resolve({
            "employment_status": "working",
            "briefs_enabled": "yes",
            "order_lifecycle_enabled": "no",
            "recipe_library_enabled": False,
        })
        self.assertEqual("enabled", explicit["stock_services"]["briefs"]["activation"])
        self.assertEqual("disabled", explicit["stock_services"]["order_lifecycle"]["activation"])
        self.assertEqual("disabled", explicit["stock_services"]["recipe_library"]["activation"])

    def test_invalid_boolean_fails_closed(self) -> None:
        with self.assertRaisesRegex(ValueError, "invalid boolean"):
            router.resolve({
                "employment_status": "working",
                "works_away_from_home": "probably",
            })

    def test_invalid_custom_modes_fail_closed(self) -> None:
        with self.assertRaisesRegex(ValueError, "two-item list"):
            router.resolve({
                "employment_status": "working",
                "context_mode_names": ["HOME"],
            })

    def test_context_never_changes_canonical_timezone(self) -> None:
        result = router.resolve({
            "employment_status": "working",
            "job_title": "delivery driver",
            "works_away_from_home": True,
        })
        self.assertEqual(
            "context-never-overrides-canonical-iana-timezone",
            result["canonical_timezone_rule"],
        )


if __name__ == "__main__":
    unittest.main()
