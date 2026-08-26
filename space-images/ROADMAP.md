# Roadmap to the Stars

We are going. Not someday in a storybook — on a path we can name, measure, and climb.

This repository is **inspiration grounded in tooling**: real images from public missions on your disk, and a map of how a civilization leaves Earth, settles the solar system, and eventually reaches the stars. The mind expands because the data is real — distances, timelines, and hard problems included.

With a laptop and an Internet connection you already have what this repo needs: open NASA APIs, public image archives, and scripts that pull them home.

## Why keep going

This is the raw-material source for a whole cluster of astronomy projects
in this account that otherwise generate or render synthetic sky data —
real mission imagery grounds `star-art` and other renders in
something that actually happened, not just a simulation.

## What it opens up

As the album of provenance-tagged images (mission, date, license) grows,
it becomes a dataset other repos can pull from directly instead of hitting
NASA's APIs themselves — a shared local archive of "real space, already
downloaded" that `star-art` could consume.

## Connects to

- **star-art**, **constellations** — same domain
  (the night sky), different register: this repo is documentary, those
  are rendered/generated.
- **living-room-solar-system** — same "bring real astronomy into daily
  life" instinct, different surface (living room wall vs. downloaded album).

---

## What you can do today (laptop + network)

No special lab. Free or rate-limited public APIs. Run it, keep the files, read the source captions.

| Capability | How |
| --- | --- |
| **One picture, today** | `make inspire` → APOD into `album/daily/` with sidecar story (repeat to stack more that day) |
| **Bulk sky + missions** | `make nasa` / `make planets` → APOD archive samples and library hits into `images/` and `images/<planet>/` |
| **Schedule wonder** | cron (or any scheduler) calling `make inspire` |
| **Trace provenance** | every file has paired `.json` / `.md` (title, date, mission, license, source URL, destination tag) |
| **Go further by hand** | open archives linked in the README — Hubble, JPL Photojournal, ESA, ESO, Chandra, Mars raw images |

Downloaded content stays on your machine (gitignored). The repo is the pipeline and the map, not a content dump.

---

## The ladder (humanity’s path)

We do not jump to Alpha Centauri in one leap. We climb.

```
Earth ──► LEO ──► Moon ──► Mars ──► Outer planets ──► Stars
 home     practice   fuel &   next     robots first,    generation ships,
          ground     training  home     then crews       new physics, time
```

### 1. Earth — protect the launchpad

The only world we know can host a civilization *today*. Climate, industry, and peace are load-bearing. A species that cannot steward one planet will not steward a hundred.

**Near-term markers:** sustainable energy, resilient infrastructure, open science, cheaper launch.

### 2. Low Earth orbit — the practice ground

ISS, commercial stations, frequent crew and cargo. Live off the ground without leaving the neighborhood.

**Near-term markers:** cheaper access to orbit, private stations, microgravity manufacturing and research, routine flight as infrastructure.

### 3. Moon — the first off-world foothold

Close enough to abort, far enough to train. Ice, regolith, power, and navigation for deep space.

**Near-term markers:** sustained presence (not only flags-and-footprints), lunar logistics, far-side science, propellant and construction demos.

### 4. Mars — the second home candidate

Months of travel, thin air, cold dust — and the clearest place after Earth for a lasting human outpost.

**Near-term markers:** reliable cargo chains, ISRU (fuel and oxygen on site), habitats, sample return, then crew with a plan to stay usefully.

### 5. Outer solar system — robots lead, humans follow

Jupiter’s moons, Saturn’s rings, ice giants, Kuiper belt. Most of the mass and mystery of *our* system still waits for better machines — then people.

**Near-term markers:** ice-moon ocean probes, nuclear/solar power for deep space, high-bandwidth relays, sample returns from new worlds.

### 6. The stars — the long game

Proxima, the Centauri system, everything beyond. Light-years mean **new propulsion**, **very long voyages**, or both. That work starts in labs and papers *now* — not after Mars is “done.”

**Near-term markers:** breakthrough propulsion research, interstellar precursor probes, closed-loop life support on decade timescales, a culture that treats multi-generation goals as normal.

---

## What this repo does today

- **Daily pull** — `make inspire` fetches APOD into `album/daily/` with caption
- **Bulk pulls** — NASA Image Library + APOD samples into `images/`; per-planet sets into `images/<planet>/`
- **Sidecars** — metadata and source caption next to every image
- **Make targets** — `inspire`, `nasa`, `planets`, `clean`, `lock`
- **Source map** — links to NASA, ESA, Hubble, JPL, ESO, Chandra, Mars raw, and space news (see `README.md`)

The seed: **put the cosmos on disk so you can look hard and build from it.**

---

## Project roadmap (this repository)

Ship tools that make looking outward automatic and honest. Ambition grows with the pipeline, not with packaging for every audience.

### Phase 0 — First run *(done)*

- [x] README: vision, then “run this, get a picture”
- [x] Safe defaults (no secrets in tree; free NASA API key documented)
- [x] One wow path: today's (or recent) APOD + caption

### Phase 1 — Daily pull *(done)*

- [x] On-demand / scheduled inspire job: fetch → caption → album
- [x] Lightweight orchestration (cron first; heavier tooling only if earned)

### Phase 2 — Stories with the files *(done)*

- [x] Sidecar metadata: title, date, mission, body, license, source URL, destination
- [x] Full source captions where APIs provide them

### Phase 3 — Create with the cosmos

- [ ] Export (consistent naming, credits file)
- [ ] Collage / poster recipes (scripted or documented manual flow)
- [ ] Contribution path for short “why this matters” notes
- [ ] Optional static showcase

### Phase 4 — The living ladder

- [ ] Tag content by ladder step (LEO / Moon / Mars / outer / stars)
- [ ] Timeline view: “where we are” vs “what’s next” with real mission milestones
- [ ] Link images to open mission pages and primary data archives

### Phase 5 — Wider open data

- [ ] Partner sources (ESA, JWST, other open datasets) behind the same interface
- [ ] Better search and filter over local libraries
- [ ] Annual “state of the climb” note: what humanity shipped toward the stars

---

## Principles

1. **Wonder with evidence.** Beauty and stakes first; numbers and limits close behind.
2. **Truth over hype.** Real distances, real timelines, real hard problems. Inspiration survives honesty.
3. **Credit the explorers.** Missions, agencies, and licenses stay visible.
4. **Build in the open.** Reproducible scripts beat one-off downloads on one machine.
5. **Long horizon, short loops.** Think centuries; ship something you can run this week.
6. **Depth over packaging.** Expand the mind; do not dilute the toolkit into a lesson kit.

---

## How you can help this week

1. Run `make inspire` or `make planets` and keep one image that stopped you cold.
2. Follow a source URL into a mission page or archive — one hop deeper than the pixels.
3. Open an issue: broken link, missing world, better pipeline idea.
4. Improve docs so the next person needs fewer guesses.
5. Share public imagery *with* credit and story, not only the file.

---

## North star

When someone asks *“Will we ever go?”* the answer should not be a shrug.

It should be: **here is the ladder, here is the next rung, and here is data and tooling you can run today.**

This repo exists so that answer stays concrete — images on disk, scripts that fetch them, and a roadmap you can read and extend.

*The sky is not a ceiling. It is a direction.*
