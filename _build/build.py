"""Builds the static site from the content below.

Run from the repo root:  python3 _build/build.py
Writes index.html, about/index.html and one folder per project.
"""
import html, json, os
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://www.eleni-karagianni.com"
MAIL = "eleni.karagianni.arch@gmail.com"
LINKS = [
    ("LinkedIn", "https://www.linkedin.com/in/elenikaragiannii/"),
    ("GitHub", "https://github.com/elenikaragianniarch-lab"),
    ("Instagram", "https://www.instagram.com/eleni_karagianni_arch/"),
    ("CV (PDF)", "/files/Eleni_Karagianni_CV.pdf"),
]
e = html.escape


def size(src):
    with Image.open(os.path.join(ROOT, src.lstrip("/"))) as im:
        return im.size


# ---------------------------------------------------------------- blocks
def img(src, alt="", cap="", zoom=True, lazy=True):
    w, h = size(src)
    z = ' class="zoom"' if zoom else ""
    ld = ' loading="lazy" decoding="async"' if lazy else ' fetchpriority="high"'
    c = f'<figcaption class="cap">{cap}</figcaption>' if cap else ""
    return f'<figure class="fig"><img src="{src}" width="{w}" height="{h}" alt="{e(alt)}"{z}{ld}>{c}</figure>'


def vid(src, poster, cap="", alt=""):
    w, h = size(poster)
    c = f'<figcaption class="cap">{cap}</figcaption>' if cap else ""
    return (f'<figure class="fig"><video data-loop muted loop playsinline preload="none" poster="{poster}" '
            f'width="{w}" height="{h}" aria-label="{e(alt or cap)}"><source src="{src}" type="video/mp4"></video>{c}</figure>')


def yt(id_, poster, title, cap=""):
    c = f'<figcaption class="cap">{cap}</figcaption>' if cap else ""
    return (f'<figure class="fig"><button class="yt" type="button" data-id="{id_}" data-title="{e(title)}">'
            f'<img src="{poster}" alt="" loading="lazy"><span class="play">Play film</span></button>{c}</figure>')


def row(kind, *figs, extra=""):
    # A single still narrower than the column would be blown up: show it inset instead.
    if kind == "full" and "<video" not in figs[0]:
        import re
        w = int(re.search(r'width="(\d+)"', figs[0]).group(1))
        if w < 1300:
            kind = "inset"
    return f'<div class="row {kind}"{extra}>{"".join(figs)}</div>'


def text(h, *paras, note=""):
    body = "".join(p if p.startswith(("<ol", "<ul", "<p")) else f"<p>{p}</p>" for p in paras)
    n = f'<p class="note meta">{note}</p>' if note else ""
    return f'<section class="text grid"><h2>{h}</h2><div class="prose">{body}</div>{n}</section>'


def facts(h, intro, items, after=""):
    f = "".join(f"<div><b>{a}</b><span>{b}</span></div>" for a, b in items)
    i = f'<div class="prose"><p>{intro}</p></div>' if intro else '<div class="prose"></div>'
    a = f'<div class="note prose"><p>{after}</p></div>' if after else ""
    return f'<section class="text grid"><h2>{h}</h2>{i}<div class="facts">{f}</div>{a}</section>'


def steps(h, items, stack=""):
    li = "".join(f"<li><strong>{a}.</strong> {b}</li>" for a, b in items)
    s = f'<p class="note meta">{stack}</p>' if stack else ""
    return f'<section class="text grid"><h2>{h}</h2><div class="prose"><ol>{li}</ol></div>{s}</section>'


def quote(q, who):
    return f'<section class="quote grid"><blockquote>{q}</blockquote><cite class="meta">{who}</cite></section>'


def explore(items, also=""):
    li = "".join(f'<li><a href="{u}"{" target=_blank rel=noopener" if u.startswith("http") else ""}><span>{t}</span><span>{d}</span></a></li>' for t, u, d in items)
    a = f'<p class="also meta">{also}</p>' if also else ""
    return f'<section class="explore grid"><h2>Explore</h2><ul>{li}</ul>{a}</section>'


def ext(t, u):
    return f'<a href="{u}" target="_blank" rel="noopener">{t}</a>'


# ---------------------------------------------------------------- projects
M = "/media"
PROJECTS = []


def project(**k):
    PROJECTS.append(k)


