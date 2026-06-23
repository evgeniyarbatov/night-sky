# Roadmap

> Know the night sky as well as you know the streets you run.

This project started with a simple observation: runners spend hours under the open sky, yet the stars above remain strangers. When a cloudless night finally arrives, the sky can feel more alien than familiar — a scatter of lights with no names, no stories, no sense of place. The streets are home. The sky is not.

This roadmap turns that around. The goal is not just to *see* what was overhead on a given run, but to build a lasting relationship with the night sky — so that when you happen to run under the stars, you feel oriented, curious, and quietly awestruck. At home in the cosmos. Wondering about it as a human being. Reaching for the stars, truly.

---

## North Star

**Feel at home in the night sky.**

That means:

- **Recognition** — Orion is not a random bright patch; it is *your* winter companion on the river path.
- **Orientation** — You know which way is north, what rises in the east on this route, what season the sky belongs to.
- **Wonder** — Each run can surface a single thought worth carrying: how far that light has traveled, what a constellation meant to someone ten thousand years ago, how small and how large we are.
- **Reach** — The sky stops being wallpaper and becomes something you move toward — in attention, in knowledge, in imagination.

The existing pipeline (GPX → sky reconstruction → maps → video) is the first step: *recovering* the sky you ran through but could not read. Everything below extends that into *learning*, *anticipation*, and *inspiration*.

---

## What Exists Today

| Capability | Status |
|---|---|
| Parse GPX traces (lat, lon, heading, time) | Done |
| Select distinctive viewpoints along a route | Done |
| Render sky at each point via Stellarium | Done |
| Overlay map + direction arrow on sky image | Done |
| Merge into slideshow / video | Done |
| Multiple elevation angles (horizon, 30°, 70°) | Done |
| Variable field of view (zoom) | Planned ([TODO.md](TODO.md)) |

The current workflow is **retrospective**: after a run, reconstruct what was above you. The roadmap adds **prospective** and **pedagogical** layers — preparing you before a night run and helping you recognize what you see while the memory is fresh.

---

## Principles

1. **Runs are the frame.** Every feature should connect to a real route, a real time, a real direction of travel. Abstract planetarium sessions are not the product; *your* sky on *your* run is.

2. **One thing at a time.** A single constellation, one bright star, one fact, one question. Runners are moving; the sky teaches in glances, not lectures.

3. **Seasons and returns.** Familiarity comes from seeing the same sky again on the same streets. The product should track how your routes change with the year.

4. **Wonder over trivia.** Distance in light-years matters less than the feeling that photons left that star before you were born and arrived on your run tonight.

5. **Offline-first, low-friction.** Night runs are cold, dark, and phone-conserving. Post-run artifacts and optional pre-run briefings beat real-time AR as the near-term focus.

---

## Phases

### Phase 1 — Recover the Sky You Missed
*Make the invisible visible after every night run.*

The foundation is already built. This phase hardens it and makes the output more legible.

**Goals**
- Run the full pipeline on any GPX file without hardcoded paths or local-only assumptions.
- Produce a per-run **sky log**: for each viewpoint, what you were facing and what was there.

