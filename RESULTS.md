# Results so far (2026-10-31 ~03:25 UTC)

Part 1 done: `analysis.txt` (mine) and `comparison.md` (side by side).
Not yet looked at: paired examples, margins (parts 2-3), the cache probe.

What the table shows, read plainly:
- **Whitespace flips fewer labels at 27B than in any of their 11
  models:** trailing space, CRLF, double space and NBSP are all below
  their minimum (e.g. NBSP 2.4% [1.7, 3.5] against their 4.8% to 39%).
  That fits their size trend continuing past 14.8B, but it's one model,
  and the runtime and quantization differ too, so I can't say which.
- **Punctuation is about where their larger models are** (0.7% to 0.9%).
- **Whitespace still beats punctuation** (1.3% [1.0, 1.7] against 0.8%
  [0.5, 1.2]), but the intervals touch; the gap is much smaller.
- **The identical re-run flipped 3 of 1,200 (0.25%)**, above their zero
  for most models, so the noise floor here isn't zero even though Ollama
  seems to reuse cached work for it. The cache probe has to explain that.
- For the decision (PLAN.md): at this size, label moves from one of these
  changes are about 0.3% to 2.4%, so an old-vs-new score difference under
  about 2 points could be formatting; net accuracy not computed yet.

## Net accuracy and flip direction (~03:45 UTC)
Canonical accuracy 90.9%. Every change moves net accuracy by at most half
a point (-0.50 double space to +0.42 NBSP and curly quotes), while
moving up to 2.4% of labels. Flips go both ways (NBSP: 11 right to wrong,
16 wrong to right). Same pattern as theirs: formatting adds variance, not
bias. **For the decision:** on this model, an old-vs-new accuracy gap
under about half a point is inside what formatting alone did here; a
gap over 2 points isn't explained by these changes.

## What ten NBSP pairs show that the table hides
- **Flips sit on items with two defensible answers.** AG News flips are
  tech-company business stories (PeopleSoft, Cisco, Half.com: Business
  vs Sci/Tech) and Howard Stern vs the FCC (Business, World or
  Sci/Tech). Several gold labels are themselves arguable. A "flip" here
  is the model moving between two readings, not breaking.
- **BoolQ carries half the flips** (14 of 29 NBSP, 10 of 22 double space,
  all 3 control) though it's a third of the items.
- **The 3 identical-prompt flips are all BoolQ, and each answer differs
  in its first token's form:** "yes" vs " no", with a leading space.
  The model emits two spellings of its answer, and the near-tie between
  "no" and " no" vs "yes" is where the identical re-run moved. Question
  this suggests, which part 2 can answer: are flipped items the ones
  whose top two labels are nearly tied?

## Part 2: are flipped items the near-ties? (~05:00 UTC)
`part2.py` on `margins-canonical.jsonl` (1,200 items, the canonical
prompt once more with top-20 first-token logprobs); output in part2.txt.
The logprob top label matches the run's canonical answer on 1,194 of
1,200.

| | n | margin < 1 nat | margin > 2 nats | median |
|---|---|---|---|---|
| flipped by any of 6 changes | 44 | 84.1% | 4.5% | 0.37 |
| never flipped | 1,156 | 3.3% | 91.0% | 6.41 |

| canonical margin (nats) | items | flipped |
|---|---|---|
| under 0.5 | 38 | 27 (71%) |
| 0.5 to 1 | 37 | 10 (27%) |
| 1 to 2 | 71 | 5 (7%) |
| 2 to 4 | 167 | 2 (1%) |
| 4 or more | 887 | 0 |

**Against the thresholds fixed in PLAN.md:** neither is met. "Only when
small" needed 90% of flipped items under 1 nat: it's 84%. Refuting it
needed more than 20% above 2 nats: it's 4.5% (2 items). So: **mostly
small, not only.** The useful form for a researcher: no item with a
margin of 4 nats or more flipped (0 of 887), and items under 0.5 nat
flipped 71% of the time. The canonical margin is close to a flip
detector you can compute before changing anything.

The two exceptions are both AG News Business stories that the no-break
space pushed to Sci/Tech, at margins 3.70 and 2.71 (agnews/2145,
agnews/2542). That's the condition with the most flips, and one
direction; part 3 (margins on the NBSP prompts) tests whether NBSP
moves confidence on items that don't flip too.

## Part 3: does the no-break space move confidence, or only answers? (~05:45 UTC)
`part3.py`; output in part3.txt. A shift is the NBSP prompt's margin
minus the canonical one, signed toward the canonical label (negative =
toward another label).

| NBSP | n | median shift | median abs shift | moved toward another label |
|---|---|---|---|---|
| flipped | 29 | -1.20 | 1.20 | 90% |
| unflipped | 1,171 | -0.01 | 0.75 | 51% |
| unflipped SST-2 | 397 | -0.76 | 0.98 | |
| unflipped BoolQ | 386 | +0.40 | 0.62 | |
| unflipped AG News | 388 | +0.24 | 0.75 | |

**Against PLAN.md:** unflipped margins don't "barely move": the median
moves 0.75 nat, far over 0.1. And 23 of 29 matched pairs (nearest-margin
unflipped item, same task) differ by sign or by more than 1 nat, so by
the pre-set rule "it's just low margin" doesn't explain the flips.
What the numbers look like instead: **the no-break space moves every
item's confidence by about 0.75 nat, and a flip is where that move is
toward another label and larger than the item's margin.** Pooled, the
direction looks random (51%); split by task it isn't: NBSP makes SST-2
less sure of its answer and BoolQ and AG News more sure. The two
exceptions from part 2 (Business stories to Sci/Tech) moved 3.2 and 3.9
nats, four to five times the typical move: there the format does act on
the item.

**Not yet settled:** whether 0.75 nat is the format or the margin's own
re-run noise. Part 3b (PLAN.md, threshold fixed first) runs the same
pass on the identical control prompts.

## Part 3b: the margin's own noise (~06:30 UTC)
Same pass on the identical control prompts (`part3.py ... margins-control.jsonl control`;
part3b.txt). Median abs shift: **0.000 nat** (SST-2 0.107, BoolQ and AG
News 0.000), against the pre-set line of 0.37. So the 0.75 nat in part 3
is the no-break space, not re-run noise: **the format moves confidence on
nearly every item, and flips are where it crosses the margin.**

One more thing it shows: the 3 items the identical re-run flipped in the
main run have a margin shift of exactly 0 here. Their canonical margins
are 0.26 (boolq/2049), 0.38 (boolq/2578) and 0.03 nat (boolq/3148).
*Corrected ~07:00 UTC: I first wrote "0.02 to 0.03, coin tosses" for all
three, from the one I'd looked at.* This pass didn't reproduce their
flips: the label it ranks first matches the canonical run's answer on
2049, and the control run's on 2578 and 3148. Two things my records
can't settle: whether each call was evaluated fresh or from cache (I
didn't log `prompt_eval_count`), and which single token greedy decoding
picked, since my margins sum a label's spellings ("yes", "Yes", " yes")
and keep only the sums, while greedy takes the one top token. The cache
probe (research/ollama-cache) logs the first; keeping the raw top-20
tokens would settle the second.
