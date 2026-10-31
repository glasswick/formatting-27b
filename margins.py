# Part 2 of research/formatting-27b/PLAN.md: each item's canonical-prompt label margin, from top-20 first-token logprobs.
import json, math, sys, time, urllib.request
PROMPTS, OUT, MODEL = sys.argv[1], sys.argv[2], sys.argv[3]
items = {json.loads(l)["item_id"] for l in open(sys.argv[4])}
rows = [json.loads(l) for l in open(PROMPTS)]
canon = [r for r in rows if r["kind"] == "cls" and r["cond"] == "canonical" and r["item_id"] in items]
LAB = {"sst2": {"positive": ["positive", "pos"], "negative": ["negative", "neg"]},
       "boolq": {"yes": ["yes"], "no": ["no"]},
       "agnews": {"world": ["world"], "sports": ["sport"], "business": ["business", "bus"], "sci/tech": ["sci", "tech", "science"]}}
def label_of(task, tok):
    t = tok.strip().lower()
    if not t: return None
    for lab, starts in LAB[task].items():
        if any(t.startswith(s) or (len(t) >= 2 and s.startswith(t)) for s in starts): return lab
    return None
with open(OUT, "w") as f:
    for r in canon:
        body = {"model": MODEL, "messages": [{"role": "user", "content": r["prompt"]}], "think": False, "stream": False,
                "logprobs": True, "top_logprobs": 20, "options": {"temperature": 0, "seed": 0, "num_predict": 1}}
        req = urllib.request.Request("http://127.0.0.1:11434/api/chat", json.dumps(body).encode(), {"Content-Type": "application/json"})
        top = json.load(urllib.request.urlopen(req, timeout=300))["logprobs"][0]["top_logprobs"]
        p = {}
        for x in top:
            lab = label_of(r["task"], x["token"])
            if lab: p[lab] = p.get(lab, 0) + math.exp(x["logprob"])
        ranked = sorted(p.items(), key=lambda kv: -kv[1])
        floor = math.exp(min(x["logprob"] for x in top))
        if len(ranked) >= 2: m, exact = math.log(ranked[0][1]) - math.log(ranked[1][1]), True
        elif ranked: m, exact = math.log(ranked[0][1]) - math.log(floor), False
        else: m, exact = None, False
        f.write(json.dumps({"item_id": r["item_id"], "task": r["task"], "top": ranked[:2], "margin": m, "exact": exact}) + "\n"); f.flush()
