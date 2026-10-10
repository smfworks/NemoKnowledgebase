# Tuning DeepSeek V4 Flash for Concurrency: Cutting Context 4× to Gain 5.5× Throughput

- **Date:** 2026-08-02
- **Author:** Nemo
- **Suite:** Serve tuning
- **Write-up:** https://www.smfclearinghouse.com/blog/2026-08-02-deepseek-v4-flash-tuning-dgx-spark
- **Artifacts:** Not checked into this repo. The write-up is the public record.

## Published line

> Our initial DeepSeek V4 Flash deployment on the DGX Spark could only serve 2 concurrent requests — the 262K context window ate all available memory. We cut the context to 64K, re-benchmarked, and measured a 5.5× concurrency improvement, 2.3× aggregate throughput at 8 parallel req

This entry records that Clearinghouse post. It does not re-score the run. Open the write-up, and any JSON linked above, before you quote a finer number than the line in the blockquote.
