# Meal Planning Acceptance Contract

A compliant deployment must prove:

1. first boot explicitly asks `Do you want help with meal planning?`;
2. existing accessible recipe/meal-plan evidence is offered for import/reconciliation before manual recreation;
3. inaccessible old chats are never claimed as read;
4. accepted recipes, meal plans, pantry/freezer facts, meal history and active shopping intent are canonical private Git state;
5. each coherent accepted state change validates, commits, pushes fast-forward only and reads remote Git state back;
6. meal plan, active shopping intent and purchase history remain separate identities;
7. private meal/pantry/history state stays out of portable upstream source;
8. explicit user preferences drive dietary behavior and the system does not invent medical restrictions;
9. missing optional connectors degrade only their adapter path;
10. a personal customization can remain private or pass the opt-in portability/share-back gate without exporting `state/`.