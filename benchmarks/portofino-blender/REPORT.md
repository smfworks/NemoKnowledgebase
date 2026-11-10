# Portofino Blender agentic test — 2026-11-10

Fable 5.2 26/30 vs Muse Ember 11/30. Full protocol, repair logs, and receipts in this directory.

- Prompt frozen: 2,376 bytes, sha256 b6164e3482b7af7e (prompt.txt in each model dir)
- Generations: Fable gen-1794315824-v9iFni1nMdsRL9Nvf1N0 ($1.80, 32,487 content chars, 19,531 reasoning, effort=low) · Muse gen-1794315831-pVJzhX0j9p3nOpCLf7hW ($0.0015, 8,687 chars, effort=minimal)
- Harness: Blender 4.5.3 LTS headless + render_runner.py (identical budget: 288 frames = first 12 s of each path, 1280x720, Cycles CPU 16 threads, 64 samples, denoised, H.264 24 fps)
- Repairs: Fable zero. Muse two (fixes.txt): cone radius1 API rename; camera frame-1 y -280 -> -298 (start inside hill Sphere.007)
- Final videos: Fable 0/24 sampled frames black; Muse 15/24 (62%) black - camera inside its own hill meshes (bbox containment verified at frames 72/100/144/200/288)
- Scorecards: ~/NemoVault/scorecards/2026-11-10-{fable-5.2,muse-ember}-portofino.md (rubric written pre-render)
- Post: https://www.smfclearinghouse.com/blog/2026-11-10-portofino-blender-agentic (videos + .blend embedded)
- n=1 both arms: designed comparison, not a stability study
