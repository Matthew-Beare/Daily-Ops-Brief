# Meal Planning

## Purpose

Help a user turn existing recipes/preferences and current constraints into practical meal plans and active grocery intent without replacing purchase history or inventing dietary requirements.

## Discovery

First boot always makes meal planning discoverable and asks `Do you want help with meal planning?` If selected, inspect accessible existing recipe/meal-plan evidence before rebuilding it. Sources may include current conversation, uploaded/File Library material, connected Drive/docs/notes, and other explicitly connected sources. Never claim global access to inaccessible old chats.

Capture only user-selected useful configuration: household/serving pattern, cooking frequency, likes/dislikes, explicit dietary preferences/constraints, time/effort, equipment, repeat-versus-novelty preference, batch/leftover/freezer strategy, grocery cadence, home/away/travel variants, and optional user-requested cost/nutrition goals.

## Runtime contract

Private deployment Git is canonical state.

- Canonical recipe entries preserve provenance and dedupe equivalent recipes.
- Accepted recipes, meal plans, pantry/freezer facts, meal history, and shopping intent are written as Git state events/snapshots under `GIT_STATE_MODEL.md`.
- Meal plans reference canonical recipes or clearly marked new proposals.
- Plans are proposals until accepted according to the user's policy.
- Grocery output creates/updates active shopping intent when enabled.
- Shopping intent is not purchase history. Purchase evidence later reconciles fulfillment through the purchase/shopping workflow.
- Do not fabricate inventory, allergies, medical diets, nutrition targets, or completed meals.
- Every coherent accepted state change validates, commits, pushes fast-forward only, and reads the remote Git state back before reporting success.

## Existing meal-planning import

When accessible prior chats/files/provider sources already contain recipes or meal planning:
1. read the reachable material;
2. dedupe/provenance-map it;
3. show material ambiguities rather than silently choosing;
4. normalize approved useful information into Git recipe/meal-plan state;
5. commit/read back the import checkpoint.

Old chats need not remain available after durable state has been imported.

## Minimal dependencies

The module can run manually with private Git only. Drive/files, shopping, finance, grocery, nutrition, or other integrations are optional evidence/action adapters. Failure of one adapter must not disable basic meal planning.

## Portability

Portable source contains behavior/config schema/tests only. A user's recipes, food preferences, meal history, pantry contents, and shopping data live in the private deployment `state/` tree and are never upstream contribution material.