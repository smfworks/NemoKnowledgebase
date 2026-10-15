# Payload for the Cold Iron arm

`nvidia/nemotron-3.5-super-vl:free` still thinks if you only send `enable_thinking=false`.

Smoke on 2026-10-15, temperature 0, `max_tokens=64`, prompt `What is 2+2? Reply with just the number.`:

| Payload | Result |
| --- | --- |
| Default | content `4`, 49 reasoning tokens |
| `chat_template_kwargs.enable_thinking=false` | content `4`, 37 reasoning tokens |
| `reasoning.effort=none` | content `4`, 0 reasoning tokens |
| both of those together | content `4`, 0 reasoning tokens |

This 157 sent both:

```json
{
  "chat_template_kwargs": {"enable_thinking": false},
  "reasoning": {"effort": "none"}
}
```

`effort=none` alone is enough to land content with `reasoning_tokens=0` on that smoke. The runner also sends `enable_thinking=false` on `--thinking off`. We did not run a 157 on `effort=none` alone.

`nemotron` is already in the local runner's reasoning-indicator list, from Nemotron 3.5 Lightning. That raises the unset token cap to 4096. The tier-0 YAML files set their own 4096 cap. Do not add a broader token.

The exact-slug branch lives in the local `smf-bench` checkout used for this run. It is not claimed to be on the public `smf-bench` default branch.
