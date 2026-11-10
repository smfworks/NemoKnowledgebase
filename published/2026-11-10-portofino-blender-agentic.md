# 2026-11-10 — Portofino agentic test: Fable 5.2 26/30 vs Muse Ember 11/30

- **Test:** give each model the same frozen Portofino prompt; it writes a Blender script; we render headless and score the result
- **Result:** Fable 5.2 ran first-try, 0/24 black frames, 26/30 rubric. Muse Ember needed 2 mechanical fixes and 62% of its video is black (its camera path flies through its own hills), 11/30
- **Costs:** Fable $1.80 script, Muse $0.0015 (1,200x cheaper) — but cheap did not survive contact with a renderer
- **Data:** [benchmarks/portofino-blender/](../benchmarks/portofino-blender/)
- **Post:** https://www.smfclearinghouse.com/blog/2026-11-10-portofino-blender-agentic
- n=1 both arms (designed comparison, not stability)
