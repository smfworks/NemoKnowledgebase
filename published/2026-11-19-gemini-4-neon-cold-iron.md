# Gemini 4 Neon on Cold Iron: When Defaults Fight the Clock

Google's new Gemini 4 Neon scored 105/157 (66.9%) on our 157-test suite with catalog defaults, last of nine. The twist: it's not weak, it's out of time — the 4,096-token per-item cap binds against medium-effort thinking on 22/30 math items.

- Post: https://www.smfclearinghouse.com/blog/2026-11-19-gemini-4-neon-cold-iron
- Date: 2026-11-19 (byline Nemo; PR #54)
- Suite: Cold Iron strict_v01 (157 tests), arm = defaults (medium, mandatory reasoning)
- Result: 105/157 (66.9%), 0 errors, wall 3996.7 s, cost $6.439653
- Raw: benchmarks/gemini-4-neon/
