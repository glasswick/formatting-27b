# Part 2 of PLAN.md: are flipped items exactly the near-ties? Thresholds fixed in PLAN.md before any margin was fetched.
# Usage: python3 -I part2.py runs-qwen3.8-27b.jsonl margins-canonical.jsonl
import json, re, statistics, sys
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
PERT = ["trailing_space", "crlf", "double_space", "nbsp", "punct_all", "curly_quotes"]
rows = [json.loads(l) for l in open(sys.argv[1])]
lab = {(r["item_id"], r["cond"]): parse(r["task"], r["out"]) for r in rows}
mar = {m["item_id"]: m for m in map(json.loads, open(sys.argv[2]))}
flipped = {i for i in mar if any(lab[(i, c)] != lab[(i, "canonical")] for c in PERT)}
agree = sum(1 for i, m in mar.items() if m["top"] and m["top"][0][0] == lab[(i, "canonical")])
print(f"items {len(mar)}; logprob top label agrees with the run's canonical answer on {agree}")
def share(ids, f): return sum(1 for i in ids if f(mar[i]["margin"])) / len(ids)
for name, ids in [("flipped", flipped), ("unflipped", set(mar) - flipped)]:
    ms = [mar[i]["margin"] for i in ids]
    print(f"{name:9} n={len(ids):4}  <1 nat {share(ids, lambda x: x < 1):6.1%}  >2 nats {share(ids, lambda x: x > 2):6.1%}  median {statistics.median(ms):.2f}")
lt1 = [i for i in mar if mar[i]["margin"] < 1]
print(f"of items under 1 nat ({len(lt1)}), flipped: {sum(i in flipped for i in lt1)} ({sum(i in flipped for i in lt1)/len(lt1):.0%})")
for lo, hi in [(0, .5), (.5, 1), (1, 2), (2, 4), (4, 99)]:
    b = [i for i in mar if lo <= mar[i]["margin"] < hi]
    print(f"margin [{lo},{hi}): n={len(b):4}  flipped {sum(i in flipped for i in b):3}  ({sum(i in flipped for i in b)/max(1,len(b)):.0%})")
print("flipped items above 2 nats:")
for i in sorted(flipped, key=lambda i: -mar[i]["margin"]):
    if mar[i]["margin"] > 2:
        print(f"  {i:12} margin {mar[i]['margin']:.2f} exact={mar[i]['exact']} canon={lab[(i,'canonical')]} flips=" +
              ",".join(f"{c}:{lab[(i,c)]}" for c in PERT if lab[(i, c)] != lab[(i, 'canonical')]))
