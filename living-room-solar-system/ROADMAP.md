# Roadmap: Living Room Solar System

## How this connects to the rest of the portfolio

This is the only sky-facing project aimed at a room rather than a camera or a race — everything else in the astronomy cluster produces an image or a data point; this one produces a daily household habit. That distinction is worth keeping as the north star while the phases below get built.

**Connects to:**
- **constellations** / **[private]** — both already compute nightly visibility from a fixed observer location; the visibility engine described in "Architecture sketch" below could share code with those instead of reimplementing Skyfield queries independently.
- **stargazing-on-the-run** / **[private]** — render the sky onto photos/Stellarium views taken *outdoors*; this project is the same astronomical computation aimed *indoors*. A shared "what's up right now" core library would serve all three.
- **sun-year** / **solar-lunar-times** — already compute solar/lunar positions and times for a location; directly relevant to Phase 1's Moon phase and Phase 2's "why does it look like that" seasonal work.
- **space-images** / **[private]** — Phase 6's knowledge cards ("surface / sample truth") need exactly the kind of curated NASA/ESA imagery those repos already work with.
- **[private]** — extracts ideas from browsing; a natural place to source the curated science facts Phase 6 wants, rather than building a second extraction pipeline.

---

Make distant worlds **relatable and visible every day** — not as abstract facts, but as positions, motions, and stories you can point to from the couch. Curiosity first; walking on those worlds is the long arc this kind of familiarity feeds.

This document builds on what the repo already does and stays within what is **technically possible** with open ephemerides, public mission data, and household hardware.

---

## North star

**The sky should feel like part of the house.**

Someone who never looks up should still know, tonight, that Jupiter is “that height on the south wall,” that the Moon is rising later, that a spacecraft is overhead for three minutes. Familiarity is the product; wonder is the side effect.

---

## What we have today

A single CLI (`scripts/planets.py`) that:

1. Loads a fixed observer from `config.json`.
2. Uses Skyfield + `de421.bsp` for planet positions, Astral for sunset → sunrise.
3. Samples the night, summarizes visibility (avg altitude/azimuth, rise/set window).
4. Groups objects by azimuth and asks for wall distances.
5. Maps altitude → **wall projection height** (`tan(alt) × distance`).

That is the core primitive: **sky direction → place in the room**. Everything below either strengthens that mapping, widens what we map, or adds meaning to the mark on the wall.

---

## Design principles

| Principle | Meaning in practice |
| --- | --- |
| **Everyday over spectacle** | Prefer something you leave running or re-run nightly over a one-shot demo. |
| **True position first** | Geometry from real ephemerides; aesthetics never invent altitudes. |
| **Room-scale honesty** | Scale models that lie about distances get labeled as scale models; wall projection stays “where to look in the sky.” |
| **Household hardware** | Tape, stickers, phone, Raspberry Pi, cheap LEDs, optional projector — not a planetarium install. |
| **Questions over answers** | Surface “why is Venus only in the west?” and “how far is that?” more than encyclopedias. |
| **Offline-capable core** | Ephemeris-based visibility should work without network; enrichments can be online. |

---

## Phases

Phases are ordered by leverage on the existing stack. Later phases assume earlier ones unless noted.

### Phase 0 — Solidify the living-room primitive

**Goal:** Make tonight’s map trustworthy and re-runnable without friction.

| Track | Ideas | Why it matters |
| --- | --- | --- |
| **Time modes** | Tonight / now / arbitrary date; optional daytime (planets above horizon while Sun is up). | “What is up *right now*” is how people actually use it. |
| **Better geometry** | Instantaneous alt/az at a chosen time, not only night-average; optional path over the night (arc of marks). | Averages hide motion; arcs teach that the sky moves. |
| **Room profile** | Save wall distances (and optional ceiling height / blocked azimuths) in config so re-runs don’t re-prompt. | Everyday use fails if every run needs a tape measure. |
| **Obstruction model** | Simple horizon mask (buildings, trees) as altitude floor per azimuth sector. | False “visible” erodes trust in a city apartment. |
| **Output you can keep** | Print a one-page “tonight’s wall map”; optional JSON for other tools. | The mark on the wall should outlive the terminal session. |

