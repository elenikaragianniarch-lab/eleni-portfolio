"""Night Walk data build: OSM + police.uk -> scored street graph (graph.json) for client-side routing."""
import json, math, collections
import numpy as np
from scipy.spatial import cKDTree
from matplotlib.path import Path

osm = json.load(open("data/osm.json"))["elements"]
crime = json.load(open("data/crime.json"))
LAT0, LON0 = 51.5365, -0.134
KX = math.cos(math.radians(LAT0)) * 111320
KY = 110540
def proj(lat, lon): return ((lon - LON0) * KX, (lat - LAT0) * KY)

nodes = {e["id"]: proj(e["lat"], e["lon"]) for e in osm if e["type"] == "node"}
ntags = {e["id"]: e["tags"] for e in osm if e["type"] == "node" and e.get("tags")}
ways = [e for e in osm if e["type"] == "way"]

WALK = {"footway","pedestrian","residential","unclassified","tertiary","secondary","primary","trunk","service",
        "living_street","path","steps","cycleway","primary_link","secondary_link","tertiary_link","trunk_link","track"}
def walkable(t):
    h = t.get("highway")
    if h not in WALK: return False
    if t.get("access") in ("private","no") and t.get("foot") not in ("yes","designated","permissive"): return False
    if t.get("foot") == "no": return False
    if h == "cycleway" and t.get("foot") not in ("yes","designated","permissive"): return False
    if h == "service" and t.get("service") in ("parking_aisle",): return False
    if t.get("indoor") == "yes" or t.get("level","0") not in ("0",""):
        if h not in ("steps",): return False
    return True

streets = [w for w in ways if walkable(w.get("tags", {}))]
parks = [w for w in ways if w.get("tags", {}).get("leisure") == "park"]
park_paths = []
for p in parks:
    pts = [nodes[n] for n in p["nodes"] if n in nodes]
    if len(pts) > 3: park_paths.append(Path(pts))

# ---------- POIs ----------
def pts_where(fn):
    out = []
    for nid, t in ntags.items():
        w = fn(t)
        if w: out.append((*nodes[nid], w))
    return np.array(out) if out else np.zeros((0, 3))

NIGHT = {"pub":1.0,"bar":1.0,"nightclub":1.0,"fast_food":0.9,"restaurant":0.7,"cafe":0.4,"cinema":0.8,"theatre":0.8,"casino":0.8}
def activity_w(t):
    a = t.get("amenity")
    if a in NIGHT: return NIGHT[a]
    if "shop" in t:
        oh = t.get("opening_hours","")
        if "24/7" in oh: return 1.2
        return 0.6 if t["shop"] in ("convenience","supermarket","alcohol","kiosk","newsagent") else 0.3
    if t.get("public_transport") in ("stop_position","platform") or t.get("highway") == "bus_stop": return 0.6
    if t.get("railway") in ("station","subway_entrance","train_station_entrance") or t.get("public_transport") == "station": return 1.2
    return 0
def help_w(t):
    a = t.get("amenity")
    if a in ("police","hospital","pharmacy","clinic","fuel"): return 1
    if "24/7" in t.get("opening_hours",""): return 1
    if t.get("railway") in ("station","subway_entrance","train_station_entrance") or t.get("public_transport") == "station": return 1
    if a in ("pub","bar","nightclub") : return 0.5   # staffed late venues ("Ask for Angela")
    return 0
ACT = pts_where(activity_w); HELP = pts_where(help_w)
CW = {"violent-crime":1.0,"robbery":1.0,"possession-of-weapons":1.0,"theft-from-the-person":0.6,"public-order":0.6,
      "anti-social-behaviour":0.3,"drugs":0.3,"criminal-damage-arson":0.3}
CR = np.array([(*proj(float(c["location"]["latitude"]), float(c["location"]["longitude"])), CW.get(c["category"], 0))
               for c in crime if CW.get(c["category"], 0) > 0])
tA, tH, tC = cKDTree(ACT[:, :2]), cKDTree(HELP[:, :2]), cKDTree(CR[:, :2])

# ---------- split ways at junctions ----------
use = collections.Counter()
for w in streets:
    for i, n in enumerate(w["nodes"]):
        use[n] += 1 if 0 < i < len(w["nodes"]) - 1 else 2
segs = []
for w in streets:
    t = w["tags"]; ns = [n for n in w["nodes"] if n in nodes]
    cur = [ns[0]]
    for n in ns[1:]:
        cur.append(n)
        if use[n] > 1:
            if len(cur) > 1: segs.append((cur, t))
            cur = [n]
    if len(cur) > 1: segs.append((cur, t))

ROAD = {"primary","secondary","tertiary","trunk","residential","unclassified","living_street","primary_link","secondary_link","tertiary_link","trunk_link"}
def light_of(t):
    l = t.get("lit")
    if l in ("yes","24/7","yes;24/7","automatic"): return 1.0, True
    if l == "no": return 0.0, True
    h = t["highway"]
    if h in ROAD: return 0.85, False
    if h in ("pedestrian",): return 0.8, False
    if h == "service": return 0.5, False
    return 0.35, False

