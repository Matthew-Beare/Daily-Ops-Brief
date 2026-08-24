# Meal Planning Acceptance Contract

A compliant deployment must prove:

1. first boot explicitly asks `Do you want help with meal planning?`;
2. existing accessible recipe/meal-plan evidence is offered for import/reconciliation before manual recreation;
3. inaccessible old chats are never claimed as read;
4. structured recipe indexes, accepted meal plans, pantry/freezer facts, meal history and active shopping intent live in the selected canonical structured state authority;
5. long recipe bodies/images/documents may live in Drive/evidence storage with stable canonical references;
6. state mutations receive canonical authority readback before success;
7. meal plan, active shopping intent and purchase history remain separate identities;
8. private meal/pantry/history state stays out of portable upstream source;
9. explicit user preferences drive dietary behavior and the system does not invent medical restrictions;
10. missing optional connectors degrade only their adapter path;
11. state sharing is explicit and distinct from public feature sharing.