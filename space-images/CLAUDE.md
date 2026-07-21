# space-images

Project rules for agents and humans working in this repo. Global preferences still apply; this file wins on conflicts.

## Purpose

Open toolkit + inspiration for space imagery and the path from Earth to the stars. Audience is broad: children through adults. Docs lead with wonder and plain language; put deep technical detail after the first successful run.

## Altitude

Default write-ups and explanations to the conceptual level: name scripts, dirs, and data hops. Skip variable-level walkthroughs unless asked. ROADMAP stays current-state vision and plan — not change-log narrative.

## Docs

- **README.md** — what the repo does, how to run, layout, source links.
- **ROADMAP.md** — human ladder + phased project work; keep checkboxes honest.
- **CLAUDE.md** — this file; rules only, no examples that restate the rules.
- Prefer short tables and commands over multi-paragraph intros.
- Credit NASA/ESA/missions when adding share or publish paths.

## Code

- Python 3.11+, managed with **uv**; run via `uv run` or Makefile targets.
- Entry points: `scripts/nasa.py` → `images/`; `scripts/planets.py` → `planets/`.
- Prefer env (or local config gitignored) for API keys — never commit secrets.
- Be polite to public APIs: retries, short sleeps, no aggressive parallel hammering.
- Keep download + sidecar `.md` metadata paired; filenames safe for common filesystems.
- No drive-by refactors. No new deps without a clear need.
- Fail hard on real errors; do not swallow network failures silently.
- Comments only when the *why* is non-obvious.

## Make / tooling

- `make install` / `make nasa` / `make planets` / `make clean` / `make lock` are the user-facing commands; keep `make help` accurate when targets change.
- Ruff + mypy config live in `pyproject.toml`; match existing lint/format style.
- Downloaded content under `images/` and `planets/` stays gitignored.

## Commits

Conventional Commits (`feat:`, `fix:`, `chore:`, `docs:`, `refactor:`, `test:`). New commit only; do not amend pushed history unless asked. Do not commit unless the user asks.

## Plan before build

For anything beyond a trivial fix, state the plan and wait for explicit go-ahead before writing code or large doc rewrites.