project(
    slug="nine-acts", title="Nine Acts of Ostranenie", short="Nine Acts", year="2026",
    kind="Multi-agent AI, archive, 3D",
    one="Nine AI agents read Rotterdam through its books, photographs and films, argue, and design rooms from the argument.",
    thumb=f"{M}/nine-acts/stair.webp", og=f"{M}/nine-acts/lead.webp",
    meta=[("Year", "2026"), ("With", "Ruijia Zheng"), ("Context", "MArch Urban Design, RC11, the Bartlett, UCL"),
          ("Tutors", "Julian Besems, Ioana Drogeanu, Andrew Porter"),
          ("Awards", "Best Computation Prize, Bartlett Urban Design 2026<br>Honorable Mention, Playing Models 2026, SCI-Arc")],
    lede="Nine AI agents read Rotterdam through its books, photographs and films, argue about what they find, and design rooms out of that argument, live in Blender. <i>Ostranenie</i> is Viktor Shklovsky's word for making the familiar strange. The project tries to do that to a city, and to the machines that read it.",
    lead=img(f"{M}/nine-acts/lead.webp", "A long room with corrugated translucent walls, black columns and large framed photographs", "The photography exhibition, one of the rooms the agents designed.", lazy=False),
    body=[
        text("The archive",
             "We scraped 177,241 items about Rotterdam into one table: 38,538 texts, 5,862 street photographs, and 60,959 stills and subtitle fragments from 5,046 films.",
             "Every item was embedded with CLIP and scored for how unusual it is, combining IsolationForest and LOF. Next to that sat a taste model trained on the items we picked by hand. The two only partly agree, and the agents inherit that gap."),
        row("full", img(f"{M}/nine-acts/archive-paths.webp", "Scatter map of the archive with paths drawn between items", "The archive as one map. Lines are contradiction paths: items that are structurally close but semantically far apart.")),
        row("two", img(f"{M}/nine-acts/archive-scatter.webp", "Dense point cloud in green and red on black", "All 177,241 items in one embedding space."),
            img(f"{M}/nine-acts/archive-explorer.webp", "Archive explorer interface with a search panel and image results", "The archive explorer: search by meaning, ranked by oddness.")),
        row("two cover", img(f"{M}/nine-acts/fieldwork-1.webp", "Reflection of a boat in green harbour water", "Fieldwork, Rotterdam."),
            img(f"{M}/nine-acts/fieldwork-2.webp", "Large sculpted heads inside a station hall", "Fieldwork, Rotterdam."), extra=' style="--ar:4/5"'),
        text("Nine agents",
             "All nine run on the same open model, hosted locally (Qwen3.6-27B). What separates them is what they can see, how they score it, which of ten tools they can use and what they remember. We did that on purpose: if they only differed in their prompts, they would drift back to the same probable answer.",
             note="Agents were run about 100 times across 14 sites along the river Maas."),
        '<section class="text grid"><h2></h2><div class="agents">'
        '<div><b>Normal Literature</b><span>Reads for the expected</span></div>'
        '<div><b>Normal Photography</b><span>Reads for the expected</span></div>'
        '<div><b>Normal Films</b><span>Reads for the expected</span></div>'
        '<div><b>Odd Literature</b><span>Reads for the strange</span></div>'
        '<div><b>Odd Photography</b><span>Reads for the strange</span></div>'
        '<div><b>Odd Films</b><span>Reads for the strange</span></div>'
        '<div><b>The Curator</b><span>Asks the human, "Is this strange to you, right now?", and recalibrates</span></div>'
        '<div><b>The Contradiction Walker</b><span>Looks for where the evidence disagrees with itself</span></div>'
        '<div><b>The Blindspot</b><span>Looks for what the archive leaves out</span></div>'
        '</div></section>',
        row("wide", img(f"{M}/nine-acts/app-discussion.webp", "Transcript of an agent discussion with linked evidence", "Step 4 of a run: 22 turns of discussion, every claim linked to the item it came from."),
            img(f"{M}/nine-acts/walker-card.webp", "Profile card of the Contradiction Walker agent with its elements", "What one agent contributed to the proposal.")),
        quote("“The label ‘street photograph’ is factually incorrect. This is a harbor scene.”", "The Contradiction Walker, harbour-yard run"),
        text("One run",
             "Each run starts from the same three inputs for a site: a text, photographs and a massing model. The agents react, pull evidence from the archive, produce text, images or 3D form (or stay silent), and then argue. Deletions are tracked, so you can see who removed whose sentence.",
             "In the harbour-yard run, five agents placed 39 elements over 22 turns. The correction above, from street to quay, moved the tallest element to the water's edge. Every proposal can be traced back to the evidence and the argument behind it."),
        row("full", img(f"{M}/nine-acts/run-3d-2.webp", "3D scene with agent-placed objects over a photogrammetry site model", "Agents' elements placed on the site model.")),
        row("three cover", img(f"{M}/nine-acts/street-1.webp", "Suspended objects over a street between historic buildings", "An early run in the city centre."),
            img(f"{M}/nine-acts/run-3d-1.webp", "Dark 3D view with floating objects", "Productions from one run."),
            img(f"{M}/nine-acts/run-3d-3.webp", "Assembled 3D objects on a grid", "Elements from five agents, assembled."), extra=' style="--ar:1/1"'),
        text("Designing in Blender",
             "Through MCP, the agents work directly in Blender. They did it in five tasks, each building on the one before. These are the screen recordings, unedited apart from length."),
        row("full", vid(f"{M}/nine-acts/blender-1.mp4", f"{M}/nine-acts/blender-1.webp", "1. Hosting activities. The agents decide what to host, how many spaces and how big.")),
        row("two", vid(f"{M}/nine-acts/blender-2.mp4", f"{M}/nine-acts/blender-2.webp", "2. Shaping from within. Each agent puts a camera inside its spaces and reshapes them."),
            vid(f"{M}/nine-acts/blender-3.mp4", f"{M}/nine-acts/blender-3.webp", "3. Components. They build and place components for each activity.")),
        row("two", vid(f"{M}/nine-acts/blender-4.mp4", f"{M}/nine-acts/blender-4.webp", "4. Gifts. They enter each other's spaces, each carrying a form as a gift."),
            vid(f"{M}/nine-acts/blender-5.mp4", f"{M}/nine-acts/blender-5.webp", "5. Materials. Each agent picks materials from its own part of the archive.")),
        row("two", img(f"{M}/nine-acts/axo-black-1.webp", "Exploded axonometric of rooms on black", "Rooms after task 3."),
            img(f"{M}/nine-acts/axo-black-2.webp", "Exploded axonometric with coloured materials on black", "The same rooms with materials applied.")),
        text("The rooms",
             "The final set has seven rooms: a reading room, a covered passage, a screening room, a meeting room, the photography exhibition, a viewing room and a conservation studio."),
        row("full", img(f"{M}/nine-acts/stair.webp", "Stair with red treads inside a reflective metallic room", "The covered passage.")),
        row("two", img(f"{M}/nine-acts/room-2.webp", "Curved metallic surfaces and a small screen in a dim room", ""),
            img(f"{M}/nine-acts/room-3.webp", "Room with a large woven copper form and a block of stone", "")),
        row("full", img(f"{M}/nine-acts/screening.webp", "Low dark room with a projector beam and amber lighting", "The screening room.")),
        row("three", img(f"{M}/nine-acts/room-4.webp", "Room with tall copper walls and a reflective bench", ""),
            img(f"{M}/nine-acts/room-6.webp", "Tall copper fins in a dark room", ""),
            img(f"{M}/nine-acts/room-7.webp", "Perforated pale metal surface", "")),
        row("two", img(f"{M}/nine-acts/material-1.webp", "Material samples: glass, stone, red cloth", "Materials chosen by two of the agents."),
            img(f"{M}/nine-acts/material-2.webp", "Material samples: stone, amber resin, dark metal", "")),
        facts("What odd images do to language",
              "Before writing the agents' voices, we had a vision-language model describe 6,000 of the photographs and compared the language used for ordinary and odd ones. Odd images made description work harder.",
              [("+65%", "verbs per description (15.12 against 9.15, p &lt; 0.001)"), ("2.5×", "negations per description"),
               ("0.251", "spatial vagueness (near, around, toward), against 0.209"), ("48%", "strong, specific verbs, against 54% for ordinary images")]),
        steps("How it works", [
            ("Archive", "Scraping with requests, BeautifulSoup, Playwright and the Flickr API into one SQLite table of 177,241 items."),
            ("Scoring", "512-dimension CLIP embeddings, SOM and UMAP maps, IsolationForest and LOF anomaly scores, a curatorial taste model, and a human–machine disagreement score."),
            ("Agents", "Nine tool-using agents on one locally hosted model, each with its own archive access, thresholds, ten tools and memory. A human stays in the loop through the Curator."),
            ("Runs", "Reactions, retrievals, productions and discussion at 14 river-edge sites, with every deletion tracked."),
            ("Blender through MCP", "The agents place, shape, furnish and texture rooms in a shared 3D scene."),
        ], stack="Python, pandas, SQLite, CLIP, MiniSom, UMAP, scikit-learn, Qwen3.6-27B (local), MCP, Blender, Plotly"),
        row("three", img(f"{M}/nine-acts/app-archive.webp", "Archive map web app", "Archive map"),
            img(f"{M}/nine-acts/app-map.webp", "Location map web app with markers", "Location map"),
            img(f"{M}/nine-acts/app-3d.webp", "3D viewer web app", "3D output")),
        explore([("Search the archive", "https://nine-acts-archive-map.vercel.app/", "Live app"),
                 ("Read a full agent discussion", "https://vercel-step4-discussion.vercel.app/", "Live app"),
                 ("Orbit one proposal in 3D", "https://vercel-3d-output.vercel.app/", "Live app")],
                also=f'Also: {ext("process blog", "https://eleni-rae.tumblr.com")} · {ext("project booklet (PDF)", "https://drive.google.com/file/d/11YgnDuLaGwM_DPTDF5XDniTneLfDmVnB/view")} · The project later became a <a class="u" href="/about/#teaching">workshop at the Bartlett</a>.'),
    ],
)

