# Side by side: the authors' published per-model flip rates (results/tables/rate_cls_flip.csv)
# and mine, for the 7 conditions both runs share.
import csv, sys, subprocess, statistics
theirs_csv, mine_out = sys.argv[1], sys.argv[2]
conds = ["control", "trailing_space", "crlf", "double_space", "nbsp", "punct_all", "curly_quotes"]
t = {}
for r in csv.DictReader(open(theirs_csv)):
    if r["cond"] in conds and not r["model"].startswith("rerun"): t.setdefault(r["cond"], {})[r["model"]] = float(r["rate"])
mine = {}
import re
for line in open(mine_out):
    m = re.match(r"(\w+)\s+n=.*rate=([\d.]+) (\[.*\])", line)
    if m and m[1] in conds: mine[m[1]] = (m[2], m[3])
print("| condition | their 11 models: min / median / max | Qwen2.5-14B (AWQ 4-bit) | Qwen3-8B (bf16) | qwen3.8:27b (NVFP4, Ollama), mine [95% CI] |")
print("| --- | --- | --- | --- | --- |")
for c in conds:
    v = sorted(t[c].values())
    print(f"| {c} | {v[0]:.3f} / {statistics.median(v):.3f} / {v[-1]:.3f} | {t[c]['qwen2.5-14b']:.3f} | {t[c]['qwen3-8b']:.3f} | {float(mine[c][0]):.3f} {mine[c][1]} |")
