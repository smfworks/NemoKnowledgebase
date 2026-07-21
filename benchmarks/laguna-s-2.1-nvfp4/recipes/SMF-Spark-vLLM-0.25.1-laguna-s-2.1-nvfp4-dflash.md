# SMF-Spark-vLLM-0.25.1-laguna-s-2.1-nvfp4-dflash

- Host: spark-56bc (DGX Spark GB10)
- Engine: vLLM 0.25.1 + FlashInfer 0.6.15.dev20260712
- Model: poolside/Laguna-S-2.1-NVFP4
- Draft: poolside/Laguna-S-2.1-DFlash-NVFP4 (15 tokens, method=dflash)
- util 0.82 · max_model_len 262144 · max_num_seqs 32
- parsers: poolside_v1 tools + reasoning
- port 8888
- Official A run: cal-laguna-s-2.1-nvfp4-strict-v01 · 107/157 · 2026-07-21

See blog: https://www.smfclearinghouse.com/blog/2026-07-21-laguna-s-2.1-nvfp4-smf-bench-coding-local