project(
    slug="night-walk", title="Night Walk", short="Night Walk", year="2026",
    kind="Prototype, safety, urban design",
    one="A route finder for walking home at night that also shows which streets to fix.",
    thumb=f"{M}/night-walk/card.webp", og=f"{M}/night-walk/route.webp",
    meta=[("Year", "2026"), ("Role", "Individual prototype"), ("Area", "King's Cross and Camden, London"), ("Status", "Working prototype, runs in the browser")],
    lede="A route finder for walking home at night that also shows which streets to fix. It compares the quick way and the safe way across 2,560 simulated walks, finds the streets that make the quick way unsafe, and tests design fixes for them before anything is built.",
    lead=vid(f"{M}/night-walk/walk.mp4", f"{M}/night-walk/route.webp", "Camden Market to Granary Square. The safe route, in pink, is seven minutes longer and stays off the unlit canal towpath."),
    body=[
        text("Why I'm building it",
             'I\'ve walked home at night choosing the route the way most women do: which street is lit, which one has people on it, which shortcut to skip. I made a short film about that fear, <a href="/the-bus/">The Bus</a>. At LOvMe.ai I worked on safety advice and spoke to women about how they move through cities at night. And my thesis, <a href="/unseen-city/">The Unseen City</a>, is about what data about cities leaves out. Night Walk is where the three meet.'),
        text("The problem",
             f'In Britain, 82% of women say they feel unsafe walking alone in a park or open space after dark ({ext("ONS, 2022", "https://www.ons.gov.uk/peoplepopulationandcommunity/crimeandjustice/bulletins/perceptionsofpersonalsafetyandexperiencesofharassmentgreatbritain/16februaryto13march2022")}). Map apps send people the quickest way, which is often the dark one. Safety apps send them around it. Neither tells a council which street to fix first, or what fixing it would change.',
             f'Public money is already going into this: the Home Office\'s {ext("Safer Streets Fund", "https://www.gov.uk/government/publications/safer-streets-fund-round-five/safer-streets-fund")} has put £159 million into 413 local projects, much of it lighting, CCTV and design.'),
        row("full", img(f"{M}/night-walk/city.webp", "Dark map of King's Cross and Camden with coloured street networks and dotted circles", "City map: all 2,560 simulated walks. Pink streets are the ones the safe route avoids; green are safe corridors; dotted circles mark where safety costs the most time.")),
        facts("What it found", "",
              [("+1.2 min", "average extra time to walk the safe way"), ("73% → 93%", "share of the walk on lit streets, quick way against safe way"),
               ("+87", "walks that no longer need a detour if the top three streets are fixed"), ("73% → 80%", "light on the quick way home after those three fixes")],
              after="Lighting the Regent's Canal towpath and opening up its underpasses does the most: 58 more walks become safe enough and 100 minutes of detours disappear. Camden Street comes next. Some streets that look bad on a map, such as Camden Road, change nothing when fixed, because people already avoid them for other reasons. That's the kind of thing a council can only see with a tool like this."),
        row("two", img(f"{M}/night-walk/fix.webp", "Map with numbered streets to fix and a ranked list", "Fix the city: streets ranked by how many walks a fix would make safe."),
            img(f"{M}/night-walk/fix-section.webp", "Before and after street section of the canal towpath with lighting", "Proposal 1, the canal towpath, after: low amber lighting, a lit underpass, late uses at ground level.")),
        steps("How it works", [
            ("Walk", "A route finder with safest and shortest routes, the cost in minutes and step-by-step navigation."),
            ("See", "2,560 simulated walks between random points show where the quick way and the safe way split."),
            ("Diagnose", "Every street is scored on light, people around, sightlines, help nearby and incidents."),
            ("Fix", "Design moves are tested on all 2,560 walks before anything is built."),
            ("Propose", "Ranked proposals with before and after sections, rough cost and who should act."),
        ], stack="Python, NumPy, SciPy, OpenStreetMap, police.uk, Dijkstra routing, minimax-regret negotiation between four walker profiles, vanilla JS and SVG. 8,165 street segments."),
        text("Who it could serve",
             "Councils and police and crime commissioners bidding for safety funding, developers and estates planning night-time public space, canal and transport operators, and consultancies writing women's safety audits. The method works for any city with open map data."),
        text("Limits",
             "The scores are rules I designed from open data (OpenStreetMap and one month of police.uk records). They haven't yet been tested with the women who walk these streets, lighting is only tagged on 59% of them, and impact is measured on simulated walks rather than real footfall. The next step is walk-alongs, a short survey and council lighting data. It is a design prototype and shouldn't be used as safety advice."),
        explore([("Open Night Walk", "/nightwalk/", "Live app")]),
    ],
)

