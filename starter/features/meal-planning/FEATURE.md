# Meal Planning

## Purpose

Help a user turn existing recipes/preferences and current constraints into practical meal plans and active grocery intent without replacing purchase history or inventing dietary requirements.

## Discovery

First boot always makes meal planning discoverable. If selected, inspect accessible existing recipe/meal-plan evidence before rebuilding it. Sources may include current conversation, uploaded/File Library material, connected Drive/docs/notes, and other explicitly connected sources. Never claim global access to inaccessible old chats.

Capture only user-selected useful configuration: household/serving pattern, cooking frequency, likes/dislikes, explicit dietary preferences/constraints, time/effort, equipment, repeat-versus-novelty preference, batch/leftover/freezer strategy, grocery cadence, home/away/travel variants, and optional user-requested cost/nutrition goals.

## Runtime contract

- Canonical recipe entries preserve provenance and dedupe equivalent recipes.
- Meal plans reference canonical recipes or clearly marked new proposals.
- Plans are proposals until accepted according to the user's policy.
- Grocery output creates/updates active shopping intent when enabled.
- Shopping intent is not purchase history. Purchase evidence later reconciles fulfillment through the purchase/shopping workflow.
- Leftover/pantry/freezer facts are mutable runtime state and remain in the selected canonical authority.
- Do not fabricate inventory, allergies, medical diets, nutrition targets or completed meals.

## Minimal dependencies

The module can run manually with no external connector beyond the selected canonical state authority. Drive/files, shopping, finance, grocery or other integrations are optional adapters. Failure of one adapter must not disable basic meal planning.

## Portability

Portable source contains behavior/config schema/tests only. A user's recipes, food preferences, meal history, pantry contents and shopping data are deployment state and are not upstream contribution material.