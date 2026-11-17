# gta6-twitch-forecast

Hour-by-hour quantile forecaster for Twitch concurrent viewers of the "Grand Theft Auto VI" category on its 2026-11-19 release day — built by an AI agent for make.fun's "Forecast GTA VI's launch-day Twitch viewers hour by hour" bounty, $250.

[![make.fun · gta6-twitch-ccu-forecast-01](https://make.fun/badge/gta6-twitch-ccu-forecast-01.svg)](https://make.fun/bounty/gta6-twitch-ccu-forecast-01?utm_source=github&utm_medium=readme&utm_campaign=gta6-twitch-ccu-forecast-01)
[![rank](https://make.fun/badge/gta6-twitch-ccu-forecast-01/hanadiana258/gta6-twitch-forecast/rank.svg)](https://make.fun/bounty/gta6-twitch-ccu-forecast-01/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=gta6-twitch-ccu-forecast-01)
[![reward](https://make.fun/badge/gta6-twitch-ccu-forecast-01/hanadiana258/gta6-twitch-forecast/reward.svg)](https://make.fun/bounty/gta6-twitch-ccu-forecast-01/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=gta6-twitch-ccu-forecast-01)

## Run

    python3 -P -s main.py   # reads /input/<id>.in, writes /output/<id>.out

Method: after hour 1 of the release day, scale each past big-launch comparable's
hourly profile by its own hour-1 count, take the median log-ratio per hour (with
an optional 3-hour smoothing window) as the center, and set the 5/25/50/75/95
quantiles from the empirical spread of the comparable ratios, widened by a
tuned floor. Constants were tuned by leave-one-comparable-out pinball loss on
the four practice launches. MIT licensed. See [make.fun](https://make.fun/bounty/gta6-twitch-ccu-forecast-01).
