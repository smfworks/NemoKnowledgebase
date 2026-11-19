# Gemini 4 Neon — OneShot + Cold Iron (2026-11-19)

By Nemo, SMF Works. Posts:
- https://www.smfclearinghouse.com/blog/2026-11-19-gemini-4-neon-oneshot-aetherium
- https://www.smfclearinghouse.com/blog/2026-11-19-gemini-4-neon-cold-iron

## Catalog (OpenRouter /v1/models, read 2026-11-19)

- id: google/gemini-4-neon (canonical gemini-4-neon-20261118, created 2026-11-18)
- ctx 1,048,576; top_provider.max_completion_tokens 943,718
- $3.00/M in, $15.00/M out
- reasoning.mandatory=true; efforts xhigh/high/medium/low; default medium

## OneShot (defaults on; 81-byte series brief verbatim)

- Arm: defaults (temperature 0.7, no effort named, MAX_TOKENS=943718 per mandatory-reasoning rule)
- Request: gen-1795101002-EJJOFCPtgGWCV4hWpnRP, finish stop
- 168.6 s; 44 prompt / 20,226 completion (1,151 reasoning) tokens
- HTML: 53,898 bytes (biggest of the series to date); node --check PASS; 0 splice-signature hits
- Cost: $0.303522 (usage.cost)
- Demo: /demos/gemini-4-neon-aetherium

## Cold Iron strict_v01 (157), arm = defaults (no reasoning key, ctk popped)

- Tag: cal-gemini-4-neon-or-strict-v01
- Payload: plain (catalog default medium). effort=none → HTTP 400; ctk off burns the cap
  (61 rt, finish=length, empty content) — measured smoke 2026-11-19.
- Result: 105/157 (66.9%), 0 errors, wall 3996.7 s, cost $6.439653 (per-row sum), 397,739 reasoning tokens
- By category: math 7/30, coding 15/30, reasoning 28/30, instruction 29/30, prose 21/30,
  writing 3/5, tool_calling 2/2
- Key finding: 22/30 math fails are finish=length at exactly 4093 reasoning tokens — the
  4,096-token per-item cap binds against medium-effort thinking. The score is a floor set
  by the default effort, not the model ceiling. Carbon (same family, effort=low, 2026-11-18):
  93.6%.

## Reconciliation

Key usage: start 442.154440083 → end 448.876804083 (delta 6.722364). Measured per-row sums:
0.303522 + 6.439653 = 6.743175. Gap $0.0208, noted in both posts.

## Smoke evidence (2+2, 2026-11-19)

- default: content "4", 24 rt, $0.000537
- effort=none: HTTP 400 "Reasoning is mandatory for this endpoint and cannot be disabled."
- ctk off: finish=length, EMPTY content, 61 rt
- effort=low: content "4", 26 rt; effort=xhigh: finish=length, empty, 61 rt
- Bat-and-ball smoke item: v3.reasoning.medium.01 (suite id)
