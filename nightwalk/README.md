# Night Walk

Four walkers with different needs negotiate one safer route home at night, King's Cross to Camden. A design prototype by Eleni Karagianni, 2026. Not safety advice.

- `build.py` turns OpenStreetMap (Overpass export) and police.uk street-crime data into `graph.json`: 8,165 street segments, each scored 0–1 on lighting, people around, sightlines, help nearby and recorded incidents.
- `index.html` runs everything in the browser: Dijkstra routing per walker, minimax-regret negotiation between candidate routes, and a scorecard against the shortest route.

Data © OpenStreetMap contributors (ODbL); police.uk data under the Open Government Licence v3.0.
