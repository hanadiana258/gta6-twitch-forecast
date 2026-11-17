# SPEC — GTA6 Twitch CCU hourly forecaster

Entry: `main.py` (Python 3.13, stdlib ONLY — no network, no third-party imports).
Deterministic: no wall-clock time, no randomness, sorted iteration.

## Input
- Env `MAKEFUN_INPUT_DIR` (else `/input`). Read every `*.in` file there in sorted name order.
- Each is JSON, schema `makefun/twitch-ccu-case/v1`. Key fields:
  - `known`: list with one row `{"hour":1,"from","until","viewers","channels","reads"}` — hour-1 print.
  - `forecast`: rows `{"hour","from","until"}` for hours 2..24.
  - `comparables`: list of `{name, day_start, unlock, hourly:[{from,viewers,channels,reads}]}` — past launch days ±14/3 days, hourly mean viewers.
- Output: env `MAKEFUN_OUTPUT_DIR` (else `/output`), file `<id>.out`, JSON object with exactly one key `hours`: 23 rows `{"hour": h, "q": [q05,q25,q50,q75,q95]}` for hours 2..24, each quantile a positive finite number ≤ 1e9, nondecreasing within the row.

## Algorithm (implemented in main.py)
1. `v1 = known[0]["viewers"]` if present and > 0, else fallback: median of positive `history_hourly` viewers; if still nothing, 1000.
2. For each comparable, find its release-day hours: points whose `from` falls on UTC `day_start`. Build log-ratio profile: for target hour h (2..24), `r(h) = ln(v_c(h) / v_c(1))` when both counts exist and v_c(1) > 0.
3. For each hour h collect r(h) across comparables; median `m(h)` = median of that list.
4. Forecast center: `med(h) = v1 * exp(m(h))`.
5. Spread: half-width `s(h) = max(SIGMA_FLOOR, SPREAD_K * (q85(h) - q15(h)) / 2)` where q85/q15 are the 85th/15th percentiles of r(h) and SIGMA_FLOOR, SPREAD_K are module-level float constants.
6. Quantile row: `q(tau) = med(h) * exp(z(tau) * s(h))` with z = [-1.6449, -0.6745, 0.0, 0.6745, 1.6449]; clamp each to [1, 1e9], then sort the row.
7. If a comparable's hourly series is missing a point, just skip that pair; empty lists fall back to 0.0 ratios.

## Tuning
Constants SIGMA_FLOOR and SPREAD_K must be tuned by a local script (scripts/tune.py or scratch/) that leaves-one-comparable-out over the case's own comparables: for every comparable with a full release day, pretend its hour-1 value is `known`, forecast hours 2..24 from the OTHER comparables, and score mean pinball loss `2*max(tau*d,(tau-1)*d)` with `d = ln(y)-ln(q)` (y from the held-out comparable's real hourly counts, y clamped to >=1). Pick the (SIGMA_FLOOR, SPREAD_K) pair minimizing the mean loss; bake the winner into main.py. Also try blending in a median-of-hours smoothing across neighbors (3-hour window on m(h)) and keep it only if it improves the loss.

## Hard requirements
- Runs under: `python3 -P -s /bot/main.py`, 72s wall, no network, read-only /bot, empty /output.
- Two runs on the same input produce byte-identical output.
- Any input missing/malformed: still emit a valid `<id>.out` (fallback forecast with all rows `q = [v1]*5`).
