# What Ollama runs for a repeated prompt: results (2026-10-31)

`probe.jsonl`: 23 prompts × 11 calls (qwen3.8:27b, Ollama 0.40.13, greedy, seed 0).
Thresholds from PLAN.md, fixed before any call.

**Threshold 1 (a cached re-run): not met, and the instrument was wrong.**
`prompt_eval_count` was the same on every repeat, 0 of 20 below half. But the
timings show reuse plainly. `prompt_eval_duration` has a median of 332 ms on cold
calls (the model unloaded before each) against 67 ms on warm repeats, and many warm
calls show 0 ms. So Ollama reports the full prompt length even when it reuses the
cached prompt. I fixed the wrong field in advance. I report the miss as it is,
not re-scored.

**Thresholds 2 and 3, on the 20 random prompts: none.** Cold calls agreed
with each other on 20 of 20, and warm calls agreed with cold ones on 20 of 20 (220
calls). Threshold 4 applies: no difference seen in 20, so the 95% upper bound is
about 14%. That's loose, and it does not show the floor is zero.

**The 3 items the identical re-run flipped in the main run** (an extra set,
reported apart, as PLAN.md says):

| item | cold calls (3 of 3, and the first identical call) | every warm call after it (7 of 7) |
|---|---|---|
| boolq/2049 | yes | no |
| boolq/3148 | no | yes |
| boolq/2578 | yes | yes (no flip this time) |

On 2 of the 3, the answer depends on whether the prompt was computed fresh or
reused from cache, every time. It's not random: cold always gives one answer,
warm always the other. So on Ollama the control condition compares a fresh
prompt with a cached one on near-ties, and isn't a measure of run-to-run noise.

*Corrected 2026-10-31, 21:16 UTC.* I first wrote here that this "explains the
main run's flips". It explains one of them. In the main run the canonical call
spent fresh-prompt time (0.45 to 0.57 s) and the control call cached time (0.2
to 0.32 s). On boolq/2049 the answers match the probe: fresh "yes", cached "no".
On boolq/3148 they're the other way round: the main run gave "yes" fresh and
"no" cached, and the probe gives "no" fresh and "yes" cached, 4 of 4 and 7 of 7.
So cache state flips 3148 in both runs, but which answer goes with which state
changed between them. I don't know what else differed (the probe reloaded the
model before each fresh call, and the main run didn't). The third item, 2578,
flipped in the main run but not here, and I don't know why. Found while making
amigalberry's per-item field table (research/neartie-fields).

What a researcher using Ollama can do: unload between calls (`keep_alive: 0`), or
at least record `prompt_eval_duration` alongside `prompt_eval_count`. The count
alone hides reuse.
