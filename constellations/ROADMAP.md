# Roadmap

## Vision

Stars are meant to be discovered and looked at. This project exists to make that easy: anyone, anywhere on Earth, can step outside, look up, and *recognize* what they see — so the night sky starts to feel like home, not a blank dark ceiling.

The pipeline today answers a precise engineering question: *from this lat/lon, which IAU constellations clear the horizon between astronomical dusk and dawn, and how do their altitude and azimuth move through the night?* That is a solid foundation. The product question is larger: *what would make a person put down their phone, walk outside, and keep looking?*

Everything below is ordered toward that feeling — recognition, curiosity, and the habit of going out.

---

## Where we are

| Strength | Gap |
|---|---|
| Real IAU boundaries + official art | Fixed observer (one `config.json` location) |
| Dusk→dawn visibility window | Plots are accurate but hard to use *outside* |
| Azimuth (cardinals) + altitude over time | No “look this way now” snapshot of the sky |
| Offline data + offline tests | No path for someone far from Saigon without editing config |
| One PNG per constellation | No “what should I learn first tonight?” story |

Personal notes that drive design (see also `TODO.md`):

- The graphs are precise but disorienting when you are under the real sky.
- Orientation usually comes from buildings and landmarks, not abstract degrees.
- Reference art quality is uneven (some GIFs are low-res).

---

## Principles

1. **Outside first.** Every feature should improve the moment of standing under the sky, not only the moment of staring at a chart indoors.
2. **Anywhere on Earth.** Location is an input, never a hardcoded home. Hemispheres, seasons, and polar nights are first-class.
3. **Recognition over encyclopedia.** Prefer a few learnable shapes over dumping all 88 constellations at once.
4. **Discovery, not consumption.** The win is a person who can find Orion or the Southern Cross without the tool open. Screens are a bridge to bare-eye seeing.
5. **Honest sky.** Light pollution, clouds, and low altitude matter; do not promise a planetarium if the user has a washed-out city sky.
6. **Keep the core honest.** Visibility math stays grounded in IAU data and real astronomy libraries; polish never replaces correctness.

---

## Horizon 1 — Feel at home *here* (near term)

Make the existing pipeline useful the night you walk out the door — still local, still plot-centric, but oriented to human navigation.

### 1.1 Any place, not one city

- Treat `config.json` as a profile: lat, lon, elevation, timezone (already partly there); document how to set it for *your* roof.
- Optional: resolve place name → coordinates (or accept city presets) so “tonight from Hanoi / Lisbon / Buenos Aires” is one step, not a geodesy homework.
- Label every plot with place + date so shared images carry context.

### 1.2 “Look now” sky, not only time series

Altitude and azimuth vs time are powerful *after* you know where to look; they are weak as the first glance.

- Add a **sky snapshot** for a chosen local time (e.g. “now”, or 22:00): direction of the constellation’s center (or brightest anchor), altitude, and a short phrase like *“southwest, about halfway up.”*
- Prefer **cardinal language and body-relative cues** (“toward the sunset side,” “above the northern horizon”) over bare degree dumps in titles and summaries.
- Surface **culmination** (highest point) when it falls inside the night window — a natural “best look” moment.

### 1.3 Landmarks and local frame

From the field notes: people orient by buildings and streets, not 0–360° ticks.

- Support a small set of **local landmarks** in config (name + azimuth, optional altitude min/max): *“between the tower and the river,” “above the apartment block to the east.”*
- Optional later: a **horizon strip** — simplified silhouette or labeled azimuth bands for “my balcony” — so plots match the real view corridor.
- Keep landmark data personal and local (config / untracked file); do not force one city’s skyline on the world.

### 1.4 Tonight’s short list

- Rank visible constellations for *this* night and place: high altitude, long visibility window, and (when we have it) brightness / ease of recognition.
- Emit a **tonight card**: top 3–5 to learn, each with when and which way — not 88 equal PNGs with equal weight.
- Separate **never visible from here** from **visible but low / brief**, so people in different latitudes get honest expectations.

### 1.5 Clearer plots, better art

- Fix low-res / missing GIF cases (re-source or regenerate reference art where IAU assets fail).
- De-emphasize charts for objects below the horizon; lead with the ones you can actually see.
- Consistent naming, place/date in titles, readable type for phone screens.

