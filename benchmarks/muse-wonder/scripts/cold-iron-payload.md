# Payload for the Cold Iron arm

`meta/muse-wonder` rejects `reasoning.effort=none` and `reasoning.enabled=false` with HTTP 400. `chat_template_kwargs.enable_thinking=false` does not stop reasoning.

Send this on every Cold Iron request, including the ones the suite caps at 1024:

```json
{
  "reasoning": {"effort": "minimal"},
  "chat_template_kwargs": {"enable_thinking": false}
}
```

`effort=minimal` is the lowest catalog effort. It is not true thinking-off. A 2+2 smoke on 2026-10-12 landed content `4` with 20 reasoning tokens.

Do not add `muse` to the runner's reasoning-indicator list. That bumps every test to 4096 tokens. The tier-0 YAML files already set their own 4096 cap. Writing and tool items set lower caps.
