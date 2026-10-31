# My own runner (not the authors' code): their prompts as data, sent to a local Ollama model,
# greedy, thinking off, 12 tokens, as their gen_server.py does. Resumable; a fixed set of calls.
import json, sys, time, urllib.request, random, os
PROMPTS, OUT, MODEL = sys.argv[1], sys.argv[2], sys.argv[3]
PER_TASK = int(sys.argv[4]); LIMIT = int(sys.argv[5]) if len(sys.argv) > 5 else 10**9
CONDS = ["canonical", "control", "double_space", "nbsp", "trailing_space", "crlf", "punct_all", "curly_quotes"]
rows = [json.loads(l) for l in open(PROMPTS)]
rows = [r for r in rows if r["kind"] == "cls" and r["cond"] in CONDS]
items = {}
for r in rows: items.setdefault(r["task"], []).append(r["item_id"])
keep = set()
rng = random.Random(0)
for t, ids in items.items():
    ids = sorted(set(ids)); rng.shuffle(ids); keep |= set(ids[:PER_TASK])
todo = [r for r in rows if r["item_id"] in keep]
done = set()
if os.path.exists(OUT):
    for l in open(OUT): done.add(json.loads(l)["pid"])
n = 0
with open(OUT, "a") as f:
    for r in todo:
        if r["pid"] in done: continue
        if n >= LIMIT: break
        body = json.dumps({"model": MODEL, "messages": [{"role": "user", "content": r["prompt"]}], "think": False,
                           "stream": False, "options": {"temperature": 0, "seed": 0, "num_predict": 12}}).encode()
        t0 = time.time()
        req = urllib.request.Request("http://127.0.0.1:11434/api/chat", body, {"Content-Type": "application/json"})
        out = json.load(urllib.request.urlopen(req, timeout=300))["message"]["content"]
        f.write(json.dumps({"pid": r["pid"], "item_id": r["item_id"], "task": r["task"], "cond": r["cond"], "out": out, "s": round(time.time() - t0, 2)}) + "\n"); f.flush()
        n += 1
print("wrote", n, "of", len(todo), "todo", file=sys.stderr)
