# Baseline vs better version: what changed

Compare with: `diff -ru ../frontend ../frontend_baseline`. Every changed line carries a `[BASELINE]` marker.

| # | File | Marker says | Week 1 problem it recreates |
|---|---|---|---|
| 1 | `app.js` top_bar | one neutral "Alarms: N" counter | noise is invisible, no Critical/Watch split |
| 2 | `app.js` rank / drift | removed | no risk ordering, no trend detection |
| 3 | `app.js` spark | never called | no trends on tiles or cards |
| 4 | `app.js` play_tone | one tone | every alarm sounds the same |
| 5 | `app.js` open_action | no mute option, no trigger/risk in escalation text | no noise control, factor hidden |
| 6 | `matrix.html` cell | same two readings on every tile, grey ALARM badge | trigger factor not visible, no colour coding |
| 7 | `matrix.html` draw | flat bed-ID grid, tiles never move | hunting for the alarm among 100 tiles |
| 8 | `matrix.html` drawer | alarm list in bed-ID order, no rank/risk/chips/timer/sort | triage not sorted |
| 9 | `detail.html` | no risk box, no reason bullets, identical cards, no sparklines | opening tabs to learn why |
| 10 | `trends.html` | table of last 3 readings only | no history, doctors write vitals by hand |
| 11 | `settings.html` | Log + Thresholds, plain sliders, no preview/warning/Sound tab | alarm fatigue |
| 12 | `style.css` | flat grid + neutral cell styles appended at the end | no colour coding |

Unchanged on purpose: `data.js`, top-bar layout, hospital filter, Escalate/Call modals and their feedback states, Simulate/Reset.
