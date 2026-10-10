# Qwen3.8-Flash-Next on one Spark: MiaAI's 24/7 kit, measured

- **Date:** 2026-09-19
- **Author:** Nemo
- **Suite:** Serve decode measurement
- **Write-up:** https://www.smfclearinghouse.com/blog/2026-09-19-qwen38-flash-next-24-7-kit
- **Artifacts:** [`benchmarks/qwen3.8-flash-next-tp1-d369`](../benchmarks/qwen3.8-flash-next-tp1-d369) (paths from this file)

## Published line

> We took MiaAI-Lab's 24/7 single-Spark recipe at 6b50864 on spark-d369. Recipe structured decode at one stream matched their published 65.2 tok/s. Two-stream per-stream rate matched; aggregate did not, and we still pin MAX_NUM_SEQS=2.

This entry records that Clearinghouse post. It does not re-score the run. Open the write-up, and any JSON linked above, before you quote a finer number than the line in the blockquote.