project(
    slug="turin-machine", title="Turin Machine", short="Turin Machine", year="2025",
    kind="AI characters, language into form",
    one="Two AI characters walk Turin and talk. Their words build a space, one sentence at a time.",
    thumb=f"{M}/turin-machine/lead.webp", og=f"{M}/turin-machine/lead.webp",
    meta=[("Year", "2025"), ("Role", "Individual project"), ("Context", "MArch Urban Design, RC11, the Bartlett, UCL")],
    lede="Two AI characters walk through Turin and talk: Nietzsche, who lived there, and Franco, the blind detective from Dario Argento's <i>The Cat o' Nine Tails</i>. Their conversations are boiled down to a vocabulary of 42 words, and each word changes a 3D form, so a sentence can be built as a space.",
    lead=img(f"{M}/turin-machine/lead.webp", "Dense spatial assembly of fragments floating in a gridded room with a pink floor", "Spatial assembly built from the 42-word vocabulary.", lazy=False),
    body=[
        text("Datasets",
             "2,054 industrial buildings, 205 British Pathé films, 958 films shot in Turin, and a two-hour walk I recorded across 23 locations, cut into 30 sound fragments. The two characters only know the city through this material."),
        row("narrow", img(f"{M}/turin-machine/route.webp", "Map of Turin with the walk's locations in red", "The walk: 23 locations."),
            img(f"{M}/turin-machine/buildings.webp", "Grid of photographs of industrial buildings", "Part of the industrial building dataset.")),
        row("two", img(f"{M}/turin-machine/films.webp", "Grid of film stills", "Stills from films shot in Turin."),
            img(f"{M}/turin-machine/sound.webp", "Grid of spectrograms", "The 30 sound fragments from the walk.")),
        text("Two ways of seeing",
             "Franco reads the city through sound, touch and uncertainty. Nietzsche reads it through concepts, critique and feeling. They walk the same 23 locations, and each exchange is grounded in what the datasets hold about that place."),
        text("From talk to words",
             "TF-IDF over all the dialogues gives a vocabulary of 42 words. Each word has one of three behaviours: soft (low density, continuous), medium (balanced, partly broken) or chaotic (dense, fragmented). In Blender Geometry Nodes, each word sets density, fragmentation and continuity."),
        row("full", img(f"{M}/turin-machine/words.webp", "Grid of 42 small 3D forms, each labelled with a word", "The 42 words, each as a form."), extra=""),
        row("inset", img(f"{M}/turin-machine/vocab-chart.webp", "Bar chart of the machine's vocabulary by dataset", "The machine's vocabulary of Turin, by source.")),
        quote("“The monumental industry hum feels tired; as brick and stones become unforgiving under the sun.”", "One sentence from the dialogues, built word by word below"),
        row("full", img(f"{M}/turin-machine/sequence.webp", "Sequence of forms growing from left to right on black", "Each word adds a layer.")),
        row("two", img(f"{M}/turin-machine/assembly.webp", "Collage of a building fragment on a gridded backdrop", ""),
            img(f"{M}/turin-machine/waves.webp", "Forms floating above a curved grid", "")),
        text("Prints and spaces", "The assemblies were 3D-printed and rendered as interiors."),
        row("two", img(f"{M}/turin-machine/print.webp", "Hand holding a small 3D print among printed pieces", "3D prints of word assemblies."),
            img(f"{M}/turin-machine/material-model.webp", "Top view of a model made of many white and wooden pieces", "")),
        row("three", img(f"{M}/turin-machine/interior-1.webp", "Interior render with stairs, white figures and timber", ""),
            img(f"{M}/turin-machine/interior-2.webp", "Interior render with a balcony and white figures", ""),
            img(f"{M}/turin-machine/interior-3.webp", "Wide interior render with fragments and figures", "")),
        text("A branch I dropped",
             "I first clustered all the images with a self-organising map. It was technically sound but gave flat, unconvincing space, so I moved to the language-driven method above. The dropped branch is documented on the process blog."),
        row("two", img(f"{M}/turin-machine/som.webp", "Self-organising map of thousands of images", "The image SOM."),
            img(f"{M}/turin-machine/concept-map.webp", "Map of Turin areas placed on a chart of embeddings", "Conceptual map of Turin from image embeddings.")),
        steps("How it works", [
            ("Data", "Scraped building, film and archive datasets, plus audio segmentation of the recorded walk."),
            ("Dialogue", "Two persona agents (GPT-4o mini) talk at each location, constrained by the datasets."),
            ("Vocabulary", "TF-IDF over the dialogues, cleaned to 42 words in three behaviours."),
            ("Geometry", "Each word drives parameters in Blender Geometry Nodes; a sentence becomes a stack of forms."),
            ("Output", "3D prints, renders and a short film."),
        ], stack="Python, GPT-4o mini, TF-IDF, CLIP, SOM, audio segmentation, Blender Geometry Nodes, 3D printing, DaVinci Resolve"),
        explore([("Code on GitHub", "https://github.com/elenikaragianniarch-lab/turin-machine", "GitHub"),
                 ("Process blog", "https://eleni-karagiannii.tumblr.com", "Tumblr"),
                 ("The walk, sound only", "https://www.youtube.com/watch?v=XdMCOOmc4bs", "YouTube")]),
    ],
)

