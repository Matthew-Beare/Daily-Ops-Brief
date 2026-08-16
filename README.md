# Daily Ops Brief

Rebuildable policy and deterministic tooling for a twice-daily personal operations brief.

The live Google Sheets remain the operational database. Gmail supplies order, carrier, and important-message evidence. This repository versions the policy, schemas, fixtures, tests, and rebuild procedure—not raw email or live personal records.

## Guarantees

- Exactly two scheduled brief dispatchers: 2:45 AM and 2:45 PM Eastern.
- Gmail and shipment state are reconciled before a brief is rendered.
- `Shipments` contains active fulfillment only; delivered rows are deleted immediately.
- Important email remains in Inbox under `Ops/Archive Approval` until explicit approval.
- Silence never authorizes archiving.
- Clear Daily Brief/Ops-list commands from any supported conversation are written to the canonical Sheet, not left in chat memory.
- Promotions and sale monitoring are out of scope.

## Repository layout

```text
config/       Sanitized configuration contract
docs/         Architecture, operating procedure, and Sheet schemas
fixtures/     Synthetic test/rebuild inputs
schemas/      Machine-readable Sheet contracts and migrations
skill/        Complete skill template, references, assets, and policy engines
tools/        Rebuild tooling
tests/        Unit tests
.github/      Continuous integration
```

## Validate

Python 3.11 or newer is sufficient; the policy has no third-party runtime dependencies.

```bash
python3 -m unittest discover -s tests -p 'test_*.py' -v
```

## Rebuild

1. Create the two Google Sheets and tabs documented in [`docs/SHEET_SCHEMA.md`](docs/SHEET_SCHEMA.md) and codified in `schemas/google-sheets.json`.
2. Copy `config/ops.example.json` to `config/ops.local.json` and set the two spreadsheet IDs. The local file is ignored by Git.
3. Create the Gmail labels listed in [`docs/OPERATIONS.md`](docs/OPERATIONS.md).
4. Render an installable skill package:

   ```bash
   python3 tools/render_skill.py \
     --config config/ops.local.json \
     --output build/ops-brief-policy
   ```

5. Install the generated `build/ops-brief-policy` package.
6. Create only the two dispatcher schedules shown in [`docs/OPERATIONS.md`](docs/OPERATIONS.md).
7. Run the full test suite before activating either schedule.

## Data boundary

Do not commit live Sheet exports, email bodies, Gmail IDs, addresses, account numbers, credentials, calendar contents, rendered personal briefs, or local configuration. Private Git is still durable history, not a secrets or personal-records vault.
