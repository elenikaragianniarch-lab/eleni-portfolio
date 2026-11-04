# Night Walk — approved design (4 Nov 2026)

Eleni approved this version. Change only on her request. Checkpoint: git tag `nightwalk-design-v1`.

## Type
- Inter Tight (text, headings, light weights) + Roboto Mono (labels, numbers, legend, caps). Self-hosted from ../fonts/.
- No outlines/halos on any line or label.

## Page
- Dark UI: page/panel #1B1B1B, text #ECECEC, muted #8B8B8B, hairlines #343434. Square buttons (no rounded pills).
- Top-left link "← Eleni Karagianni" back to the portfolio (../#night-walk, target _top).
- Tabs: Find my route | City map.

## Map (route view) — after the Po river reference
- Land #3D3834 (warm taupe) inside a crisp frame (#9A9590 1px) with ticks; thin full grid every 250 m (white 7%); lat/lon labels on top and left (Roboto Mono, #9A9590).
- Streets: lit (tagged) cream #EFE6D8 line at 42% opacity; estimated-lit 22%; dark streets = faint cream dots (18%). Lit streets switch on in rings from the start point on load.
- Canal: pale grey band #C4C4C2 at 38%. Parks: forest-dot pattern (#3B302A ground, #8C5A3C ring, #D4975F centre) at 55%.
- Night venues: small red squares #E0412F at 45%.
- Dark veil #0E0D0C at 58% over the whole map; risk boxes are cut out so they keep the lighter colour.
- Safest route: dusty red-pink #E3495F, 5.5 px, no casing. Shortest route: white dotted (0.01/6.5 dash, 3.2 px), no casing.
- Four walkers always shown, thin 2 px, offset side by side like a metro map: Maya #8F7B58, Sam #6A7C88, Leila #76866A, Jo #8A7A70.
- Risk boxes: one per event on the short way (each underpass; unlit stretches in ~200 m chunks), up to 5, non-overlapping. White rect + heavier corner brackets. Label strip: numbered square + salmon (#E8785E) caps name.
- Headline top-left on #1B1B1B: white sentence + salmon second sentence, e.g. "The quick way follows the unlit Regent's Canal towpath through 9 underpasses. The safe way stays on lit streets, 7 min longer."
- Legend strip along the bottom with swatches.
- Markers: A light grey disc, B pink disc; station labels white mono caps, no halo.
- Side panel: Safest/Shortest card (safest in pink), "Risks on the short way" two-column grid of numbered tiles (zoomed map via <use href="#world">, salmon caps title, one-line note), reasons list, Start walking (pink) + Preview the walk.

## City map
- All four layers overlaid by default; buttons toggle (All together / single / add-remove).
- Safe corridors: sage #A3B58C (width by use). Streets the safe route avoids: salmon #E8785E (width by trips). Weakest streets: fine cream dots; strongest: thin grey #6E6A64. Where safety costs time: circles filled with white dots, no outline.
- Headline: "2,560 simulated walks, all on one map. Where the safe way costs time, and which streets to fix."

## Default
- Camden Market → Granary Square (shortest takes the canal towpath; four walkers differ).

## Portfolio
- Thumbnail img/w08.png: halftone (12 px grid, offset rows), grey dot field, light streets, bold black safe route. Hover img/c08.jpg: the dark taupe map.
