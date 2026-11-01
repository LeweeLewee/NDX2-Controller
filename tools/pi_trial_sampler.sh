#!/bin/sh
# Run in the existing authenticated HA Terminal app, not the bridge container.
# Bounded 24-hour read-only host observation; no player commands or credentials.
set -eu
umask 077
trial_dir=${1:?private trial output directory required}
mkdir "$trial_dir"
started=$(date +%s)
finish=$((started + 86400))
printf '%s\n' "$started" > "$trial_dir/started_at"
printf '%s\n' "$finish" > "$trial_dir/expected_finish"
while :; do
    now=$(date +%s)
    {
        date -u +%Y-%m-%dT%H:%M:%SZ
        ha apps stats local_still_water_bridge --raw-json || true
        ha core stats --raw-json || true
        cat /app_configs/local_still_water_bridge/private/status.json || true
        printf '\n'
    } >> "$trial_dir/samples.log" 2>&1
    if [ "$now" -ge "$finish" ]; then break; fi
    sleep 300
done
date -u +%Y-%m-%dT%H:%M:%SZ > "$trial_dir/completed_at"
