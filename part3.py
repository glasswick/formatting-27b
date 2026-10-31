# Part 3 of PLAN.md: does the no-break space move confidence everywhere, or only on the items that flip?
# Signed margin = log p(canonical label) - log p(best other label); a label missing from the top 20 gets the 20th token's probability (a bound).
# Usage: python3 -I part3.py runs-qwen3.8-27b.jsonl margins-canonical.jsonl margins-<cond>.jsonl [cond, default nbsp]
import json, math, re, statistics, sys
LABELS = {"sst2": ["positive", "negative"], "boolq": ["yes", "no"]}
AG = {"world": "world", "sports": "sports", "sport": "sports", "business": "business", "sci/tech": "sci/tech",
      "sci-tech": "sci/tech", "science": "sci/tech", "technology": "sci/tech", "tech": "sci/tech"}
def parse(task, text):  # same as analyze.py
    t = re.sub(r"<think>.*?</think>", "", text.strip().lower().replace("’", "'"), flags=re.S).strip()
    cands = AG if task == "agnews" else {l: l for l in LABELS[task]}
    best = None
    for k, v in cands.items():
        m = re.search(r"\b" + re.escape(k) + r"\b", t)
        if m and (best is None or m.start() < best[0]): best = (m.start(), v)
    return best[1] if best else "other"
rows = [json.loads(l) for l in open(sys.argv[1])]
lab = {(r["item_id"], r["cond"]): parse(r["task"], r["out"]) for r in rows}
can = {m["item_id"]: m for m in map(json.loads, open(sys.argv[2]))}
COND = sys.argv[4] if len(sys.argv) > 4 else "nbsp"
nb = {m["item_id"]: m for m in map(json.loads, open(sys.argv[3]))}
ALL = {"sst2": ["positive", "negative"], "boolq": ["yes", "no"], "agnews": ["world", "sports", "business", "sci/tech"]}
shift, flipped = {}, set()
for i, c in can.items():
    n = nb[i]; L = c["top"][0][0]
    lp = lambda l: math.log(n["probs"].get(l, n["floor"]))
    s_nb = lp(L) - max(lp(o) for o in ALL[c["task"]] if o != L)
    shift[i] = (c["margin"], s_nb - c["margin"])
    if lab[(i, COND)] != lab[(i, "canonical")]: flipped.add(i)
un = set(can) - flipped
for name, ids in [("flipped", flipped), ("unflipped", un)]:
    sh = [shift[i][1] for i in ids]
    print(f"{name:9} n={len(ids):4}  median shift {statistics.median(sh):+.3f}  median |shift| {statistics.median(map(abs, sh)):.3f}  "
          f"share moved toward other label {sum(x < 0 for x in sh)/len(sh):.0%}")
exact = [i for i in un if can[i]["exact"] and nb[i]["top"] and len(nb[i]["probs"]) >= 2]
print(f"unflipped with both labels in top 20 both times (n={len(exact)}): median |shift| {statistics.median(abs(shift[i][1]) for i in exact):.3f}")
for t in ALL:
    ids = [i for i in un if can[i]["task"] == t]
    print(f"  unflipped {t:7} n={len(ids):4} median shift {statistics.median(shift[i][1] for i in ids):+.3f}  median |shift| {statistics.median(abs(shift[i][1]) for i in ids):.3f}")
lo = [i for i in un if can[i]["margin"] < 2]
print(f"unflipped with canonical margin < 2 nats (n={len(lo)}): median shift {statistics.median(shift[i][1] for i in lo):+.3f}, median |shift| {statistics.median(abs(shift[i][1]) for i in lo):.3f}")
print("matched counterexamples (nearest-margin unflipped item, same task):")
big = 0
for i in sorted(flipped, key=lambda i: can[i]["margin"]):
    j = min((j for j in un if can[j]["task"] == can[i]["task"]), key=lambda j: abs(can[j]["margin"] - can[i]["margin"]))
    d = shift[i][1] - shift[j][1]; big += abs(d) > 1 or (shift[i][1] < 0) != (shift[j][1] < 0)
    print(f"  {i:12} m={can[i]['margin']:.2f} shift {shift[i][1]:+.2f}   {j:12} m={can[j]['margin']:.2f} shift {shift[j][1]:+.2f}   diff {d:+.2f}")
print(f"pairs differing in sign or by > 1 nat: {big} of {len(flipped)}")
