"""Night Walk: test design fixes. Re-runs the 2,560 simulated walks with each street improved, and measures what changes."""
import json, random, collections, copy
import numpy as np
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import dijkstra

G = json.load(open("graph.json")); CITY = json.load(open("city.json"))
V, E0 = G["V"], G["E"]; n = len(V); K = 3
WALKERS = [dict(w=[.9,.2,.3,.1,.4], tol=.45), dict(w=[.4,.9,.5,.9,.4], tol=1.6),
           dict(w=[.5,.3,.8,.3,.3], tol=1.1, step=True), dict(w=[.9,.9,.9,.6,.9], tol=3.4)]
mean = [sum(w["w"][k] for w in WALKERS) / 4 for k in range(5)]; mx = [max(w["w"][k] for w in WALKERS) for k in range(5)]
BLENDS = [dict(w=mean, tol=2, step=True), dict(w=mx, tol=2.4, step=True), dict(w=mean, tol=1.5, step=True), dict(w=mx, tol=3.2, step=True)]
PROFILES = [dict(short=True)] + WALKERS + BLENDS

def ecost(e, p):
    if p.get("step") and e[8]: return np.inf
    return e[2] * (1 + K * p["tol"] * sum(p["w"][k] * (1 - e[3 + k]) for k in range(5)) / 2.5)

def mats(E):
    out = []
    for p in PROFILES:
        best = {}
        for i, e in enumerate(E):
            c = e[2] if p.get("short") else ecost(e, p)
            if not np.isfinite(c): continue
            for a, b in ((e[0], e[1]), (e[1], e[0])):
                if (a, b) not in best or c < best[(a, b)][0]: best[(a, b)] = (c, i)
        ks = list(best)
        out.append((csr_matrix(([best[k][0] for k in ks], ([k[0] for k in ks], [k[1] for k in ks])), shape=(n, n)), {k: v[1] for k, v in best.items()}))
    return out

# same trips as sim.py
adj = collections.defaultdict(list)
for e in E0:
    if not e[8]: adj[e[0]].append(e[1]); adj[e[1]].append(e[0])
seen, comps = set(), []
for s0 in adj:
    if s0 in seen: continue
    st, c = [s0], []; seen.add(s0)
    while st:
        u = st.pop(); c.append(u)
        for v in adj[u]:
            if v not in seen: seen.add(v); st.append(v)
    comps.append(c)
OK = max(comps, key=len); deg = collections.Counter()
for e in E0: deg[e[0]] += 1; deg[e[1]] += 1
cand = [v for v in OK if deg[v] >= 3]
random.seed(7); origins = random.sample(cand, 160)
PAIRS = []
for s in origins:
    far = [t for t in cand if t != s and 600 < np.hypot(V[t][0] - V[s][0], V[t][1] - V[s][1]) < 2200]
    PAIRS.append((s, random.sample(far, min(16, len(far)))))

def path(pred, emap, s, t):
    out, u = [], t
    while u != s:
        p = pred[u]
        if p < 0: return None
        out.append(emap[(p, u)]); u = p
    return out[::-1]

def run(E):
    M = mats(E); rc = lambda r, p: sum(ecost(E[i], p) for i in r)
    rows = []
    for s, ts in PAIRS:
        res = [dijkstra(m, indices=s, return_predecessors=True) for m, _ in M]
        for t in ts:
            rs = [path(res[k][1], M[k][1], s, t) for k in range(len(PROFILES))]
            if rs[0] is None or rs[3] is None: continue
            best = [rc(rs[1 + i], WALKERS[i]) for i in range(4)]
            pick, pm = None, 1e18
            for r in rs[1:]:
                if r is None: continue
                g = max(rc(r, WALKERS[i]) / best[i] - 1 for i in range(4))
                if g < pm - 1e-9: pm, pick = g, r
            sh = rs[0]; Ls = sum(E[i][2] for i in sh); La = sum(E[i][2] for i in pick)
            sc = sum(E[i][2] * sum(E[i][3:8]) / 5 for i in sh) / Ls
            lit = sum(E[i][2] for i in sh if E[i][3] >= .8) / Ls
            rows.append(((La - Ls) / 80, sc, lit))
    A = np.array(rows)
    return dict(trips=len(A), detour=float(A[:, 0].mean()), detour_sum=float(A[:, 0].sum()), quick_safe=float((A[:, 0] < 1).mean()),
                short_score=float(A[:, 1].mean()), short_lit=float(A[:, 2].mean()))

# ---------- candidate streets and their fixes ----------
avoid = np.array(CITY["avoid"])
groups = collections.defaultdict(list)
for i, e in enumerate(E0):
    if e[10] and avoid[i] > 0.02: groups[e[10]].append(i)
names = [f["name"] for f in CITY["fix"]][:8]

def diagnose(ids):
    d = dict(unlit=0, tun=0, quiet=0, hidden=0, steps=0, inc=0, L=0)
    prevT = 0
    for i in ids:
        e = E0[i]; d["L"] += e[2]
        if e[3] < .5: d["unlit"] += e[2]
        if e[9] and not prevT: d["tun"] += 1
        prevT = e[9]
        if e[4] < .3: d["quiet"] += e[2]
        if e[5] < .5 and not e[9]: d["hidden"] += e[2]
        if e[8]: d["steps"] += 1
        d["inc"] += e[2] * (1 - e[7])
    d["inc"] /= max(1, d["L"]); return {k: round(v, 2) for k, v in d.items()}