project(
    slug="unseen-city", title="The Unseen City", short="The Unseen City", year="2026",
    kind="Thesis, AI and the city",
    one="A thesis on what systems that measure cities leave out, and why.",
    thumb=None, og=None,
    meta=[("Year", "2026"), ("Type", "MArch thesis, the Bartlett, UCL"), ("Supervisor", "Elizabeth Selby"),
          ("Award", "Theory Report Prize, Bartlett Urban Design 2026, the programme's single thesis prize")],
    lede="A thesis on what the systems that measure cities leave out. It calls this the politics of noise, and argues for AI that states its point of view instead of claiming to be neutral.",
    lead='<div class="band"><p>Every system that measures a city has already decided what doesn’t count.</p></div>',
    body=[
        text("The argument",
             "<ol><li>Cities are governed by making them readable, and every reading leaves something out.</li>"
             "<li>What falls below a system's threshold gets built around as if it wasn't there. The threshold is always a decision.</li>"
             "<li>Rather than neutral machines, we should design systems that declare their partial point of view, and keep people responsible for them.</li></ol>"),
        text("Tested on",
             "<strong>MIT's Streetscore.</strong> 208,738 comparisons by 7,872 people, and about a million street views scored. Its scores track income and fail on unusual scenes.",
             '<strong>My own <a href="/nine-acts/">Nine Acts</a>.</strong> Including a critique of it: the agents who argued most also built tallest.'),
        text("Why it matters",
             "Building AI and thinking critically about it are usually separate jobs. This thesis is the other half of Nine Acts: what dataset choices, thresholds and evaluation do to a city."),
    ],
)

project(
    slug="under-common-care", title="Under Common Care", short="Under Common Care", year="2025",
    kind="Adaptive reuse, collective housing",
    one="Shared housing made from the empty buildings of one street in Volos.",
    thumb=f"{M}/under-common-care/lead.webp", og=f"{M}/under-common-care/courtyard-2.webp",
    meta=[("Year", "2025"), ("With", "Paschalina Iliadou"), ("Type", "Diploma thesis, University of Thessaly"), ("Site", "Gazi Street, Volos, Greece")],
    lede="A network of shared housing built from the abandoned buildings of Gazi Street in Volos. Empty buildings, plots and courtyards become collective homes, common rooms and neighbourhood services, connected by the street itself.",
    lead=img(f"{M}/under-common-care/lead.webp", "Render of a white building with red external stairs and stacked balconies", "Building 6, a new building on an empty plot.", lazy=False),
    body=[
        text("The site",
             "Gazi Street has many vacant buildings, housing that local people can't afford, and a shrinking mix of uses towards the centre. We treated the empty buildings as capacity waiting for a programme."),
        row("full", img(f"{M}/under-common-care/axo.webp", "Line axonometric of the street with six highlighted buildings", "Gazi Street and the six interventions.")),
        text("Six strategies",
             "Each building got a strategy based on its age and condition. A 1930s building is reorganised for public use. A 1940s warehouse frame becomes the base for four storeys of housing. Post-war buildings from 1945 to 1960 are renovated with shared rooms and added floors. A new building fills an empty plot."),
        row("full", img(f"{M}/under-common-care/strategies.webp", "Axonometric drawings of five buildings with labels", "The six intervention strategies, by construction date and condition.")),
        text("Homes and shared rooms",
             "Plans at 1:100 cover a home for single-parent families, 56 m² and 70 m² flats, and a flat shared by two families. The shared programmes are a goods-exchange shop, a café, gyms and an open-air cinema."),
        row("two contain", img(f"{M}/under-common-care/plan.webp", "Ground floor plans with furniture and courtyards", "Buildings 1 and 5, ground floor."),
            img(f"{M}/under-common-care/section.webp", "Section through a six-storey building with people and furniture", "Building 6, section.")),
        row("two", img(f"{M}/under-common-care/courtyard-1.webp", "Courtyard with café tables, trees and lamps", ""),
            img(f"{M}/under-common-care/courtyard-2.webp", "Courtyard with tables, bunting and plants", "")),
    ],
)