**Deliverables**
- [ ] Configurable GPX input (drop a file in `data/gpx/`, no personal path in `scripts/gpx.py`).
- [ ] **Sky object manifest** per screenshot: brightest stars, visible planets, moon phase, named constellations in the field of view (via Stellarium scripting or a Python sky library such as [Skyfield](https://rhodesmill.org/skyfield/)).
- [ ] Annotated output: labels on merged images or a sidecar JSON/Markdown summary per run.
- [ ] FOV variation — same direction, tighter zoom on a notable object ([TODO.md](TODO.md)).
- [ ] README walkthrough with a sample GPX so anyone can reproduce a sky log in one `make` invocation.

**Success criterion:** After a night run, open one folder and answer: *What was that bright thing in the southeast at minute 23?*

---

### Phase 2 — Learn Your Running Sky
*Turn reconstruction into recognition.*

**Goals**
- Build familiarity with the patches of sky visible from your regular routes.
- Connect names, shapes, and stories to the directions you actually run.

**Deliverables**
- [ ] **Route sky profile** — a static or slowly-updated chart: "On the Tuesday loop, facing north at 6 a.m. in January, you see …"
- [ ] **Constellation cards** — one image + 3 sentences per constellation encountered on a route (myth, science, or a single wonder-prompt).
- [ ] **Seasonal rotation view** — same route, same direction, sky at monthly intervals; see how Orion yields to Leo yields to Cygnus.
- [ ] **Personal sky index** — a running list of objects and constellations you have "met" on runs (first seen date, route, direction).
- [ ] Light pollution layer on maps (e.g. [Light Pollution Map](https://www.lightpollutionmap.info/) tiles or Bortle estimate from coordinates).

**Success criterion:** On a clear night, before you look up, you can name one thing you expect to see on a familiar route — and when you look, it is there.

---

### Phase 3 — Anticipate the Night
*Prepare before you lace up.*

Night runs are rare. When one is possible, a short briefing turns chance into intention.

**Deliverables**
- [ ] **Tonight preview** — given a GPX route and a planned start time, generate: moon rise/set, visible planets, 1–3 "look for this" highlights by segment of the run.
- [ ] **Clear-sky window** — optional weather / cloud integration (e.g. Open-Meteo) for the run's time and location.
- [ ] **Printable or phone-glance card** — single page: route map + direction arrows + "at km 3, look south for …"
- [ ] **Audio-friendly script** — optional text-to-speech or podcast-style 5-minute "sky for tonight's run" from the same data.

**Success criterion:** You choose to run at night because you know something worth seeing will be overhead — not because you happened to notice it was clear.

---

### Phase 4 — Wonder & Reach
*Inspiration as a first-class output.*

Technical accuracy serves a human end: feeling part of something vast and ancient.

**Deliverables**
- [ ] **Wonder prompts** — one question per run or per viewpoint, tied to what is visible (e.g. "The light from this star left before your last marathon — what else happened in that span of time?").
- [ ] **Scale moments** — occasional overlays or captions: distance, age, size comparisons that respect the runner's pace (distances in "minutes at your easy pace" as well as light-years).
- [ ] **Deep-sky highlights** — when a nebula, cluster, or galaxy is technically visible from your site, note it even if the eye cannot resolve it; imagination counts.
- [ ] **Sky journal** — append reflections to a run's sky log; over months, reread how the same corner of sky felt in different seasons and moods.
- [ ] **Annual recap video** — all night runs in a year, same pipeline as today, with a narration layer drawn from your journal and object index.

**Success criterion:** You finish a night run with one thought you did not have before — about the universe, not about your split times.

---

### Phase 5 — Portable Sky (Optional)
*Reduce dependency on Stellarium; open the project to more people.*

Stellarium is powerful but desktop-bound. Longer term, native Python rendering improves CI, sharing, and mobile-adjacent workflows.

**Deliverables**
- [ ] Skyfield- (or similar) based renderer for core screenshots; Stellarium as optional high-fidelity path.
- [ ] Web viewer for sky logs and route profiles (static site from generated JSON + images).
- [ ] Explore watch / phone integrations only if they serve Phases 2–4 without distracting from the run.

**Success criterion:** A new contributor generates a sky log without installing Stellarium.

---

## Suggested Order of Work

```
Phase 1 (harden + annotate)  →  Phase 2 (learn routes)  →  Phase 3 (preview)
                                        ↓
                               Phase 4 (wonder)  —  weave in from Phase 2 onward
                                        ↓
                               Phase 5 (portable)  —  when annotation needs outgrow Stellarium
```

Phase 4 is not a separate product; wonder-prompts and journal hooks should appear as soon as Phase 1 produces named objects. Even a single line — *"This is Sirius, the brightest star in Earth's night sky"* — is Phase 4 in miniature.

---

## Metrics That Matter

Avoid vanity counts. Track relationship with the sky:

| Metric | Meaning |
|---|---|
| Constellations recognized on a route without checking | Familiarity |
| Night runs chosen partly for the sky | Anticipation |
| Sky log entries revisited after a month | Memory |
| Journal entries written | Wonder |
| Same route, different season — objects noted | Continuity |

---

## Open Questions

- **Culture:** Western constellation names are the default in Stellarium today. When should Indigenous, Chinese, or Arabic star lore appear alongside or instead?
- **Hemisphere & travel:** Runs abroad produce unfamiliar skies. Is that a feature (sky travelogue) or noise?
- **Urban runners:** Heavy light pollution limits stars. Do we lean into planets, moon, and bright stars only, or map "dark enough" segments of a route?
- **Privacy:** GPX files are personal. Default to local-only processing; document what leaves the machine if a web viewer ships.

---

## How This Connects to the Original Story

The [README](README.md) asked for a simple parity: know the night sky like the streets. Streets are learned by repetition — the same corners, season after season, until they are muscle memory. The sky works the same way, but we rarely give it the reps.

This project uses runs as those reps. Each GPX file is a diary of where your body went; the pipeline reveals where your attention could have gone. Over time, the sky above your regular routes becomes as known as the turn at the oak tree — not because you studied astronomy in a classroom, but because you kept showing up, in the dark, on the move, as a human being under the stars.

That is the roadmap: from *unfamiliar scatter* to *recognized home* to *quiet awe* — one run at a time.