**Done when:** Re-running for your room is non-interactive (except first setup), and “now” vs “tonight average” are both available.

---

### Phase 1 — More of the solar system, still on the walls

**Goal:** Same projection model; richer solar neighborhood.

| Object class | Technical basis | Living-room form |
| --- | --- | --- |
| **Moon** | Skyfield / existing ephemeris; phase fraction and illumination. | Wall height + phase symbol; “how full” as a daily habit. |
| **Sun** | Day path only; never confuse with night planets. | Optional day mode: “Sun is *that* high on the east wall at 09:00.” |
| **Major moons** | Galilean moons, Titan when bright enough / interesting enough — positions relative to parent, not always naked-eye. | Annotation next to Jupiter/Saturn mark: “Io / Europa tonight.” |
| **Bright asteroids / dwarf planets** | When above a magnitude threshold (e.g. Vesta, Ceres at opposition). | Rare guests on the wall — teaches that the map is not only the classic seven. |
| **Comets (selected)** | Public orbital elements when available; only if predicted magnitude warrants. | Temporary “visitor” labels with a date range. |

**Honesty layer (required with expansion):**

- Naked-eye vs binocular vs telescope vs “ephemeris only” badges.
- Apparent size (arcseconds) and approximate distance (AU / light-minutes) next to the wall height — so the mark means “where,” not “how big it looks.”

**Done when:** Moon + planets share one report; each mark carries visibility class and a one-line distance/size cue.

---

### Phase 2 — Motion, seasons, and “why does it look like that?”

**Goal:** Turn static marks into a sense of *changing sky*.

| Idea | Technical approach | Everyday hook |
| --- | --- | --- |
| **Night arcs** | Sample path; output a sequence of wall heights over hours. | Tape a dashed path: “Jupiter climbs then falls.” |
| **Week / month preview** | Same engine, multi-night table. | “Best night for Mars this week.” |
| **Opposition / elongation alerts** | Simple geometric conditions from ephemeris. | Push or print: “Saturn is opposite the Sun — all night.” |
| **Conjunctions** | Angular separation between pairs under a threshold. | “Venus and Moon share the same wall sector tonight.” |
| **Retrograde made visible** | Multi-night azimuth trend. | A small plot or week-of marks that reverse direction. |
| **Scale stories** | Light-time, travel time at Apollo / New Horizons / light speed (labeled as thought experiments). | The wall mark for Neptune includes “radio takes ~4 hours.” |

Avoid fake “to scale in the room” orbits unless they are a **separate, clearly labeled** mode (e.g. Sun at one wall, planets as beads on a string along the floor with stated scale). Mixing true sky direction with false distance scale confuses the core metaphor.

**Done when:** A user can answer “what changed since last week?” without opening a textbook.

---

### Phase 3 — Earth-orbit and human presence

**Goal:** Make *our* activity in space as ordinary as weather.

| Object | Data source (examples) | Living-room form |
| --- | --- | --- |
| **ISS / bright satellites** | Public TLEs + Skyfield or equivalent; magnitude filters. | “Pass in 12 minutes, SW → NE, max elev 60° → wall height H.” Timed, not averaged. |
| **Starlink / mega-constellations** | Optional, filtered (bright trains only); easy to opt out. | Rare “train” nights — teaches orbital density without becoming noise. |
| **JWST / deep-space craft** | Not usually naked-eye; show **where in the sky** the craft *is*, and **where it points** if public. | “JWST is in that direction (L2)” as a conceptual mark — labeled non-visual. |
| **Mission timeline overlay** | Static curated facts + optional APIs for status. | Beside Mars: “Perseverance is awake; sample tubes cached.” |

