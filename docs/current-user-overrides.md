# Current Deployment Overrides

This file documents durable deployment-specific behavior only. Mutable people, assets, routes, trips, receipts and payment state remain in canonical Sheets and are not copied here.

## Speech-recognition alias normalization

When current-user dictation clearly refers to the user's wife and speech recognition produces variants such as `Pat`, `Pat Pat`, `Big Tet`, `Big Bed` or `Pigpet`, normalize the conversational referent to **Pig Pet** before reading/writing canonical state. The authoritative person/alias row remains in the Purchase & Receipt Archive `People & Assets` table.

Do not apply this alias rule to another user's starter deployment.

## Terminal paid-mile model

For this deployment, company-paid terminal mileage is symmetric by terminal pair: once A↔B mileage is verified, use the same value both directions unless the user explicitly supplies an exception. Employer/shared run-sheet evidence is reconciled into the existing Routes/Trips/Mileage authorities; it does not create a parallel database.
