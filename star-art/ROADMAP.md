# Roadmap

A compass for wandering, not a backlog for shipping.

This project turns real star positions into quiet, ink-wash images. The point is not to build a tool or teach astronomy. It is to sit with the feeling of looking up from a city — seeing almost nothing — and still knowing that the rest is there: vast, old, and indifferent to whether anyone notices.

---

## North star

**Make the invisible feel present.**

Every direction below asks the same question in a different way: *What would it mean to wonder at the scale of the night sky from where I actually stand?*

## Why keep going

Light pollution has made the night sky invisible to most people who could
otherwise see it. Turning real star positions into something felt rather
than just plotted is a way of giving that back — and doing it as art
rather than a star-chart app is the whole point: precision in service of
feeling, not the reverse.

## What it opens up

Once the negative-constellation and precession-diptych ideas ship, the
same "real astronomical data, rendered as something to sit with" technique
becomes portable to other datasets in this account that are currently
treated as purely analytical — sound, traffic, running routes.

## Connects to

- **gpx-art**, **[private]** — same lineage: real physical/positional data
  rendered as quiet ink-wash images, different source signal.
- **stargazing-on-the-run**, **[private]** — same sky, oriented
  toward personal experience (a specific run, a specific photo) rather
  than the general compositions this repo explores.
- **space-images** — real mission imagery this repo's renders could sit
  alongside as documentary counterpoint to the generated ink washes.

---

## Where we are

The codebase already does several things well:

- Renders real star fields from the Hipparcos catalog at astronomical dusk
- Projects the sky in a stereographic view (zenith-centered, 180° field of view)
- Draws in a **sumi** style — pale paper, dark ink, magnitude as size and opacity
- Maps named stars, planets, galaxies, nebulae, clusters, and exotic objects (black holes, quasars, pulsars)
- Connects bright stars with a wandering path (**wabi-sabi minimal**)
- Steps through a full night as a timelapse

Locations today are dark-sky sites and observatories. Magnitude cutoff is generous (~12.4), so images show thousands of stars — far more than a city dweller ever sees. That gap is the artistic opportunity.

---

## Direction 1: The city sky

*Start where you actually look up.*

### What you see vs. what is there

Generate pairs (or overlays) from the **same coordinates and moment**:

| Layer | Magnitude limit | Feeling |
|-------|-----------------|---------|
| City glance | ~3–4 | Orion's belt, a few lonely points |
| Suburban | ~5–6 | Familiar constellations emerge |
| Dark site | ~12+ | The field you have now |

The city image might be nearly empty. The full image might be dense. Hold them side by side — or ghost the hidden stars behind the visible few — and let the contrast do the work.

### Your places, not tourist dark sites

Add personally meaningful coordinates: your apartment window, the bus stop, a rooftop, a childhood backyard, a park bench. The TODO already points here. These locations matter more than Mauna Kea for this project.

### Light pollution as atmosphere, not error

Do not simulate Bortle classes for accuracy. Instead, treat dimming as a **deliberate artistic filter**: fewer dots, more silence, longer gaps between ink marks. The sky is not broken — it is *withheld*.

---

## Direction 2: Scale made tangible

*Numbers are not the art. Felt distance is.*

### Magnitude as metaphor

Brighter stars are already larger and darker in sumi. Push further:

- **Size** — Betelgeuse and Proxima Centauri should not feel like peers
- **Opacity** — faint stars as breath on paper, almost not there
- **Absence** — mark where a famous star sits below the city's visibility threshold (a circle with nothing inside, a label in the margin)

### Distance without lecture

Optional quiet annotations — not infographics:

- "4 light-years" beside the nearest named star
- "2.5 million" beside Andromeda
- "26,000" beside Sagittarius A*

Small text, monospace, like the existing footer. Let the reader stumble on scale rather than be taught it.

### Depth: looking from the side

The TODO asks: *what if I looked at the stars from the side?* A 3D scatter — even crude — where proximity to the viewer changes size or tone could make the dome feel like a volume. The night sky is not a plate on the ceiling; it is a shell we live inside.

### Deep objects as anchors

Galaxies and exotic objects are already in the codebase. From a city they are **invisible by definition**. Render them anyway — single points, or points with halos — on the same canvas as the stars you can see. A map of what is overhead that your eyes cannot reach.

---

## Direction 3: Time and motion

*The sky you missed while you were inside.*

### One night, one place

Timelapse exists. Use it for **contemplation**, not documentation: watch the field rotate, stars rise and set, the pattern breathe. Consider slower frame intervals, or a single long arc showing star trails as ink strokes.

### The sky on a day that mattered

Pick a date — birthday, anniversary, the night you moved cities — and render that evening's sky from your window. The stars were there. You may not have looked.