This phase is where “walk on those worlds” becomes concrete: **rovers and landers** as characters attached to planet marks, not as a separate app.

**Done when:** At least one Earth-orbit pass and one surface-mission fact can attach to the same nightly ritual as the planets.

---

### Phase 4 — Stars and deep sky (carefully)

**Goal:** Beyond the solar system without pretending the wall is a planetarium dome.

| Layer | What’s honest | What to avoid |
| --- | --- | --- |
| **Bright stars / constellations** | Top N stars above magnitude limit; constellation lines for the current season. | Catalog dump of thousands of stars on one wall. |
| **Milky Way band** | Approximate galactic equator crossing the sky → a soft “band” across room directions. | Photorealistic sky that fights room lighting. |
| **Deep-sky objects** | A few famous Messier/NGC objects when up: Andromeda, Orion Nebula, Pleiades — with instrument class. | Claiming naked-eye for objects that need dark skies and optics. |
| **Exoplanet hosts (selected)** | Direction to a few systems with known planets; light-year distance explicit. | Implying you can “see the planet.” |

**Scale shock, handled gently:** when an object is light-years away, wall height still means *direction only*; distance lives in the label. Optional “if the Sun is a grape on the table, Alpha Centauri is in the next city” side mode — again, separate from projection geometry.

**Done when:** Seasonal sky has 5–15 anchors people recognize by name, each with a direction in the room.

---

### Phase 5 — Embodiment: from terminal to room

**Goal:** Lower the cost of *seeing* the map every day.

Progression (pick what fits the household; none require all of them):

1. **Physical marks** — reusable stickers/magnets with planet symbols; heights from the script; optional QR to tonight’s fact card.
2. **Phone AR (optional)** — camera overlay of alt/az targets using the same engine; verify wall marks against the real sky at a window.
3. **Ambient display** — small always-on screen or e-ink: “now up” + next notable event.
4. **Directional LEDs** — addressable strip or sparse LEDs along walls/ceiling at calibrated azimuths; brightness = altitude or magnitude.
5. **Soft projection** — short-throw or pico projector drawing dots/labels on walls; keep contrast modest so it stays ambient, not a show.
6. **Multi-room / multi-observer** — only after room profiles are solid; e.g. balcony vs living room horizon masks.

**Constraint:** Embodiment layers consume the **same** visibility/projection API as the CLI. No second astronomy stack for the lights.

**Done when:** Someone can absorb “what’s up” in under ten seconds without running a full interactive session.

---

### Phase 6 — Narrative and knowledge, attached to place

**Goal:** Every mark can open a *small* door into real science — not a wiki dump.

| Content type | Source strategy | Example attachment |
| --- | --- | --- |
| **What we know** | Curated static cards (size, day length, atmosphere, last visit). | Venus mark → “runaway greenhouse; surface ~460°C.” |
| **How we know** | Mission lineage, telescope, year. | Neptune → “Voyager 2 flyby 1989.” |
| **Open questions** | Explicit unknowns. | Uranus → “why is the magnetic field so tilted?” |
| **Surface / sample truth** | Public imagery catalogs (NASA/ESA), with credit and date. | Mars → thumbnail of a recent rover site, not a fantasy landscape. |
| **Human future (cautious)** | Distances and energy as constraints; no timeline promises. | Moon → “3 days by Apollo-class transfer; dust and radiation are the hard parts.” |

Prefer **local content packs** versioned in-repo over scraping. Update cadence can be slow; truth ages better than hype.

**Done when:** Each default object has a short card (what / how we know / open question) reachable from the nightly map.

---

### Phase 7 — Beyond the neighborhood (research horizon)

Only after solar-system + bright-sky habits work. These are **direction and scale educators**, not new wall clutter by default.

