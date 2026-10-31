# What Ollama runs for a repeated prompt

*Written 2026-10-31 ~02:20 UTC, before any probe call. The thresholds
below are fixed now; if I change one after seeing data, I say so here
with the reason.*

## The question
In my formatting run (meta_mapper's "Invisible Formatting Effects",
extended to qwen3.8:27b, NVFP4, Ollama 0.40.13), the "control" condition
re-sends the canonical prompt byte for byte. The authors use it as a
noise floor. In my run it took 0.26 s against 2.25 s for the first call,
which suggests Ollama reused cached work. If so, my control row may
measure "cached vs fresh", not run-to-run noise.

## The probe (runs only after the main run ends; same server)
- 20 classification prompts from their data/prompts.jsonl (canonical
  only; fixed seed 0 for the draw), same settings as the run: chat,
  think false, temperature 0, seed 0, num_predict 12.
- **identical:** each prompt 5 times back to back.
- **interleaved:** each prompt 3 times, with a different prompt between.
- **unloaded:** each prompt 3 times with the model unloaded between calls
  (`keep_alive: 0`), so each call starts cold.
- Log per call: answer text, `prompt_eval_count`, `eval_count`, durations.

## Thresholds (fixed before running)
1. **Not a fresh re-run:** if on identical repeats `prompt_eval_count` is
   below half of the first call's in at least 18 of 20 prompts, the
   control row re-uses cached work. I stop calling it a noise floor and
   call it a "cached re-run".
2. **Real nondeterminism:** if any prompt's answer differs across its
   3 unloaded calls, there is noise even cold; I report how many of 20.
3. **The cache changes answers:** if unloaded calls agree but a cached
   repeat (identical or interleaved) differs from them on any prompt,
   the cache itself moves outputs; I report how many of 20.
4. If none of 2 and 3 happen, I can say only: in 20 prompts, no
   difference seen, which bounds the noise loosely (0 of 20: the 95%
   upper bound is about 14%). It does not show the floor is zero.

## Added before running (2026-10-31 ~08:00 UTC)
The 3 items the identical re-run flipped in the main run (boolq/2049,
boolq/2578, boolq/3148) get the same 11 calls as an extra set, reported
apart. They don't count toward thresholds 1 to 4, which stay on the 20
random prompts. Why: 20 random prompts will almost surely miss the
cases the question is about.
