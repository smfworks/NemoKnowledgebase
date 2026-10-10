# How we test

This is the method behind the numbers on the [repo front page](../README.md). If a post and this file disagree about a suite's size, count the YAML. The YAML wins.

## Cold Iron

Cold Iron is the thinking-off 157. It used to be called Official A. The runner flag is still `--core-profile strict_v01`.

Ranked arm:

- Thinking off, or the closest analogue the endpoint will accept. Record what you sent. Do not relabel a refusal as thinking off.
- Temperature and token caps are whatever that run's JSON says. Do not invent a house default after the fact.
- Errors stay in the denominator. A 429 is not a quiet skip.
- Text only. Vision and video claims on a model card are unscored here.
- Thinking-on runs are diagnostic. They do not enter the Cold Iron rank.
- A one-shot HTML file, a video wall-clock, and a coding-agent transcript are different tests. Say so in the post.

Category counts, from `smf-bench/suites/` on 2026-10-10:

| File | Tests |
| --- | ---: |
| `suites/quality/tier0_deterministic/math.yaml` | 30 |
| `suites/quality/tier0_deterministic/coding.yaml` | 30 |
| `suites/quality/tier0_deterministic/reasoning.yaml` | 30 |
| `suites/quality/tier0_deterministic/instruction.yaml` | 30 |
| `suites/quality/tier0_deterministic/prose.yaml` | 30 |
| `suites/quality/writing/writing.yaml` | 5 |
| `suites/quality/tool_calling/tool_calling.yaml` | 2 |

30+30+30+30+30+5+2 = 157.

## Official B

`legacy_181` is Cold Iron plus:

| File | Tests |
| --- | ---: |
| `suites/quality/reasoning/reasoning.yaml` | 8 |
| `suites/quality/agentic/agentic.yaml` | 16 |

157+8+16 = 181.

Use Official B when you are continuing the July Stage 1 board. Do not paste an Official B percent next to a Cold Iron percent and call it a ranking.

## What we refuse to do

- We do not average two serves of the same model into one rank.
- We do not hide a timeout inside a fail.
- We do not treat a vendor leaderboard as our score.
- We do not publish a number we did not open in the result file or the command output.
- We do not call a partial run complete.

## Where the files go

| Thing | Path |
| --- | --- |
| Published write-up index | `published/<slug>.md` |
| Scripts | `benchmarks/<name>/scripts/` |
| Raw JSON | `benchmarks/<name>/results/` |
| Short lab report | `benchmarks/<name>/reports/` |
| Generated images or clips, when they are the test media | `benchmarks/<name>/test-media/` |

The narrative lives on the Clearinghouse. This repo is the bench and the index.
