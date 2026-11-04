"""Night Walk city simulation: thousands of trips, shortest vs agreed safe route, precomputed into city.json."""
import json, random, collections
import numpy as np
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import dijkstra

G = json.load(open("graph.json"))
V, E = G["V"], G["E"]
n = len(V)
K = 3
WALKERS = [dict(w=[.9,.2,.3,.1,.4], tol=.45), dict(w=[.4,.9,.5,.9,.4], tol=1.6),
           dict(w=[.5,.3,.8,.3,.3], tol=1.1, step=True), dict(w=[.9,.9,.9,.6,.9], tol=3.4)]
mean = [sum(w["w"][k] for w in WALKERS) / 4 for k in range(5)]
mx = [max(w["w"][k] for w in WALKERS) for k in range(5)]
BLENDS = [dict(w=mean, tol=2, step=True), dict(w=mx, tol=2.4, step=True), dict(w=mean, tol=1.5, step=True), dict(w=mx, tol=3.2, step=True)]

def ecost(e, p):
    if p.get("step") and e[8]: return np.inf
    pen = sum(p["w"][k] * (1 - e[3 + k]) for k in range(5))
    return e[2] * (1 + K * p["tol"] * pen / 2.5)

def build(costf):
    best = {}
    for i, e in enumerate(E):
        c = costf(e)
        if not np.isfinite(c): continue
        for a, b in ((e[0], e[1]), (e[1], e[0])):
            if (a, b) not in best or c < best[(a, b)][0]: best[(a, b)] = (c, i)
    keys = list(best)
    m = csr_matrix(([best[k][0] for k in keys], ([k[0] for k in keys], [k[1] for k in keys])), shape=(n, n))
    return m, {k: v[1] for k, v in best.items()}

PROFILES = [dict(short=True)] + WALKERS + BLENDS
MATS = [build((lambda e: e[2]) if p.get("short") else (lambda e, p=p: ecost(e, p))) for p in PROFILES]

# step-free connected component (same rule as the app's snapping)
adj = collections.defaultdict(list)
for i, e in enumerate(E):
    if not e[8]: adj[e[0]].append(e[1]); adj[e[1]].append(e[0])
seen, comps = set(), []
for s in adj:
    if s in seen: continue
    st, c = [s], []; seen.add(s)
    while st:
        u = st.pop(); c.append(u)
        for v in adj[u]:
            if v not in seen: seen.add(v); st.append(v)
    comps.append(c)
OK = max(comps, key=len)
deg = collections.Counter()
for e in E: deg[e[0]] += 1; deg[e[1]] += 1
cand = [v for v in OK if deg[v] >= 3]

random.seed(7)
NO, ND = 160, 16
origins = random.sample(cand, NO)
def path(pred, emap, s, t):
    out, u = [], t
    while u != s:
        p = pred[u]
        if p < 0: return None
        out.append(emap[(p, u)]); u = p
    return out[::-1]
def rcost(r, p): return sum(ecost(E[i], p) for i in r) if not p.get("short") else sum(E[i][2] for i in r)

short_use = np.zeros(len(E)); safe_use = np.zeros(len(E)); avoided = np.zeros(len(E))
trips, detours = [], collections.defaultdict(list)
for s in origins:
    res = [dijkstra(m, indices=s, return_predecessors=True) for m, _ in MATS]
    far = [t for t in cand if t != s and 600 < np.hypot(V[t][0] - V[s][0], V[t][1] - V[s][1]) < 2200]
    for t in random.sample(far, min(ND, len(far))):
        rs = [path(res[k][1], MATS[k][1], s, t) for k in range(len(PROFILES))]
        if any(r is None for r in rs[:1]) or rs[3] is None: continue
        own = rs[1:5]; best = [rcost(own[i], WALKERS[i]) for i in range(4)]
        pick, pmax = None, 1e18
        for r in rs[1:]:
            if r is None: continue
            reg = max(rcost(r, WALKERS[i]) / best[i] - 1 for i in range(4))
            if reg < pmax - 1e-9: pmax, pick = reg, r
        sh = rs[0]
        Ls, La = sum(E[i][2] for i in sh), sum(E[i][2] for i in pick)
        lit = lambda r: sum(E[i][2] for i in r if E[i][3] >= .8) / sum(E[i][2] for i in r)
        und = lambda r: sum(1 for j, i in enumerate(r) if E[i][9] and (j == 0 or not E[r[j-1]][9]))
        trips.append((Ls, La, lit(sh), lit(pick), und(sh), und(pick)))
        detours[s].append((La - Ls) / 80)
        ps = set(pick)
        for i in sh:
            short_use[i] += 1
            if i not in ps: avoided[i] += 1
        for i in pick: safe_use[i] += 1

T = np.array(trips)
stats = dict(trips=len(T), extra_min=round(float(np.mean((T[:,1]-T[:,0])/80)), 1), extra_pct=round(float(np.mean(T[:,1]/T[:,0]-1))*100),
             lit_short=round(float(np.mean(T[:,2]))*100), lit_safe=round(float(np.mean(T[:,3]))*100),
             und_short=round(float(np.mean(T[:,4]>0))*100), und_safe=round(float(np.mean(T[:,5]>0))*100),
             same=round(float(np.mean(np.abs(T[:,1]-T[:,0])<1))*100),
             under3=round(float(np.mean((T[:,1]-T[:,0])/80<=3))*100))
# streets to fix: group avoided segments by street name (or a nearby label), weighted by how often the shortest route used them
groups = collections.defaultdict(lambda: dict(trips=0, L=0, ids=[], why=collections.Counter()))
for i, e in enumerate(E):
    if avoided[i] < 3: continue
    name = e[10] or ("Unnamed path" if e[8] == 0 else "Unnamed steps")
    g = groups[name]; g["trips"] = max(g["trips"], int(avoided[i])); g["L"] += e[2]; g["ids"].append(i)
    if e[3] < .5: g["why"]["unlit"] += e[2]
    if e[4] < .3: g["why"]["few people around"] += e[2]
    if e[5] < .5: g["why"]["underpass or hidden path" if e[9] else "hidden path"] += e[2]
    if e[7] < .5: g["why"]["many recorded incidents"] += e[2]
    if e[8]: g["why"]["steps"] += e[2]
fix = sorted(groups.items(), key=lambda kv: -kv[1]["trips"])
fix = [dict(name=k, trips=v["trips"], pct=round(100 * v["trips"] / len(T), 1), why=[w for w, _ in v["why"].most_common(2)], ids=v["ids"]) for k, v in fix if not k.startswith("Unnamed")][:10]
city = dict(stats=stats,
            safe=[round(float(x / max(1, safe_use.max())), 3) for x in safe_use],
            short=[round(float(x / max(1, short_use.max())), 3) for x in short_use],
            avoid=[round(float(x / max(1, avoided.max())), 3) for x in avoided],
            detour=[[V[s][0], V[s][1], round(float(np.mean(d)), 1)] for s, d in detours.items() if d],
            fix=fix)
json.dump(city, open("city.json", "w"), separators=(",", ":"))
print(stats)
for f in fix: print(f["name"], f["trips"], f["pct"], f["why"], len(f["ids"]))
import os; print(os.path.getsize("city.json") // 1024, "KB")
