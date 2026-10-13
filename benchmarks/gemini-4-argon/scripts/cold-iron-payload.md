# Payload for the Cold Iron arm

`google/gemini-4-argon` rejects `reasoning.effort=none` and `reasoning.enabled=false` with HTTP 400.

This run sent:

```json
{
  "chat_template_kwargs": {"enable_thinking": false}
}
```

No `reasoning.effort` field. A 2+2 smoke on 2026-10-13 landed content `4` with `reasoning_tokens=0` on that payload, and on the default payload.

Do not copy Gemini 3.8 Flash's `reasoning.effort=low` onto this slug. We did not run the 157 that way.

Do not add `gemini` to the runner's reasoning-indicator list. That bumps every test to 4096 tokens. The tier-0 YAML files already set their own 4096 cap. Writing and tool items set lower caps.