def apply(E, ids):
    E = copy.deepcopy(E)
    for i in ids:
        e = E[i]
        if e[3] < .8: e[3] = 1.0
        if e[9]: e[3] = 1.0; e[5] = max(e[5], .8)
        if e[4] < .3: e[4] = .6; e[6] = max(e[6], .8)
        if e[5] < .5 and not e[9]: e[5] = .85
        if e[7] < .5: e[6] = max(e[6], .9)
    return E

def moves(name, d):
    canal = "canal" in name.lower() or "towpath" in name.lower()
    m = []
    if d["unlit"] >= 30: m.append(["Light", "Bat-friendly amber lighting at low level along the water" if canal else "Warm, even lighting at face height, and lit façades"])
    if d["tun"]: m.append(["Underpass", "Light and paint the underpass, mirrors at both ends, open views through"])
    if d["quiet"] >= 60: m.append(["Activate", "Late uses at ground level: kiosks, night market, a staffed help point"])
    if d["hidden"] >= 40: m.append(["Sightlines", "Trim planting, remove blind corners, add a second way in and out"])
    if d["inc"] > .5: m.append(["Help", "Help point and a partnership with late venues"])
    if d["steps"]: m.append(["Step-free", "Ramp or lift beside the steps"])
    cost = "£££" if (canal and d["unlit"] > 300) or d["steps"] else "££" if (d["unlit"] >= 30 or d["tun"]) else "£"
    if canal: partners = ["Canal & River Trust", "Camden Council"]
    elif d["tun"]: partners = ["Camden Council", "Network Rail"]
    elif name in ("York Way",): partners = ["Camden Council", "Islington Council"]
    elif name in ("Goods Way", "Canal Reach"): partners = ["King's Cross estate", "Camden Council"]
    else: partners = ["Camden Council"]
    kind = "towpath" if canal else "underpass" if d["tun"] else "street"
    return m, cost, partners, kind

def base_trips(E):
    """shortest routes do not change when a street is improved, so compute them once, with each trip's safe-route detour"""
    M = mats(E); rc = lambda r, p: sum(ecost(E[i], p) for i in r); T = []
    for s, ts in PAIRS:
        res = [dijkstra(m, indices=s, return_predecessors=True) for m, _ in M]
        for t in ts:
            rs = [path(res[k][1], M[k][1], s, t) for k in range(len(PROFILES))]
            if rs[0] is None or rs[3] is None: continue
            best = [rc(rs[1 + i], WALKERS[i]) for i in range(4)]; pick, pm = None, 1e18
            for r in rs[1:]:
                if r is None: continue
                g = max(rc(r, WALKERS[i]) / best[i] - 1 for i in range(4))
                if g < pm - 1e-9: pm, pick = g, r
            T.append((rs[0], (sum(E[i][2] for i in pick) - sum(E[i][2] for i in rs[0])) / 80))
    return T

def ok(E, sh):
    L = sum(E[i][2] for i in sh); lit = sum(E[i][2] for i in sh if E[i][3] >= .8) / L
    dark_tun = any(E[i][9] and E[i][3] < .8 for i in sh); hidden = sum(E[i][2] for i in sh if E[i][5] < .5) / L
    return lit >= .9 and not dark_tun and hidden < .1, lit

def evaluate(E, T):
    r = [ok(E, sh) for sh, _ in T]
    good = [g for g, _ in r]
    return dict(trips=len(T), quick_safe=sum(good) / len(T), lit=sum(l for _, l in r) / len(T), good=good)

if __name__ == "__main__":
    import time; t0 = time.time()
    T = base_trips(E0); base = evaluate(E0, T); bg = base.pop("good")
    print("base", base, round(time.time() - t0))
    use = collections.Counter(i for sh, _ in T for i in set(sh))
    out = []
    for nm in names:
        ids = groups.get(nm, [])
        if not ids: continue
        d = diagnose(ids); r = evaluate(apply(E0, ids), T); g = r.pop("good"); m, cost, partners, kind = moves(nm, d)
        flipped = [k for k in range(len(T)) if g[k] and not bg[k]]
        r.update(flipped=len(flipped), minutes_saved=round(sum(T[k][1] for k in flipped), 1), uses=sum(1 for sh, _ in T if any(i in set(ids) for i in sh)))
        out.append(dict(name=nm, ids=ids, problems=d, moves=m, cost=cost, partners=partners, kind=kind, after=r))
        print(nm, r["flipped"], r["minutes_saved"], r["uses"], round(r["lit"] - base["lit"], 3))
    out.sort(key=lambda f: -f["after"]["flipped"])
    def combo(fs):
        ids = [i for f in fs for i in f["ids"]]; r = evaluate(apply(E0, ids), T); g = r.pop("good")
        fl = [k for k in range(len(T)) if g[k] and not bg[k]]; r.update(flipped=len(fl), minutes_saved=round(sum(T[k][1] for k in fl), 1)); return r
    both = combo(out[:3]); every = combo(out)
    json.dump(dict(base=base, fixes=out, top3=both, all=every), open("fixes.json", "w"), separators=(",", ":"))
    print("top3", both, "\nall", every, round(time.time() - t0))
