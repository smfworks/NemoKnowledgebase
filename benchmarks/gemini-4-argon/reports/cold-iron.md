# Gemini 4 Argon Cold Iron

OpenRouter `google/gemini-4-argon`. Thinking-off arm is `chat_template_kwargs.enable_thinking=false` and no `reasoning.effort` field. `effort=none` and `enabled=false` return HTTP 400. Default also landed content with `reasoning_tokens=0` on a 2+2 smoke. Tag `cal-gemini-4-argon-or-strict-v01`.

Score: 152/157 (96.8%). Fail 5. Error 0. Wall 966.2 s. Key delta $1.090362 (401.347003746 to 402.437365746).

Result file: `results/stage1_cal-gemini-4-argon-or-strict-v01_20261013_162813.json`.

Cold Iron stays text-only. The card claims image, file, audio, and video input. This file does not score that.

Do not copy Gemini 3.8 Flash's `reasoning.effort=low` onto this slug. This run did not send an effort field.