### Seasonal return

Same location, four dates (solstices and equinoxes). How little changes in the constellations you recognize, how much churns in the faint field beneath.

### Historical drift

Precession moves the poles over centuries. A diptych: sky tonight vs. sky in 12,000 BCE from the same spot. Wonder at how temporary our constellations are.

---

## Direction 4: Constellation and path

*Finding patterns in sparse data.*

### Named stars in the city

The named-star scripts label bright stars and draw a shortest path between them. From a light-polluted site, the path might connect only five or six points across a mostly blank circle — **a constellation as a sparse poem**, not a connect-the-dots worksheet.

### Paths that mean something

Instead of TSP-optimized routes, try:

- A path following a myth (Orion's outline, the Summer Triangle)
- A path from your city to a dark-sky place you have never visited (great circle as ink stroke on a star map)
- A path through objects only — planets, then nearest star, then Andromeda, then a quasar — each step a jump in scale

### Negative constellations

Draw the shape of a familiar constellation, but only place stars where they fall **below** the visibility cutoff. The outline exists; the members are gone. Cassiopeia as an empty W.

---

## Direction 5: Visual languages

*More ways to wonder with the same data.*

The **sumi** palette (`#fdfdf9` paper, `#1a1a1a` ink) is the root. Branch without abandoning restraint:

| Style | Idea |
|-------|------|
| **Inverse night** | True black ground, stars as withheld light — closer to what the eye expects outdoors |
| **Faded memory** | Single location rendered at increasing magnitude limits, stacked with decreasing opacity — layers of what you could see if you kept looking longer |
| **Horizon slice** | Narrow altitude band instead of zenith view — the strip above rooftops and treelines, where city dwellers actually gaze |
| **Zenith only** | Tiny FOV at the pole — obsessive detail in a coin-sized patch of sky |
| **Ink wash gradient** | Milky Way band as a soft gray wash behind point stars (requires knowing which stars lie in the galactic plane) |
| **One star** | A single object, centered, enormous margins — Proxima, Polaris, Sirius — portrait of a neighbor |

Register new styles with the existing `@style` decorator pattern in `star-art.py`. Each style is an experiment, not a commitment.

---

## Direction 6: Series and sequences

*Artworks that ask to be lived with over time.*

### Daily zenith

One image per day from home, same parameters, for a month. A calendar of sameness and drift.

### World tour, same moment

All locations in `stargazing-locations.json` at the same UTC instant — how the dome changes with latitude. Then contrast with **one** city location in the same grid.

### Magnitude ladder

One place, one night, ten images from mag 2 to mag 12. Print them in a row. Watch the sky fill in like tide coming in.

### Object suites

Run `make galaxies`, `make exotic`, `make planets` from a city coordinate. Gallery walls of things overhead that no city eye has ever resolved.

---

## Direction 7: Objects for the wall and the hand

*No app. Things you can pin up or fold away.*

- **Print scale** — existing output is 12×12 at 300 DPI; consider formats for A4, A3, or long panoramic strips (horizon slice)
- **Diptychs and triptychs** — city / suburb / dark as a single composed piece
- **Zine** — one location, one night, twelve pages: planets, bright stars, faint field, galaxies, exotic objects, each on its own spread with a line of text
- **Postcard from a quasar** — one deep object, one distance, one date; mail it to someone
- **Flipbook** — timelapse frames as a physical sequence

---

## Suggested wandering order

Loose sequence if you want a path without turning this into a project plan:

1. **Add your window** to `stargazing-locations.json`
2. **Render at mag 3.5** from that spot — sit with how little appears
3. **Pair it** with mag 12 from the same coordinates
4. **Named stars + path** at city magnitude — sparse wabi-sabi
5. **One historical night** — a date that matters to you
6. **One deep object** — Andromeda or Sgr A* labeled with distance
7. **Try one new style** — inverse night or horizon slice
8. **Timelapse from home** — a night you are actually awake for

Stop when something catches. There is no finish line.

---

## What this is not

- Not a stargazing guide or light-pollution advocacy tool
- Not a replacement for going somewhere dark (though it may make you want to)
- Not concerned with scientific publication or catalog completeness
- Not asking for an audience, a product, or a use case

It is practice for looking up and feeling small — in a good way — from exactly where you are.

---

## Open questions to sit with

- Does showing *more* stars increase wonder, or does **emptiness** do more work from the city?
- Should artworks include the footer metadata, or is silence better for wall pieces?
- Is accuracy a form of respect, or is poetic license allowed when it serves the feeling?
- When you finally see a dark sky in person, will the images still matter?

Leave answers unsettled. Revise this roadmap when a direction stops pulling you.
