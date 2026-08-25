# Roadmap

## Why keep going

This is the one repo in the astronomy cluster that actually generalized — location lives in `config.json`, not in the code. That sounds small, but it's the difference between a script and infrastructure. Everything else nearby (`constellations`, `stargazing-on-the-run`, `[private]`, `[private]`) almost certainly reimplements its own slice of solar/ephemeris math for its own narrow question. This is the one place that math got done properly once.

## What it opens up

The real next question isn't "what's the seventh chart" — it's "what else in this portfolio should stop computing its own sun position and call this instead." Once that happens, this stops being one repo among many astronomy scripts and becomes the shared foundation underneath all of them, which changes what's easy to build next across the whole cluster, not just here.

## Capability this builds

Turning a one-off analysis script into something other projects can depend on — a different, more valuable skill than writing another standalone script, and one this portfolio doesn't practice much.

## Connects to

- **solar-lunar-times** — computes the same rise/set/noon times in JavaScript instead of Python. Almost certainly duplicated effort; one of these two should defer to the other.
- **constellations**, **stargazing-on-the-run**, **[private]**, **[private]** — the cluster this could become the shared core for, instead of each carrying its own solar math.
- **[private]**, [private] — race-morning light planning is exactly the `config.json`-per-location, "when does the sun come up here" question this repo already answers well.