project(
    slug="mind-the-gap", title="Mind the Gap", short="Mind the Gap", year="2023",
    kind="Urban gaps, scaffolding",
    one="A scaffolding system for the gaps between Thessaloniki's buildings, based on what residents already do.",
    thumb=f"{M}/mind-the-gap/lead.webp", og=f"{M}/mind-the-gap/lead.webp",
    meta=[("Year", "2023"), ("With", "Katerina Aggelaki, Paschalina Iliadou"), ("Type", "Studio project, University of Thessaly"), ("Site", "Thessaloniki, Greece")],
    lede="We mapped the gaps between buildings across Thessaloniki and found residents already using them, with improvised staircases. The project turns that habit into a scaffolding system that attaches to any gap and carries a small public programme.",
    lead=img(f"{M}/mind-the-gap/lead.webp", "Colourful axonometric of scaffolding frames holding a kitchen, workspace and planting", "The scaffolding system in a gap.", lazy=False),
    body=[
        row("full", img(f"{M}/mind-the-gap/axo-map.webp", "Line axonometric of a dense urban block with highlighted gaps", "Mapping the gaps.")),
        text("What residents do",
             "Vacant lots and leftover spaces showed the same informal pattern again and again: staircases that residents had added to make use of space nobody else used. Our job was to notice their solution and make it repeatable."),
        row("narrow", img(f"{M}/mind-the-gap/gaps.webp", "Grid of black-and-white photographs of staircases in gaps", "Documenting informal staircases."),
            img(f"{M}/mind-the-gap/typology.webp", "Diagram of a scaffolding grid with five programme modules", "One structure, five programmes: cinema, library, playground, workspace and kitchen.")),
        text("The library", "The library module is developed in plans, elevation and section."),
        row("two contain", img(f"{M}/mind-the-gap/library-axo.webp", "Orange line axonometric of a library inside a scaffold between buildings", ""),
            img(f"{M}/mind-the-gap/library-drawings.webp", "Red line plans, elevation and section of the library", "Ground floor, first floor, west elevation and section.")),
        row("two", img(f"{M}/mind-the-gap/module.webp", "Render of a scaffolding module with planting on black", ""),
            img(f"{M}/mind-the-gap/playground.webp", "Yellow scaffolding playground module", "")),
    ],
)

project(
    slug="the-bus", title="The Bus", short="The Bus", year="2023",
    kind="Short film, 3′24″",
    one="A short film about walking home alone at night.",
    thumb=f"{M}/the-bus/still.webp", og=f"{M}/the-bus/still.webp",
    meta=[("Year", "2023"), ("Role", "Director, camera (with Aikaterini Angelaki), editor"), ("Length", "3′24″"), ("Course", "Image, Sound and Multimedia, University of Thessaly")],
    lede="A young woman misses her bus home after a night out and walks alone, more and more sure that someone is following her.",
    lead=yt("ZQ0DikdlK14", f"{M}/the-bus/still.webp", "The Bus", "The Bus (Το Λεωφορείο), 2023."),
    body=[
        text("The film",
             "Made by a team of five: Aikaterini Angelaki, Paschalina Iliadou, Eleni Karagianni, Anna Pantsidi and Maria Tserveni. It is based on real experiences of fear at night in the city.",
             'The same question later led to <a href="/night-walk/">Night Walk</a>.'),
    ],
)

project(
    slug="interview-dimitris", title="Interview with Dimitris", short="Interview with Dimitris", year="2023",
    kind="Documentary, 3′",
    one="A portrait of a photographer and the house he lived in.",
    thumb=f"{M}/interview-dimitris/still.webp", og=f"{M}/interview-dimitris/still.webp",
    meta=[("Year", "2023"), ("Role", "Direction, camera, edit, website"), ("Course", "Residential Practices: The Gift, with Prof. Zissis Kotionis, University of Thessaly")],
    lede="A portrait of Dimitris, a photographer living at Villa Koutarelia in Volos, and of the house itself, shortly before it closed.",
    lead=img(f"{M}/interview-dimitris/still.webp", "Still from the documentary inside Villa Koutarelia", "Villa Koutarelia, Volos.", lazy=False),
    body=[
        text("The brief",
             "Record a home as a biography of its people and things, then give something back. My gift to Dimitris was a website of his film photographs."),
    ],
)

ORDER = ["nine-acts", "night-walk", "turin-machine", "unseen-city", "under-common-care", "mind-the-gap", "the-bus", "interview-dimitris"]
BY = {p["slug"]: p for p in PROJECTS}


# ---------------------------------------------------------------- page shell
FAV = '<link rel="icon" href="/favicon.svg" type="image/svg+xml"><link rel="icon" href="/favicon.png" sizes="32x32"><link rel="apple-touch-icon" href="/apple-touch-icon.png">'


