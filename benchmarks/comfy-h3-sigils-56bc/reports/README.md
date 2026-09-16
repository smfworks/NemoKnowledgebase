# Sigils in the Steel — spark-56bc Comfy native H3, 28 windows

Source: `~/comfyui-minimax-h3-dgx-spark/logs/sigils.jsonl` (8181 events).
Driver: `bin/sigils-driver.py`. Node: spark-56bc GB10.

- Start 2026-09-14T11:32:13Z, `all_pass` 2026-09-16T03:50:53Z (40.3 h calendar).
- 28/28 windows PASS. 20 `abort_thermal` (all retried). Denoise on PASS hops 33285.5 s (9.25 h).
- Final `smf_sigil_4min.mp4`: 262.846 s / 6285 f / 1344×768 / 24 fps / H.264 + AAC LC 32 kHz stereo / 169207079 bytes.
- Graph: INT8 ConvRot UNET + turbo v4-600 LoRA, 6-step simple scheduler, Motion-Context 22, hop-2+ trim 22.
- Music field in every prompt: `non_diegetic_music: N/A`. No spoken dialogue. Last-second hold.
- Desk fan from C1 attempt 2 (2026-09-15 ~05:51 EDT): C1 peak 83°C vs two 85/86°C aborts.

MP4s are MiniMax Community License internal eval. This JSON is the public receipt.
