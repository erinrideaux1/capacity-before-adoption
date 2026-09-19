# 100-Calendar Stress Test

## Scope
The prototype was stress-tested against 100 synthetic four-week executive calendars across 12 scenario types:
dense, fragmented, double-booked, team-heavy, customer-heavy, tentative-heavy, protected-strategy,
AI-labeled, mixed-complexity, sparse, back-to-back, and balanced.

The calendars included overlapping events, tentative/declined/cancelled events, leader-attended team
meetings, team-only context, customer commitments, protected strategy blocks, AI-labeled learning time,
fragmented openings, and completely event-free weekdays.

## Results
- 100/100 calendars analyzed successfully after remediation.
- 100/100 deterministic fallback briefs passed the interpretation validator.
- 4/4 deliberately prohibited HR conclusions were rejected by the validator.
- 33/33 automated unit/regression tests passed.
- No negative time calculations were produced.
- For all 100 calendars, scheduled hours + nominally open hours reconciled to the stated 47.5-hour workweek.
- All deliberately double-booked calendars produced detected overlap.
- All AI-labeled scenarios produced AI-block signals without treating those blocks as proof of adoption.

## Issue found and fixed
The first stress-test pass revealed that a weekday with zero calendar events was omitted from the
working-hours calculation. That could understate the workweek and distort capacity signals on sparse calendars.

The analyzer was changed to evaluate the complete Monday-Friday workweek even when one or more weekdays
contain no calendar events. A regression test was added, and all 100 calendars were rerun successfully.

## Important limitation
This was not a 100-response live-LLM evaluation because no live API key is configured in this environment.
The LLM prompt/response validator and deterministic interpretation path were red-teamed offline.
A live-model evaluation remains required before claiming that a specific model passed 100 calendar interpretations.

## Design conclusion
The stress test supports the prototype's deterministic calendar-analysis layer and its HR guardrails across
substantially varied synthetic operating patterns. The tool still treats calendar data as evidence for discovery,
not proof of capacity, meeting value, AI adoption, leader effectiveness, or team capacity.
