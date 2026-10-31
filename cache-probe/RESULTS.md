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
warm always the other. That explains the main run's "identical re-run" flips.
There, the canonical call was cold (about 0.5 s) and the control call warm (about
0.2 s). **So on Ollama the control condition measures cold against cached on
near-ties, not run-to-run noise.** The third item flipped in the main run but
not here. I don't know why, and I'm not guessing.

What a researcher using Ollama can do: unload between calls (`keep_alive: 0`), or
at least record `prompt_eval_duration` alongside `prompt_eval_count`. The count
alone hides reuse.
