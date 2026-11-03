# 2026-11-03-glm-5-3-flash-dog-violin-stage-one-shot

[One prompt, no iteration: GLM-5.3-Flash TensorFold on dual DGX Sparks wrote a CSS dog, a Web Audio violin synth, and a functioning light switch. The first long run came back splice-corrupted, two reruns reproduced it byte-identically, and a three-length sweep shows the fault hides in completions of roughly ten thousand tokens or more.](https://www.smfclearinghouse.com/blog/2026-11-03-glm-5-3-flash-dog-violin-stage-one-shot)

- Model: GLM-5.3-Flash EXL3 4-bit TensorFold TP=2, 2x DGX Spark, thinking off, temperature 0
- Dog/violin/light-switch one-shot: 11,845 completion tokens; raw output splice-corrupted (deterministic, byte-identical across 2 runs); repaired and verified
- Length sweep 2026-11-03: clean at 1.4k / 2.2k / 6.0k tokens
- Artifacts: [benchmarks/glm-5.3-flash-tf-oneshots/](../benchmarks/glm-5.3-flash-tf-oneshots/)
