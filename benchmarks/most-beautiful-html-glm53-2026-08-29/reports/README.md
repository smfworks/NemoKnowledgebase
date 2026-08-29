# Most beautiful HTML — GLM-5.3-Flash-EXL3 vs Ox Alpha vs Grok 4.6

Verbatim prompt (81 bytes):

```
create the most beautiful and stunning single HTML file you can possibly imagine
```

One shot each. No rewrite. No second turn. HTML fence shipped as-is.

| | Ox Alpha | Grok 4.6 | GLM-5.3-Flash-EXL3 |
|--|--|--|--|
| Model | `stealth/ox-alpha` | `x-ai/grok-4.6` | `GLM-5.3-Flash-EXL3` |
| Where | OpenRouter | OpenRouter | dual Spark `:8888` (`Mia-AiLab/…-EXL3-TR3-4bpw`) |
| Request | `gen-1787662535-q148pb4L4xNRVA89hGCs` | `gen-1787662119-UobWTVz7CyyFopbjTEVD` | `chatcmpl-95848dc0c63224ff` |
| Finish | stop | stop | stop |
| Wall | 1126.04 s | 154.19 s | 2111.61 s |
| TTFT | — | — | 2.75 s |
| Tokens (prompt / completion / total) | 101 / 43,451 / 43,552 | 220 / 11,295 / 11,515 | 26 / 55,239 / 55,265 |
| Reasoning chars (stream) | 111,373 | 1,122 | 144,567 |
| Cost | $0 | $0.068 | $0 (local) |
| Piece | AURELIA | AETHER | SUMI |
| HTML bytes | 29,055 | 30,139 | 46,039 |
| `node --check` inline JS | — | — | pass |
| Live | https://www.smfclearinghouse.com/demos/ox-alpha-aurelia | https://www.smfclearinghouse.com/demos/grok-4.6-aether | local only (not shipped) |

GLM notes:
- Smoke before one-shot: `chatcmpl-bf5641ae8b129a8a`, HTTP 200, 1.787 s.
- `max_model_len` advertised 640000. Serve id `GLM-5.3-Flash-EXL3`.
- Content is a WebGL fluid (Jos Stam) museum plate named SUMI. Google Fonts (Fraunces, IBM Plex Mono, Noto Serif JP). No external JS.
- Fence complete (`<!DOCTYPE html>` … `</html>`). Not truncated (`finish_reason=stop`).
- Decode including reasoning: 55,239 completion tokens / 2111.61 s ≈ 26.16 tok/s.

Raw: `/home/mikesai1/workspace/glm53-flash-tests/01-most-beautiful-html/`