def page(path, title, desc, body, og="/og/home.jpg", nav=""):
    url = SITE + path
    ttl = title if title.startswith("Eleni") else f"{title} · Eleni Karagianni"
    def a(href, label, key):
        cur = ' aria-current="page"' if nav == key else ""
        return f'<a href="{href}"{cur}>{label}</a>'
    return f"""<!doctype html>
<html lang="en-GB">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(ttl)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Eleni Karagianni">
<meta property="og:title" content="{e(ttl)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{SITE}{og}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#ffffff">
{FAV}
<link rel="preload" href="/fonts/inter-tight-latin-wght-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/assets/site.css">
<script>window.va=window.va||function(){{(window.vaq=window.vaq||[]).push(arguments);}};</script>
<script defer src="/_vercel/insights/script.js"></script>
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="site-head wrap">
<a class="site-name" href="/">Eleni Karagianni</a>
<nav class="site-nav" aria-label="Main">{a("/#work", "Work", "work")}{a("/about/", "About", "about")}<a href="mailto:{MAIL}">Contact</a></nav>
</header>
<main id="main">
{body}
</main>
{footer()}
<script src="/assets/site.js" defer></script>
</body>
</html>
"""


def footer():
    li = "".join(f'<li><a href="{u}"{" target=_blank rel=noopener" if u.startswith("http") else ""}>{t}</a></li>' for t, u in LINKS)
    return f"""<footer class="site-foot wrap grid">
<p class="hi">Open to roles in applied AI, computational design and creative technology in London. <a href="mailto:{MAIL}">{MAIL}</a></p>
<ul>{li}</ul>
<div class="small meta"><span>© 2026 Eleni Karagianni</span><span>London</span></div>
</footer>"""


def write(path, s):
    p = os.path.join(ROOT, path.strip("/"), "index.html") if path != "/" else os.path.join(ROOT, "index.html")
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w") as f:
        f.write(s)
    print("wrote", p.replace(ROOT, ""))


# ---------------------------------------------------------------- pages
def project_page(p):
    i = ORDER.index(p["slug"])
    nxt = BY[ORDER[(i + 1) % len(ORDER)]]
    dl = "".join(f"<dt>{a}</dt><dd>{b}</dd>" for a, b in p["meta"])
    body = f"""<article>
<div class="wrap">
<header class="p-head grid"><h1>{p["title"]}</h1><p class="lede">{p["lede"]}</p><dl>{dl}</dl></header>
</div>
<div class="{"" if p["slug"] == "unseen-city" else "wrap"}"><div class="lead">{p["lead"]}</div></div>
<div class="wrap">
{"".join(p["body"])}
<nav class="next" aria-label="Next project"><span class="meta">Next</span><a href="/{nxt["slug"]}/">{nxt["title"]} →</a></nav>
</div>
</article>"""
    og = f"/og/{p['slug']}.jpg"
    desc = p["one"]
    return page(f"/{p['slug']}/", p["title"], desc, body, og=og, nav="work")


def feature(p, eager=False):
    src = p["thumb"]
    w, h = size(src)
    ld = '' if eager else ' loading="lazy"'
    return (f'<a class="feature" href="/{p["slug"]}/"><div class="media"><img src="{src}" width="{w}" height="{h}" alt=""{ld}></div>'
            f'<div class="line"><span class="t">{p["title"]}</span><span class="d">{p["one"]}</span><span class="y meta">{p["year"]}</span></div></a>')


def home():
    na = dict(BY["nine-acts"]); na["thumb"] = f"{M}/nine-acts/lead.webp"
    rows = ""
    for s in ORDER[3:]:
        p = BY[s]
        th = f'<span class="th"><img src="{p["thumb"]}" alt="" loading="lazy"></span>' if p["thumb"] else '<span class="th red"></span>'
        rows += f'<li><a href="/{s}/">{th}<span class="t">{p["title"]}</span><span class="d">{p["kind"]}</span><span class="y meta">{p["year"]}</span></a></li>'
    body = f"""<div class="wrap">
<section class="intro grid">
<h1>I’m Eleni Karagianni, an architectural engineer and computational designer in London. <span class="quiet">I build AI systems that read cities and help design them.</span></h1>
<p class="aside"><span>MArch Urban Design, the Bartlett, UCL, 2026</span><span>Open to roles in applied AI, computational design and creative technology</span><a href="/files/Eleni_Karagianni_CV.pdf">CV</a><a href="mailto:{MAIL}">Email</a></p>
</section>
<section id="work" aria-label="Selected work">
<div class="section-label"><span>Selected work</span><span>2023–2026</span></div>
{feature(na, eager=True).replace('<span class="d">', '<span class="d">Best Computation Prize, Bartlett 2026. ', 1)}
<div class="pair">{feature(BY["night-walk"])}{feature(BY["turin-machine"])}</div>
<div class="section-label"><span>More work</span><span>Thesis, architecture and film</span></div>
<ul class="index">{rows}</ul>
</section>
</div>"""
    return page("/", "Eleni Karagianni · Architectural engineer and computational designer",
                "Architectural engineer and computational designer in London. AI agents, data pipelines and spatial design. MArch Urban Design, the Bartlett, UCL.",
                body, og="/og/home.jpg", nav="work")


