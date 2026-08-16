# Google Sheets schema

Preserve these tab names, column orders, primary IDs, validation rules, and Eastern-time semantics.

## Ops Status Register

### Tasks

`Task ID | Tier | Classification | Subsystem | Task | Status | Visibility | Active From | Active Through | Recurrence / State Rule | Notes | Updated (ET)`

- ID: stable `TASK-###`.
- Tier: `Persistent`, `High`, `Medium`, or `Low`.
- A normal task requires Tier and Classification. A Persistent task requires Classification and no priority ranking.
- Status changes preserve the row; use `Done` or `Removed` rather than deletion.

### Control

`Record ID | Type | Item | State | Starts At (ET) | Expires At (ET) | Notes | Status | Updated (ET)`

- ID: stable `CTRL-###`.
- Temporary mode changes use Type `Mode Override` with an explicit, exclusive expiry.

### Routes

`Route ID | Endpoint A | Endpoint B | Route A → B | Route B → A | Avg A → B (hrs) | Avg B → A (hrs) | Operation Profile | Status | Notes | Created (ET) | Updated (ET)`

### Trips

`Trip ID | Route ID | Origin | Destination | Departure (ET) | ETA (ET) | ETA Source | Current Location | Location Time (ET) | Weather Watch | Watch Expires (ET) | Status | Route Override | Notes | Updated (ET)`

### Travel Settings

`Setting ID | Setting | Value | Notes | Status | Updated (ET)`

### Shipments

`Shipment ID | Vendor | Order Number | Item | Carrier | Tracking Number | Package Count | Order Date | Shipped Date | ETA (ET) | Status | Last Progress (ET) | Notes | Updated (ET)`

- ID: stable `SHIP-###` while active.
- Allowed Status: `Awaiting Shipment`, `Shipped`, or `Exception`.
- One row per fulfillment/tracking number; split packages may share an order number.
- This is an active queue only. Delete a row immediately when delivery is confirmed.
- Never add a `Delivered` status or a completed-shipment archive tab.

### Run Log

`Run ID | Scheduled Date (ET) | Slot | Started (ET) | Completed (ET) | Policy Version | Mode | Status | Input Health | External Evidence | Mutations | Action Count | Error / Notes`

- One row per deterministic Run ID; retries update in place.
- Status: `OK`, `Degraded`, or `Error`.
- Never store Gmail IDs, message bodies, secrets, or the full rendered brief.

## Mileage & Pay Tracker

### Mileage Log

`Entry ID | Week Ending (Thu) | Trip ID | Route ID | Departure (ET) | Arrival (ET) | Origin | Destination | Company-Paid Miles | Rate / Mile | Gross Pay Estimate | Miles Source | Status | Notes | Updated (ET)`

- ID: stable `MILE-###`.
- Status: `Planned`, `Estimated`, `Final`, or `Voided`.
- Freeze the numeric rate on each actual entry so later default-rate changes do not rewrite history.

### Settings

`Setting | Value`

At minimum, provide the current default rate per mile used for new entries.