---

## Horizon 2 — Feel at home *in the sky* (mid term)

Shift from “data about constellations” to “I know this shape when I see it.”

### 2.1 Stars you can actually use

- Layer **bright stars and simple stick figures** (not only IAU polygons). Recognition is of stars and lines people can hold in memory.
- Teach **anchor asterisms** first: Big Dipper / Plough, Summer Triangle, Southern Cross, Orion’s Belt, Teapot — then the full constellation around them.
- Magnitude cuts and light-pollution presets: *city*, *suburb*, *dark* — so the chart matches what the eye can get.

### 2.2 Learning paths, not catalogs

- **Seasonal paths** for a latitude band: “three shapes this month,” ordered by how easy they are to spot.
- **Story + science in one breath**: a short cultural name or myth *and* a factual hook (distance, type of star, “this is a galaxy not a star”) — enough to care, not a textbook.
- Progress that rewards bare-eye success: “found it without the plot” matters more than “opened every PNG.”

### 2.3 Plan a night, then go

- One-command **evening plan**: best window between dusk and dawn, moon brightness, maybe cloudiness if a weather API is worth the dependency.
- Multi-night / season view: when does this constellation return to a convenient hour? Builds anticipation instead of one-off plots.
- Export for the pocket: a single-page PDF or image set sized for phone, offline under dark-sky conditions.

### 2.4 Share the sky without gatekeeping

- Same pipeline, many places: generate “tonight from *X*” packs so friends in other countries can compare skies.
- Language-friendly names (local common names alongside IAU Latin) where data exists — recognition is cultural as well as geometric.
- Keep the barrier low: `uv` + `make` stays valid; optional simpler install story for non-developers later.

---

## Horizon 3 — Inspire everyone (longer arc)

Only when Horizons 1–2 still feel true. These are product directions, not commitments to rebuild the repo tomorrow.

### 3.1 Meet people where they live

- Web or lightweight app: enter a place (or use GPS), get *tonight’s* short list and a look-now sketch.
- Hemisphere-aware defaults so southern users are not forever second-class to northern star lore.
- Accessibility: high contrast, large type, screen-reader-friendly “look southwest, high” summaries.

### 3.2 Live orientation (carefully)

- Compass-backed “hold phone up” mode is powerful and also a trap — it can replace looking with AR clutter.
- If pursued: use it as a **training wheel** (align once, put the phone down), not as the main experience.
- Respect battery, night vision (red mode), and “put it away” as a first-class UX goal.

### 3.3 Community of looking up

- Shared “first find” moments and local dark-sky tips — inspiration scales through people, not only pixels.
- Partner with educators, parks, and astronomy clubs: printable one-pagers for school nights and public star parties.
- Stay free of ad-driven sky anxiety; discovery should feel calm.

### 3.4 What stays out of scope (unless the vision needs it)

Interactive full-sky atlas as a default product, heavy real-time AR as the centerpiece, packaging as a generic astronomy library, and committing large generated plot trees to git — unless they clearly serve “go outside and recognize.”

---

## Suggested sequence

| Order | Outcome | Why first |
|---|---|---|
| 1 | Multi-location config + labeled “tonight from *place*” | Unlocks the whole planet without rewriting math |
| 2 | Look-now summary + ranked tonight list | Turns 88 plots into something you can act on outside |
| 3 | Landmark / horizon framing | Fixes the disorientation called out in field use |
| 4 | Bright stars + asterism-first teaching | Recognition, not only boundaries |
| 5 | Pocket export + seasonal paths | Habit formation across nights |
| 6 | Broader surfaces (web, careful live mode, community) | Scale inspiration once the outdoor loop is solid |

---

## Success looks like

- Someone far from the original observer location can set a place in minutes and trust the night plan.
- A first-time user walks outside with **three names**, a direction, and a time window — and finds at least one shape.
- Returning users need the tool less: the sky itself becomes the map.
- People in both hemispheres, cities and dark sites, feel invited — not filtered out by latitude, jargon, or light pollution denial.

The code already knows *when* a constellation is up. The roadmap is to make people *want* to go find it — and to feel, over time, that those points of light are familiar neighbors.
