# Meal Planning

## Purpose

Help a user turn existing recipes/preferences and current constraints into practical meal plans and active grocery intent without replacing purchase history or inventing dietary requirements.

## Discovery

First boot always makes meal planning discoverable and asks `Do you want help with meal planning?` If selected, inspect accessible existing recipe/meal-plan evidence before rebuilding it. Sources may include current conversation, uploaded/File Library material, connected Drive/docs/notes, and other explicitly connected sources. Never claim global access to inaccessible old chats.

## State contract

The module uses the deployment's selected canonical structured state authority, defaulting to Google Sheets.

- `Recipes` stores canonical recipe identity, title/tags/provenance, and a Drive/document reference when the body is stored externally.
- `Meal Plans` stores accepted/proposed plan state.
- `Pantry & Freezer` stores user-supported inventory facts when enabled.
- `Shopping & Procurement` stores active grocery/shopping intent.
- Long recipe bodies, scans, images, PDFs, or other bulky originals may live in Drive/evidence storage with stable references.
- Shopping intent is not purchase history. Purchase evidence later reconciles fulfillment through the purchase/shopping workflow.
- Do not fabricate inventory, allergies, medical diets, nutrition targets, or completed meals.
- Every state mutation receives canonical authority readback before success is reported.

## Existing meal-planning import

When accessible prior chats/files/provider sources already contain recipes or meal planning:
1. read the reachable material;
2. dedupe/provenance-map it;
3. show material ambiguities rather than silently choosing;
4. normalize approved structured information into the canonical state authority;
5. retain long-form evidence in Drive when useful;
6. read back the imported state.

Old chats need not remain available after durable information is ingested.

## Shared meal planning

Meal planning can use personal state or an explicitly shared authority. A user may deliberately share the whole relevant workbook/folder or use a scoped shared meal-planning workbook/folder. Never infer household sharing.

## Minimal dependencies

Basic meal planning needs the selected structured state authority. Drive/files, shopping, finance, grocery, nutrition, or other integrations are optional adapters. Failure of one adapter must not disable basic meal planning.

## Portability

Portable source contains behavior/config/schema/migrations/tests only. A user's recipes, food preferences, meal history, pantry contents, shopping rows, and Drive evidence are deployment state and never upstream contribution material.