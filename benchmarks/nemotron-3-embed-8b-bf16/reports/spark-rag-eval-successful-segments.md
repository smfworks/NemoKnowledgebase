# Nemotron-3-Embed-8B-BF16 Spark RAG eval — successful segments

Serve recipe: `SMF-Spark-vLLM-0.24-nemotron3-embed-8b-bf16`

## Speed (speed_20260717T161853Z.json)
- Query mean latency: 74.8 ms
- Short bs32: 102.6 texts/s
- Medium bs32: 27.8 texts/s
- Long bs16: 4.0 texts/s

## BEIR macro nDCG@10: 0.7158
| Task | nDCG@10 | R@10 |
|------|--------:|-----:|
| SciFact | 0.8337 | 0.9467 |
| NFCorpus | 0.4228 | 0.2080 |
| ArguAna | 0.6313 | 0.9132 |
| FiQA2018 | 0.6564 | 0.7213 |
| TRECCOVID | 0.8660 | 0.0238 |
| QuoraRetrieval | 0.8843 | 0.9580 |

## Praxis synthetic
- mean nDCG@10: 0.975
- mean Recall@3: 0.917

See Clearinghouse post 2026-07-20-nemotron-3-embed-8b-dgx-spark-rag.
