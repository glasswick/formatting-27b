# The Ollama cache probe (cache-probe/PLAN.md). Fixed count: 20 prompts (+ named extras) x 11 calls.
import json, random, sys, time, urllib.request
PROMPTS, OUT, MODEL = sys.argv[1], sys.argv[2], sys.argv[3]
rows = [json.loads(l) for l in open(PROMPTS)]
canon = [r for r in rows if r["kind"] == "cls" and r["cond"] == "canonical"]
rng = random.Random(0); rng.shuffle(canon); picks = canon[:20]; spacer = canon[20]
EXTRA = sys.argv[4].split(",") if len(sys.argv) > 4 else []  # reported apart (PLAN.md, "Added before running")
extra = [r for r in canon if r["item_id"] in EXTRA]
def call(prompt, keep_alive=None):
    body = {"model": MODEL, "messages": [{"role": "user", "content": prompt}], "think": False, "stream": False,
            "options": {"temperature": 0, "seed": 0, "num_predict": 12}}
    if keep_alive is not None: body["keep_alive"] = keep_alive
    t0 = time.time()
    req = urllib.request.Request("http://127.0.0.1:11434/api/chat", json.dumps(body).encode(), {"Content-Type": "application/json"})
    j = json.load(urllib.request.urlopen(req, timeout=600))
    return {"out": j["message"]["content"], "prompt_eval_count": j.get("prompt_eval_count"), "eval_count": j.get("eval_count"),
            "load_ms": round(j.get("load_duration", 0) / 1e6), "prompt_ms": round(j.get("prompt_eval_duration", 0) / 1e6), "s": round(time.time() - t0, 2)}
with open(OUT, "w") as f:
    def log(p, cond, k, r): f.write(json.dumps({"pid": p["pid"], "set": "extra" if p in extra else "random", "cond": cond, "k": k, **r}) + "\n"); f.flush()
    for p in picks + extra:
        call(spacer["prompt"], keep_alive=0)  # unload first, so unloaded k=0 starts cold too
        for k in range(3): log(p, "unloaded", k, call(p["prompt"], keep_alive=0))
        for k in range(5): log(p, "identical", k, call(p["prompt"]))
        for k in range(3):
            call(spacer["prompt"]); log(p, "interleaved", k, call(p["prompt"]))
print("done", file=sys.stderr)
