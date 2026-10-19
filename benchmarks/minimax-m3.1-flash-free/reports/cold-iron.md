# MiniMax M3.1 Flash free — Cold Iron

- Model: `minimax/minimax-m3.1-flash:free`
- Endpoint: `https://openrouter.ai/api/v1`
- Suite: Cold Iron, `strict_v01`, 157, thinking-off analogue
- Payload: `reasoning.effort=low` alone. Do not also send `enable_thinking=false`.
- Score: 136/157 (86.6%), 21 fails, 0 errors
- Wall: 1471.6 s
- File: `results/stage1_cal-minimax-m31-flash-free-or-strict-v01_20261019_122100.json`
- Tag: `cal-minimax-m31-flash-free-or-strict-v01`

`reasoning.effort=none` and `reasoning.enabled=false` are HTTP 400. The scored file has nonzero `reasoning_tokens` on 144 rows. This is the lowest listed effort, not true off.

The public `smf-bench` checkout at `5d9ddf6` does not send this payload. The launch script calls a local runner branch that is not on that remote.

Write-up: https://www.smfclearinghouse.com/blog/2026-10-19-minimax-m3.1-flash-cold-iron
