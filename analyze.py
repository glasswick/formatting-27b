# Flip rate per condition: share of items whose parsed label differs from the canonical prompt's.
# Label parsing follows the authors' parse_label (src/score.py), rewritten here.
import json, re, sys, math, collections
LABELS = {"sst2": ["positive", "negative"], "boolq": ["yes", "no"]}
AG = {"world": "world", "sports": "sports", "sport": "sports", "business": "business", "sci/tech": "sci/tech",
      "sci-tech": "sci/tech", "science": "sci/tech", "technology": "sci/tech", "tech": "sci/tech"}
def parse(task, text):
    t = re.sub(r"<think>.*?</think>", "", text.strip().lower().replace("’", "'"), flags=re.S).strip()
    cands = AG if task == "agnews" else {l: l for l in LABELS[task]}
    best = None
    for k, v in cands.items():
        m = re.search(r"\b" + re.escape(k) + r"\b", t)
        if m and (best is None or m.start() < best[0]): best = (m.start(), v)
    return best[1] if best else "other"
def wilson(k, n, z=1.96):
    if not n: return (0, 0)
    p = k / n; d = 1 + z*z/n; c = (p + z*z/(2*n)) / d; h = z*math.sqrt(p*(1-p)/n + z*z/(4*n*n)) / d
    return (max(0, c-h), min(1, c+h))
rows = [json.loads(l) for l in open(sys.argv[1])]
lab = {(r["item_id"], r["cond"]): parse(r["task"], r["out"]) for r in rows}
items = sorted({r["item_id"] for r in rows})
conds = ["control", "trailing_space", "crlf", "double_space", "nbsp", "punct_all", "curly_quotes"]
other = sum(1 for v in lab.values() if v == "other")
print(f"items {len(items)}, calls {len(rows)}, unparsed {other}")
fam = collections.Counter(); famn = collections.Counter()
for c in conds:
    pairs = [(lab[(i, "canonical")], lab[(i, c)]) for i in items if (i, "canonical") in lab and (i, c) in lab]
    k = sum(a != b for a, b in pairs); lo, hi = wilson(k, len(pairs))
    print(f"{c:15s} n={len(pairs):5d} flips={k:3d} rate={k/max(1,len(pairs)):.4f} [{lo:.4f}, {hi:.4f}]")
    f = "whitespace" if c in ("trailing_space", "crlf", "double_space", "nbsp") else ("punctuation" if c != "control" else "control")
    fam[f] += k; famn[f] += len(pairs)
for f in ("control", "whitespace", "punctuation"):
    lo, hi = wilson(fam[f], famn[f]); print(f"{f:12s} {fam[f]}/{famn[f]} = {fam[f]/max(1,famn[f]):.4f} [{lo:.4f}, {hi:.4f}]")