def sample(pts, step=12):
    out = []
    for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
        L = math.hypot(x2 - x1, y2 - y1); k = max(1, int(L // step))
        for i in range(k): out.append((x1 + (x2 - x1) * i / k, y1 + (y2 - y1) * i / k))
    out.append(pts[-1]); return np.array(out)

S = []
for ns, t in segs:
    pts = [nodes[n] for n in ns]
    L = sum(math.hypot(b[0]-a[0], b[1]-a[1]) for a, b in zip(pts, pts[1:]))
    if L < 0.5: continue
    sm = sample(pts)
    # activity: weighted POIs within 35 m of the segment
    idx = set(i for lst in tA.query_ball_point(sm, 35) for i in lst)
    act_raw = sum(ACT[i, 2] for i in idx) / max(1, L / 60)
    if t["highway"] in ("primary","trunk","secondary"): act_raw += 0.8
    # help: nearest help point to any sample
    dH = tH.query(sm)[0].min()
    help_ = 1.0 if dH < 50 else max(0.0, 1 - (dH - 50) / 200)
    # incidents within 45 m, per 100 m
    idc = set(i for lst in tC.query_ball_point(sm, 45) for i in lst)
    inc_raw = sum(CR[i, 2] for i in idc) / max(1, L / 100)
    light, tagged = light_of(t)
    mid = sm[len(sm) // 2]
    in_park = any(p.contains_point(mid) for p in park_paths)
    tunnel = t.get("tunnel") in ("yes","building_passage","culvert") or t.get("covered") == "yes"
    steps = t["highway"] == "steps"
    h = t["highway"]
    if tunnel: open_ = 0.1
    elif in_park and h in ("footway","path","cycleway"): open_ = 0.3
    elif h in ("path","track"): open_ = 0.4
    elif h == "service": open_ = 0.6
    elif steps: open_ = 0.55
    elif h == "footway": open_ = 0.8
    else: open_ = 1.0
    if in_park and t.get("lit") != "yes": light = min(light, 0.2)
    S.append(dict(a=ns[0], b=ns[-1], pts=pts, L=L, light=light, lit_tag=tagged, act_raw=act_raw, help=help_,
                  inc_raw=inc_raw, open=open_, steps=steps, tunnel=tunnel, park=in_park,
                  name=t.get("name",""), hw=h))

a = np.array([s["act_raw"] for s in S]); c = np.array([s["inc_raw"] for s in S])
a95, c95 = np.percentile(a, 92), np.percentile(c[c > 0], 85)
for s in S:
    s["act"] = float(min(1, s["act_raw"] / a95))
    s["safe"] = float(1 - min(1, s["inc_raw"] / c95))

# keep the largest connected component
adj = collections.defaultdict(list)
for i, s in enumerate(S): adj[s["a"]].append(i); adj[s["b"]].append(i)
seen, best = set(), []
for start in adj:
    if start in seen: continue
    comp, stack = [], [start]; seen.add(start)
    while stack:
        u = stack.pop(); comp.append(u)
        for i in adj[u]:
            for v in (S[i]["a"], S[i]["b"]):
                if v not in seen: seen.add(v); stack.append(v)
    if len(comp) > len(best): best = comp
keep = set(best)
S = [s for s in S if s["a"] in keep]

vid = {}; V = []
def vix(n):
    if n not in vid: vid[n] = len(V); V.append([round(nodes[n][0], 1), round(nodes[n][1], 1)])
    return vid[n]
out = []
for s in S:
    # simplify drawing points to 1 m
    pts = [[round(x, 1), round(y, 1)] for x, y in s["pts"]]
    out.append([vix(s["a"]), vix(s["b"]), round(s["L"], 1), round(s["light"], 2), round(s["act"], 2), round(s["open"], 2),
                round(s["help"], 2), round(s["safe"], 2), int(s["steps"]), int(s["tunnel"]), s["name"], pts[1:-1]])

# drawing layers
parks_d = [[[round(x,1), round(y,1)] for x, y in [nodes[n] for n in p["nodes"] if n in nodes]] for p in parks]
lit_known = sum(s["L"] for s in S if s["lit_tag"]) / sum(s["L"] for s in S)
def nm(t): return t.get("name","")
act_pts = [[round(nodes[n][0],1), round(nodes[n][1],1), round(activity_w(t),1)] for n, t in ntags.items() if activity_w(t) >= 0.4]
help_pts = [[round(nodes[n][0],1), round(nodes[n][1],1), (t.get("amenity") or ("station" if t.get("railway") or t.get("public_transport")=="station" else "24/7 shop")), nm(t)]
            for n, t in ntags.items() if help_w(t) >= 1]
crime_pts = [[round(x,1), round(y,1), round(w,1)] for x, y, w in CR]
stations = {nm(t): [round(nodes[n][0],1), round(nodes[n][1],1)] for n, t in ntags.items()
            if (t.get("railway") == "station" or t.get("public_transport") == "station") and nm(t)}
G = dict(origin=[LAT0, LON0], kx=KX, ky=KY, V=V, E=out, parks=parks_d, help=help_pts, crime=crime_pts, act=act_pts,
         meta=dict(crime_month=crime[0]["month"], crime_n=len(crime), lit_tagged=round(lit_known, 3), segments=len(out)),
         stations=stations)
json.dump(G, open("graph.json", "w"), separators=(",", ":"), ensure_ascii=False)
print(len(V), "vertices", len(out), "segments", "lit-tag coverage", round(lit_known, 2))
print("stations", list(stations)[:30])
print("help", len(help_pts), "crime pts", len(crime_pts))
import os; print(os.path.getsize("graph.json") // 1024, "KB")