def about():
    def sec(h, items):
        li = "".join(f"<li><b>{a}</b>{b}{f'<span>{c}</span>' if c else ''}</li>" for a, b, c in items)
        return f"<section><h2>{h}</h2><ul>{li}</ul></section>"
    w, h = size(f"{M}/about/workshop-poster.webp")
    body = f"""<div class="wrap">
<section class="about-top grid">
<div class="ph"><img src="{M}/about/portrait.webp" alt="Eleni Karagianni" width="420" height="420"></div>
<div class="tx">
<h1>I’m an architectural engineer from Greece, licensed with the Technical Chamber of Greece (TEE), and I’ve just finished the MArch in Urban Design at the Bartlett, UCL.</h1>
<div class="prose"><p>I build working systems: archives, agents and pipelines that turn data into images, films and spaces. Most of my work asks how places are lived, seen and remembered, and by whom. Before the Bartlett I drew real buildings in Athens and Thessaloniki, and worked on an AI safety startup.</p>
<p>I’m looking for a role in London in applied AI, computational design or creative technology. I have full UK right to work.</p></div>
<p class="links"><a href="/files/Eleni_Karagianni_CV.pdf">Download CV (PDF)</a><a href="mailto:{MAIL}">{MAIL}</a><a href="https://www.linkedin.com/in/elenikaragiannii/" target="_blank" rel="noopener">LinkedIn</a></p>
</div>
</section>
<section class="text grid" id="teaching"><h2>Teaching</h2><div class="prose">
<p><strong>Designing with Disagreement</strong>, Bartlett B-Pro, October 2026. A two-week workshop I co-designed and taught with Ruijia Zheng, based on <a href="/nine-acts/">Nine Acts</a>: an introduction to computational and AI-assisted design through simple multi-agent systems. 23 students, most new to code, built agents that argue with each other.</p></div></section>
<div class="row inset poster"><figure class="fig"><img class="zoom" src="{M}/about/workshop-poster.webp" width="{w}" height="{h}" alt="Bartlett B-Pro poster for Workshop 06, Designing with Disagreement" loading="lazy"><figcaption class="cap">Workshop poster, Bartlett B-Pro 2026–27.</figcaption></figure></div>
<div class="cv grid">
{sec("Experience", [("Workshop tutor", "Bartlett B-Pro, UCL · 2026", "Designing with Disagreement, co-led with Ruijia Zheng"),
                     ("Urban safety research and advisory", "LOvMe.ai · 2023–25", "Problem framing, user interviews and urban-safety advice for an early-stage AI safety venture"),
                     ("Architectural designer", "Urban Soul Project, Athens · 2023", "Drawing sets for more than five projects at once, including PwC’s Athens campus"),
                     ("Architectural designer", "Angelos Koukoulis · 2023–24", "Adaptive reuse into housing, coordinating with engineers and clients")])}
{sec("Education", [("MArch Urban Design", "The Bartlett, UCL · 2025–26", ""),
                    ("Integrated Master’s in Architectural Engineering", "University of Thessaly · 2020–25", "Top of class")])}
{sec("Recognition", [("Best Computation Prize", "Bartlett Urban Design · 2026", "Nine Acts of Ostranenie"),
                      ("Theory Report Prize", "Bartlett Urban Design · 2026", "The Unseen City"),
                      ("Honorable Mention", "Playing Models 2026, SCI-Arc", ""),
                      ("IKY Award", "Greece", "")])}
{sec("Tools", [("AI and data", "Multi-agent systems, MCP, local open models, Python, CLIP, SOM, UMAP", ""),
                ("3D and design", "Blender, Rhino, Revit, TouchDesigner, Adobe", ""),
                ("Film", "Premiere, DaVinci Resolve", ""),
                ("Languages", "Greek, English", "")])}
</div>
</div>"""
    return page("/about/", "About", "Architectural engineer licensed in Greece, MArch Urban Design from the Bartlett. Experience, teaching, awards and CV.", body, og="/og/about.jpg", nav="about")


def og_images():
    os.makedirs(os.path.join(ROOT, "og"), exist_ok=True)
    def crop(src, dst, focus=.5):
        im = Image.open(os.path.join(ROOT, src.lstrip("/"))).convert("RGB")
        r = 1200 / 630
        w, h = im.size
        if w / h > r:
            nw = int(h * r); x = int((w - nw) * focus); im = im.crop((x, 0, x + nw, h))
        else:
            nh = int(w / r); y = int((h - nh) * focus); im = im.crop((0, y, w, y + nh))
        im.resize((1200, 630), Image.LANCZOS).save(os.path.join(ROOT, "og", dst), "JPEG", quality=84)
    for p in PROJECTS:
        if p["og"]:
            crop(p["og"], p["slug"] + ".jpg")
    crop(f"{M}/nine-acts/lead.webp", "home.jpg")
    crop(f"{M}/about/workshop-poster.webp", "about.jpg", focus=.0)
    # thesis: red card
    from PIL import ImageDraw
    Image.new("RGB", (1200, 630), "#ff3131").save(os.path.join(ROOT, "og", "unseen-city.jpg"), quality=90)


def sitemap():
    urls = ["/", "/about/"] + [f"/{s}/" for s in ORDER] + ["/nightwalk/"]
    x = "".join(f"<url><loc>{SITE}{u}</loc></url>" for u in urls)
    with open(os.path.join(ROOT, "sitemap.xml"), "w") as f:
        f.write(f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{x}</urlset>\n')
    with open(os.path.join(ROOT, "robots.txt"), "w") as f:
        f.write(f"User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n")


if __name__ == "__main__":
    og_images()
    write("/", home())
    write("/about/", about())
    for p in PROJECTS:
        write(f"/{p['slug']}/", project_page(p))
    sitemap()