| Theme | Feasible representation | Note |
| --- | --- | --- |
| **Galactic center** | Direction of Sagittarius A* when above horizon. | One mark, huge conceptual weight. |
| **CMB dipole / motion of the Local Group** | Advanced; optional “we are moving that way.” | Easy to overclaim; keep experimental. |
| **Gravitational-wave events / neutrino alerts** | Time-based “something happened in that sky patch.” | Ephemeral; good for wonder, bad as permanent stickers. |
| **Time-domain astronomy** | Supernovae, bright transients when public alerts exist. | Opt-in feed; magnitude and distance required. |

**Done when:** At least one extragalactic or all-sky concept has a first-class “direction in the room” story without breaking solar-system clarity.

---

## Architecture sketch (evolve, don’t rewrite)

Keep the current separation of concerns; grow interfaces, not a monolith rewrite.

```
config (place, room profile, preferences)
        │
        ▼
   ephemeris / TLE / time engine   →  visibility & paths (alt, az, mag, when)
        │
        ▼
   room projector                  →  wall height, sector, arcs
        │
        ├── CLI / print map
        ├── JSON or small local API
        ├── ambient / LED / e-ink consumers
        └── knowledge cards (static packs + optional live mission status)
```

**Near-term code shape (when implementing):** pure functions stay testable (as today); `main` remains a thin driver; room profile and multi-object catalogs become data, not hardcoded lists only.

---

## Explicit non-goals (for now)

- Photoreal real-time planetarium fidelity (Stellarium already exists).
- Accurate to-scale solar system *and* true sky directions in one unmarked display.
- Social network, accounts, or engagement metrics.
- Claiming naked-eye visibility for targets that need dark skies or optics.
- Automated control of telescopes (could be a later bridge; not the core product).

---

## Suggested sequencing (practical)

| Order | Focus | Outcome |
| --- | --- | --- |
| 1 | Phase 0 (now, room profile, arcs, export) | Habit-forming reliability |
| 2 | Phase 1 Moon + honesty badges | Emotional anchor + trust |
| 3 | Phase 2 multi-night + events | “The sky changed” |
| 4 | Phase 5 light embodiment (marks → e-ink/LEDs) | Ambient everyday |
| 5 | Phase 3 ISS + mission facts | Human presence |
| 6 | Phase 4 stars / few deep-sky | Seasonal identity |
| 7 | Phase 6 knowledge packs | Questions that stick |
| 8 | Phase 7 selective “beyond” | Cosmic context |

Phases 5 and 6 can start small in parallel with 1–2 (static stickers + a few markdown cards need little software).

---

## Success signals

Not download counts — household behavior:

- Someone in the home can point to where a bright planet is *without* opening the app.
- At least one unprompted question per week (“why is it lower than last month?”).
- Guests get a 30-second tour that uses the walls, not a screen.
- Children (or adults) know the Moon’s phase and at least two planets by sky direction.
- The system is still correct when checked against the real sky at a window.

---

## Relationship to “walking on those worlds”

This project does not build rockets. It builds **intimacy with direction, distance, and what is already known** — the same intimacy that makes later learning, advocacy, and exploration feel personal rather than abstract. The living room is the rehearsal space for caring about surfaces we have only touched with robots (so far).

---

## Open questions (to decide when building)

1. **Single household vs shareable configs** — is multi-user / multi-city a goal early, or a fork of `config.json` forever?
2. **How ambient is ambient?** — silent wall marks vs always-on display vs light that moves.
3. **Language / locale** — symbols and short cards only, or full i18n.
4. **Dark-sky vs light-polluted defaults** — magnitude cutoffs should probably default to city-honest.
5. **License for bundled imagery and mission text** — stick to clearly reusable public domain / open licenses.

---

## Summary

We already own the hard conceptual leap: **map the real sky onto the room**. The path forward is to make that map (1) accurate at “now,” (2) rich enough to include Moon, motion, and human spacecraft, (3) ambient enough to ignore until it isn’t, and (4) annotated with the small truths and open questions that turn a sticker on the wall into a lifelong habit of looking up — and wanting to go.
