# Ops Brief Regression Cases

These are contract tests for the policy/engine. A future executable test harness should encode the same cases.

## REG-001 — Saturday PM active trip is ROAD

**Now:** 2026-08-22 14:45 America/New_York  
**Control:** HOME vacation override expired 2026-08-21 12:00 ET  
**Trips:** TRIP-001 status `Active`, Morristown TN → Rialto CA  
**Expected:** `ROAD`

The expired HOME override must not leak into Saturday. Active trip evidence independently forces ROAD.

## REG-002 — Saturday PM mileage shape failure is not fatal

**Now:** 2026-08-22 14:45 America/New_York  
**Mode:** ROAD by REG-001  
**Injected failure:** `mileage_values is not a readable sheet range`  
**Expected:** brief still renders ROAD content. The run must not become `Error` solely because mileage data failed on Saturday.

Acceptable status is `OK` when mileage was not needed/consulted, or `Degraded` when the optional read was attempted and failed.

## REG-003 — Thursday mileage failure is section-scoped

**Now:** Thursday 14:45 ET  
**Injected failure:** Mileage & Pay Tracker unavailable  
**Expected:** include `Action Required — mileage/pay Sheet unavailable`; continue other valid sections. Do not substitute map miles or memory.

## REG-004 — Friday PM is ROAD before physical departure

**Now:** Friday 14:45 ET  
**Trips:** none active  
**Overrides:** none  
**Expected:** `ROAD` because the weekly ROAD window begins Friday 12:00 ET. This makes the pre-departure PM brief road-oriented even when normal departure is 16:30 ET.

## REG-005 — Expired override is ignored

**Now:** any timestamp after an override's `Expires At (ET)`  
**Expected:** ignore that override completely and continue to active-trip/weekly resolution.

## REG-006 — Active HOME override outranks active trip

**Now:** inside an explicit unexpired HOME override window  
**Trips:** an old/stale trip still says `Active`  
**Expected:** `HOME`. Explicit live override wins until expiry; the stale trip should then be reconciled separately.

## REG-007 — Active trip survives weekly HOME boundary

**Now:** Wednesday 16:31 ET  
**Trips:** current trip still genuinely `Active` due delay  
**Overrides:** none  
**Expected:** `ROAD`. A real active trip is stronger evidence than the weekly default HOME transition.

## REG-008 — Saturday AM appointment look-ahead

**Now:** Saturday 02:45 ET  
**Expected:** include appointments in the next 7 days, plus all otherwise applicable day-before/morning-of reminders. Never expose confirmation status.
