The user wants the most beautiful and stunning single HTML file I can imagine. This is a completely open brief — a chance to create something truly memorable. Let me think deeply about what would make this exceptional.

What are my options?
1. A generative art piece — interactive canvas, flowing particles, etc.
2. An immersive narrative experience — scroll-driven storytelling
3. A "digital garden" / living ecosystem simulation
4. A typographic masterpiece — kinetic type, editorial design
5. An interactive audio-visual instrument
6. A generative "living painting" that evolves

I want something that:
- Has an instant first impression that lands
- Is continuously alive — responds to every input
- Has a signature moment people remember
- Feels authored, not generated
- Avoids all the cheap tells: no gradient banners, no blue/purple, no emoji, no equal-width card grids, no dashboard feel

Let me think about a concept. The strongest ideas combine:
- A unified visual language
- Real interactivity
- A poetic concept that gives it soul

Concept ideas:

**A. "Aurora" — a living sky.** Interactive fluid simulation of aurora borealis. Beautiful but common as AI output; fluid sims are done a lot.

**B. "The Observatory" — a night sky atlas.** An interactive star map where you can drag, zoom, constellations draw themselves, and clicking stars reveals generated poetry. Elegant, dark, gold-on-ink aesthetic. Could be gorgeous but risks feeling like a widget.

**C. "Ink & Water" — an ink wash painting that lives.** Japanese/Chinese sumi-e aesthetic. Brush strokes bloom in water on rice paper. Mouse movement creates ink dispersal. Very refined, very authored. Typography: a beautiful serif, vertical text accents. Signature moment: the ink blooms.

**D. "Ephemera" — a generative art gallery of one.** A single canvas piece that regenerates, with editorial framing like a museum plaque. The framing device is memorable but the content needs to carry it.

**E. "The Garden of Forking Paths"** — a generative tree/plant that grows with your cursor, Borges-inspired. Organic, alive.

**F. "Kairos" — a clock made of light** — time-based generative art where the piece changes with time of day.

**G. A fluid ink simulation combined with editorial typography** — "the page is the painting". I keep coming back to ink.

Let me think harder. What's genuinely stunning and achievable in a single file with no build step?

Top candidates:
1. **Real-time fluid dynamics (Navier-Stokes) ink simulation** — this is the single most impressive thing you can do in vanilla WebGL. Ink swirling in water, responding to the mouse with gorgeous fluid dynamics. Combined with a refined typographic layer (title, subtle instructions), it becomes an art piece: "Sumi" or "Ink" — an interactive ink water. The fluid sim is genuinely stunning — people remember it. I've implemented stable fluids before (Jos Stam's method, GPU shaders). This is the signature moment: drag your cursor and ink blooms and swirls with real physics.

2. **A star atlas** — beautiful but more static.

3. **Growth/organic simulation** — L-systems reacting to cursor.

The fluid ink simulation is the winner for pure visual impact. But I must be careful: "black background with colorful fluid sim" is somewhat common. How do I elevate it?

Elevation strategy:
- **Aesthetic direction**: Not neon rainbow ink. Instead, a curated, restrained palette — like mineral pigments: indigo, vermilion, gold ochre, jade. On a deep near-black warm paper tone (not pure black — maybe deep ink #0d0c0a or a warm charcoal). The ink colors could be sampled from a pigment palette that shifts subtly.
- **Typography layer**: A large, elegant serif title (e.g., "S U M I" or a name like "墨 — Ink"). Use a distinctive font — Cormorant Garamond or Fraunces from Google Fonts. Vertical Japanese text accent (writing-mode: vertical-rl) with the kanji 墨. Very editorial, museum-like. Small caption: "an experiment in fluid pigment — move slowly, the water remembers."
- **Micro-interactions**: 
  - Mouse move = gentle ink currents
  - Mouse drag (or click) = splat of pigment
  - Idle = autonomous gentle currents so the piece is never dead (self-stirring)
  - A minimal control: a small pigment palette (dots) to choose ink color, rendered as pigment dots like a painter's palette
  - Maybe a "clear water" action that fades gracefully
- **Signature moment**: The initial load — a single drop of ink falls into still water and blooms in slow motion while the title fades in. That first bloom is the memory.

Actually, let me reconsider — fluid sims in WebGL require careful shader code. I know the standard stable fluids implementation well:
- Textures: velocity, pressure, divergence, dye/color, curl
- Passes: advection, curl, vorticity confinement, divergence, pressure Jacobi iterations, gradient subtraction, splat, display
- Requires float textures; use half-float with fallbacks

This is a lot of code but I can write it correctly. I've seen the famous WebGL-Fluid-Simulation by Pavel Dobryakov. I should write my own version, not copy it verbatim — I'll write my own implementation with my own structure, my own aesthetic choices (pigment palette, paper texture overlay, bloom behavior tuned for ink, self-stirring idle currents, graceful fade). The core algorithm is standard computer graphics (Stam's stable fluids), so implementing it is fine; I'll author everything myself.

Alternatively — a 2D canvas approach with metaballs/particles would be less impressive. The WebGL fluid is the right call for "most stunning".

Let me also consider combining with a second layer: a subtle paper grain overlay (CSS or canvas noise) to give it a tactile, printed feel rather than screen-glow. And film-like vignette. These are craft details.

Let me plan the full experience:

**Title/Concept**: "墨 SUMI" — An interactive ink water. Or maybe something less tied to Japanese calligraphy to avoid cultural pastiche? Actually sumi-e ink is a beautiful, respectful reference. Alternatively "TIDE", "INDIGO", "PIGMENT". Let me go with something evocative: "S U M I — the memory of water". Or in a more universal framing: "INKWATER". Hmm. Let me name it "墨 / SUMI — ink · water · memory". I'll include a small line: "Every gesture dissolves; the water remembers nothing, and everything." Poetic copy matters.

Actually, let me make it bilingual-feeling: big serif "SUMI" with 墨 as a large, faint watermark character behind or beside. Vertical-rl side text: "墨絵 — a study in fluid pigment".

**Palette** (pigments, not neon):
- 藍 Indigo: #1b3a8f-ish → but on dark bg needs brightness. Let me define dye colors as RGB added on dark background. Pigment palette options:
  - Vermilion 朱 (0.9, 0.25, 0.15)
  - Indigo 藍 (0.15, 0.3, 0.85)
  - Gold 土 (0.95, 0.7, 0.2)
  - Jade 翠 (0.1, 0.7, 0.45)
  - Sumi 墨 (near-white gray? On dark bg, ink is usually black on white... hmm)

Wait — traditional sumi is black ink on white paper. But a fluid sim looks better with glowing dye on dark. Two options:
a) Dark background, luminous pigment dye (like light in water) — more "stunning" visually.
b) Light paper background with dark ink — more authentic sumi-e but harder to make luminous; advection of dark dye on light works if I render dye as absorption. Actually it can look incredible too — black ink tendrils on warm paper. But WebGL fluid with bright dye on dark is the classic stunning look.

I'll go with (a): deep warm charcoal background (like a dark room), and the dye behaves like light-carrying pigment. But to nod to sumi-e, I could offer a "Sumi" mode... no, keep it focused. One clear idea: luminous mineral pigments in dark water. Restrained palette of 5 pigments, curated.

Actually — here's a thought to make it more distinctive: instead of saturated rainbow splats, the dye colors should be slightly desaturated, deep mineral tones, and the display shader should add subtle "paper grain" and vignette, plus a soft tone-mapping so highlights bloom gently (I can do a cheap bloom or just soft shading). Pavel's sim has bloom; implementing full bloom adds complexity. A simpler trick: shading (fake 3D from dye gradient) and soft saturation curve. I'll include a lightweight bloom? Bloom requires downsampled blur passes — maybe 5 mip levels. That's a lot but I can do a simplified single-pass blur-based glow at low cost. Hmm, let me keep scope controlled: the fluid itself with good colors and soft rendering is already stunning. I'll add:
- Soft shading (gradient-based lighting) — subtle
- Vignette + grain in display shader
- Dye dissipation tuned so ink slowly diffuses/fades like memory

**Interactions**:
- Pointer move: apply force + small splat (throttled by distance moved)
- Pointer down + move: stronger splat
- Click (tap): a drop — a splat with slight downward velocity
- Idle > few seconds: autonomous "breath" — gentle random currents and occasional drips so the piece lives alone
- Keyboard: number keys 1–5 select pigment; C clears (fade out); Space = "pulse" (a ring of force)? Maybe keep it minimal: 1-5 pigment, C clear.
- Palette UI: bottom-left, five pigment dots with Japanese labels on hover; selected one has a ring. Click to select. Also a small "still the water" (clear) button — text button, minimal.
- Double-click could toggle... no, keep it simple.

**UI layout**:
- Top-left: title block — "SUMI" large serif, with 墨 character, subtitle line, and a thin rule. 
- Bottom-left: pigment palette + clear action.
- Bottom-right: small caption "drag to stir · press to pour" and maybe a hint that fades.
- All UI in a warm off-white (paper color) on the dark field, very restrained. Hairline borders. No cards, no boxes with backgrounds — just typographic elements floating on the water. 
- A tiny "fps"? No — that's dashboard-y. Skip.

**Fonts**: Fraunces (has beautiful optical sizes, distinctive) for display; maybe "IBM Plex Mono" or "Spectral" for small captions. Fraunces + a mono for labels feels crafted. Japanese characters will fall back to system fonts — that's fine; I could load "Noto Serif JP" for the kanji to be safe. Let me load Fraunces + Noto Serif JP (only needed weights) + maybe "Space Grotesk"? Keep it to two families: Fraunces (display + text) and Noto Serif JP for CJK. Small labels can use Fraunces small caps or letterspaced uppercase — elegant.

Hmm, actually for tiny UI labels, a refined grotesk or mono reads better. "Spline Sans Mono" or "IBM Plex Mono" at small size, letterspaced uppercase. Let me use Fraunces for display, IBM Plex Mono for micro-labels. That's a distinctive pairing.

**Load sequence (signature moment)**:
1. Black-ish screen, title fades in letter by letter (or a mask reveal).
2. After ~800ms, three drops of ink fall from top center in sequence (indigo, vermilion, gold) — each is a splat with downward velocity, blooming as they hit an invisible "water line"... actually simpler: just splats at center with velocity, they bloom beautifully.
3. Hint text fades in: "move slowly — the water listens".
4. Then it's fully interactive.

I can choreograph the intro splats with timed JS calls to the splat function with nice parameters.

**Technical implementation plan** (WebGL1 with extensions, fallbacks):

I'll implement the standard stable fluids:

Textures (double-buffered where needed):
- velocity (RG16F), double
- dye (RGB16F), double
- pressure (R16F), double
- divergence (R16F), single
- curl (R16F), single

Shaders:
- baseVertex: computes vUv, vL, vR, vT, vB using texelSize
- copy/clear program
- splat program (adds gaussian of color/velocity)
- advection program (with manual bilerp fallback if linear filtering unsupported — for half float in WebGL1, OES_texture_half_float_linear may be missing; I'll implement manual bilinear)
- divergence
- curl
- vorticity
- pressure (Jacobi iteration)
- gradientSubtract
- display (with shading, vignette, grain)

Frame loop:
1. dt clamp
2. update colors if needed (I'll keep static per-pigment colors, maybe slight hue drift over time for life — subtle variation each splat)
3. apply inputs (pointer)
4. idle choreography: if time since last interaction > 4s, spawn gentle random force/splat occasionally
5. step simulation: curl → vorticity → divergence → pressure clear+iterate → gradient subtract → advect velocity → advect dye
6. render display to screen

Config:
- SIM_RESOLUTION 128–144 (velocity), DYE_RESOLUTION 512–1024 depending on device (I'll pick 1024 desktop, 512 mobile)
- PRESSURE_ITERATIONS 20
- CURL 30 (vorticity strength) — for ink, maybe 25
- DENSITY_DISSIPATION ~ 0.8–1.2 (ink fades slowly — for "memory", lower like 0.6 so it lingers; but too low fills screen. Use ~1.0 with slight fade)
- VELOCITY_DISSIPATION ~0.3
- PRESSURE ~0.8

Also handle:
- resize (recreate framebuffers preserving dye via copy? simpler: recreate and lose content — but I can copy old dye into new via a copy program with bilerp. Pavel's does that. I'll implement resizeFBO with copy.)
- visibilitychange pause
- WebGL unavailable: show a graceful message (styled) — rare case.

Half float support: WebGL1 needs OES_texture_half_float; rendering to half float needs EXT_color_buffer_half_float (WebGL1: it's implicitly supported in many browsers; standard approach: try framebuffer completeness). Alternative: use WebGL2 with EXT_color_buffer_float when available, else WebGL1 path. Pavel's code handles both. I'll write a compact version supporting both WebGL2 and WebGL1 with half float, with manual bilerp fallback when linear filtering unsupported.

Actually to reduce complexity, I could require WebGL2 (widely supported now, ~97%+). But graceful WebGL1 fallback isn't too much extra if I structure getSupportedFormat properly. Let me write the standard robust context setup:

```js
function getWebGLContext(canvas){
  const params = {alpha:true, depth:false, stencil:false, antialias:false, preserveDrawingBuffer:false};
  let gl = canvas.getContext('webgl2', params);
  const isWebGL2 = !!gl;
  if(!isWebGL2) gl = canvas.getContext('webgl', params) || canvas.getContext('experimental-webgl', params);
  let halfFloat, supportLinearFiltering;
  if(isWebGL2){
    gl.getExtension('EXT_color_buffer_float');
    supportLinearFiltering = gl.getExtension('OES_texture_float_linear');
  } else {
    halfFloat = gl.getExtension('OES_texture_half_float');
    supportLinearFiltering = gl.getExtension('OES_texture_half_float_linear');
  }
  const halfFloatTexType = isWebGL2 ? gl.HALF_FLOAT : halfFloat.HALF_FLOAT_OES;
  // format detection with getSupportedFormat
  ...
}
```

getSupportedFormat checks renderability by creating FBO test. Standard.

Shaders in WebGL2 need `#version 300 es`? Pavel's uses WebGL1-style GLSL 100 which works in WebGL2 contexts too (WebGL2 accepts GLSL ES 1.00 shaders). Yes — WebGL2 supports GLSL 1.00 shaders. So I can write all shaders in GLSL 100 and they run in both. 

Manual bilerp in advection when supportLinearFiltering is false — compile two variants via #define.

Display shader details:
```glsl
vec3 c = texture2D(uTexture, vUv).rgb;
// shading
vec3 lc = texture2D(uTexture, vL).rgb; ... 
float dx = length(rc) - length(lc);
float dy = length(tc) - length(bc);
vec3 n = normalize(vec3(dx, dy, length(texelSize)));
vec3 l = vec3(0.0, 0.0, 1.0);
float diffuse = clamp(dot(n, l) + 0.7, 0.7, 1.0);
c *= diffuse;
// tone map-ish soft
c = c / (1.0 + c*0.15)? 
```
Hmm, careful not to wash out. Pavel uses: `a = max(r,g,b); c = 1 - exp(-a*exposure)`? Actually his bloom does soft knee. I'll do a gentle filmic-ish curve: `c = pow(c, vec3(0.9))`? Let me keep: soft saturation boost then vignette + grain:

```glsl
float vig = smoothstep(1.0, 0.35, distance(vUv, vec2(0.5)) * 1.2); // careful
c *= mix(0.75, 1.0, vig);
float grain = (hash(vUv*time) - 0.5) * 0.035;
c += grain;
```

Background color: I'll clear dye buffer to background? Standard approach: dye starts black, display adds background color: `c += bgColor`? Pavel: `c += uBackgroundColor * (1 - something)`? He does `vec3 background = ...; c += background * (1.0 - ...)`? Actually simplest: output `background + c` where background is the deep charcoal (0.043, 0.04, 0.036) — since dye adds light on top. But vignette should darken background too. Order: `vec3 col = bgColor + c*diffuse; apply vignette to col; add grain; output`. Good.

Actually for richer feel, background could have extremely subtle radial variation — vignette handles that.

**Paper grain overlay**: I'll do grain in display shader (animated subtle noise) — enough. Plus maybe a static CSS noise? Shader grain is cleaner.

**Splat parameters**: radius ~0.25/100 (Pavel uses SPLAT_RADIUS 0.25 with correctRadius scaling by aspect). For ink drops, radius 0.3, velocity scaled by delta. For pointer move without press: small splat (radius 0.12, dye amount lower) so moving paints lightly; press = pour (strong). Actually Pavel's default: move always splats. For ink feel: hover-move = gentle current + faint pigment trail; press-drag = rich pour. 

Hmm — one consideration: on touch devices, touch always = press. Fine.

**Pigment color variation**: Each pigment base color; on each splat, multiply by random 0.85–1.15 per channel slightly for organic variation. Also maybe blend adjacent pigment? No — keep chosen pigment with variation.

Also "auto mode": every ~5–9s of idle, choose a random pigment and do a slow drip: a few splats along a gentle arc with small velocities — like someone barely touching the water. Plus constant faint ambient force field? Maybe a very slow rotating force at center to keep water subtly moving. Careful not to make it noisy. I'll implement: idle timer; when idle > 3.5s, every 2.5–5s spawn a "drip" (single splat, small radius, moderate dye, slight random velocity) at random position biased toward center-ish; occasionally (30%) a "current" — a sequence of small force splats along a curve over ~1s. That keeps it alive.

**Intro choreography**:
- t=0: canvas visible, water still, UI hidden (opacity 0)
- t=400ms: title "SUMI" reveals via clip-path or letter stagger
- t=900ms: kanji 墨 fades to 0.5 opacity
- t=1200ms: three drops: indigo at (0.5, 0.42) with velocity (0, 800)? Drops should look like they fall: spawn splat slightly above target with downward velocity... in fluid sim, splat adds dye + velocity at a point; giving velocity downward makes dye streak downward. To simulate a falling drop, do several splats over ~300ms moving down: positions from y=0.3 to 0.45 with velocity (0, +downward in texture coords... note y axis: WebGL vUv y up; pointer y inverted). I'll just do 3 quick splats descending with strong downward velocity — looks like a pour. Then a second drop in vermilion slightly right, then gold small. Stagger 350ms.
- t=2600ms: hint + palette + captions fade in.

Also I want the title to sit elegantly; maybe title has mix-blend-mode: screen? No — keep plain text over canvas, color paper-white #e8e2d6.

**Copy** (English, since user wrote English):
- Title: SUMI
- Overline: 墨 · a fluid pigment study
- Sub: "Five mineral pigments suspended in dark water. Stir gently — the water keeps every gesture, then forgets."
- Hint: "move to stir · press to pour · 1–5 to change pigment · C to still the water"
- Clear button label: "still the water"
- Bottom-right caption: maybe "no two moments repeat" — small italic.

Keep copy sparse and poetic. All real, no lorem.

**Palette UI**: five circles (18px) with pigment colors, labels in mono uppercase on the side or tooltip. Selected: ring offset. Vertical stack bottom-left with label "PIGMENT". Plus below, the "still the water" text button with hairline underline. Keyboard accessible (buttons). Hover: slight scale.

Pigment colors (as dye RGB on dark):
- Indigo 藍 ai: rgb(0.18, 0.34, 0.95)? Let me think in sRGB-ish for UI dots and convert for dye. Dye values are added and accumulated; typical Pavel splat color = HSV random with V=1, then *0.15. I'll define base colors:
  - Indigo: #3D5AFE-ish → too electric. Mineral indigo: (0.20, 0.35, 0.90) fine — on screen it reads blue-violet... I want to avoid generic blue-purple vibes. Indigo is legit here as one of five pigments, not the whole scheme. The overall scheme is charcoal + multicolor pigment. Fine.
  - Vermilion: (1.0, 0.28, 0.18)
  - Ochre/Gold: (1.0, 0.72, 0.25)
  - Jade: (0.15, 0.85, 0.55)
  - Sumi white? A "silver/moon" pale: (0.9, 0.92, 0.95) — like moonlight/metallic. That's a nice fifth: "Kōhaku"? Call it "Moon 白". Hmm "白" is white. Silver moon: (0.85, 0.88, 1.0) slight cool. Nice for highlights.

So pigments: INDIGO 藍, VERMILION 朱, OCHRE 金, JADE 翠, MOON 白. Default selected: Indigo (intro drops use indigo+vermilion+gold regardless).

Splat dye intensity: multiply base color by ~0.5 for hover, 1.0 for pour? Pavel multiplies by 0.15 because colors accumulate fast. Actually his SPLAT uses color*10 in some versions... In his code: `splatColor` = HSV random * 0.15. And pointer move splats use that. I'll tune: pour color = base * 0.6, hover = base * 0.15. With DENSITY_DISSIPATION ~1.0 (exponential decay per second: dissipation formula uses `exp(-dissipation*dt)`), dye persists a few seconds. For "memory" feel, use dissipation 0.8 → half-life ~0.87s? exp(-0.8*1)=0.45 per second — quite fast fade. Pavel default DENSITY_DISSIPATION=1.0. For lingering ink, maybe 0.55. But then screen accumulates. There's also diffusion from advection bilerp which blurs it out. I'll pick ~0.75 and let brightness be moderate. Tunable — I'll choose values that generally look good: DENSITY_DISSIPATION 0.8, VELOCITY_DISSIPATION 0.25, PRESSURE 0.8, PRESSURE_ITERATIONS 20, CURL 28, SPLAT_RADIUS 0.22.

**Resolution handling**: SIM 144, DYE 1024 desktop; if mobile (width<768 or touch), SIM 96, DYE 512. Also cap by devicePixelRatio? Dye resolution independent of canvas pixels — display shader upsamples with linear filtering. Good.

**Pointer handling**: track pointers (support multi-touch — each touch its own pointer with prev position). On pointermove compute delta, apply force: dx = deltaX * forceScale. Splat at position. Only splat when moved enough or pressed. Also pointerdown triggers a bigger "drop" splat.

Edge case: pointer coordinates → uv: x = clientX/width, y = 1 - clientY/height (since WebGL y flipped). Velocity dx in uv units: (x - prevX) * something; Pavel: `dx = (x - prevX) * canvas.width?` He uses corrected deltaX = x - prevX then multiplies by force 6000 in splat as velocity = dx * force? His: `splat(pointer.texcoordX, pointer.texcoordY, pointer.deltaX * 6000? ...` Actually: `let velocity = {x: pointer.deltaX * config.SPLAT_FORCE, y: pointer.deltaY * config.SPLAT_FORCE}` with SPLAT_FORCE=6000, deltas in texcoord units. Yes.

**Aspect-corrected splat radius**: `correctRadius(radius){ let aspect = width/height; if(aspect>1) radius *= aspect; }` — actually Pavel multiplies when aspect > 1 for x. His splat shader uses aspect in gaussian: `p.x *= aspect`. I'll include aspect in splat shader: `vec2 p = vUv - point; p.x *= aspectRatio;` and radius corrected similarly.

**Resize**: on window resize, resize canvas to clientWidth*dpr (dpr capped at 2), recreate FBOs with resize (copy old content). I'll implement `resizeDoubleFBO` using a copy program.

**Pressure clear**: multiply pressure by 0.8 each frame (clear program with value) — standard.

Let me now also think: is there anything else to add for "stunning"? 

Possible additions:
- **Sound?** Web Audio ambient drone or water sounds synthesized? Could be magical — a soft filtered noise "water" that responds to stirring intensity. Autoplay restrictions: start audio on first user gesture, with a small mute toggle. This could elevate a lot — "the water listens". A gentle lowpass noise whose cutoff/gain follows pointer speed, plus occasional droplet plinks (sine blips with pitch based on pigment?) on splats. Synthesized, no assets. Risk: could be gimmicky if bad. A well-crafted subtle version: brown noise through lowpass at low gain, gain follows recent motion energy; drop events trigger a soft "plip" (sine osc with quick pitch drop + decay). I think it's worth it — with a toggle (default on after first gesture, icon button top-right, using an inline SVG icon — no emoji). I'll implement carefully with smooth parameter ramps to avoid clicks.

Actually, let me weigh scope: fluid sim (~600 lines) + UI + audio (~120 lines) + choreography. It's a lot but I can write it cleanly. Audio adds a memorable dimension. I'll include it but keep it simple and robust (wrapped in try/catch, created lazily on first pointerdown).

- **Cursor**: hide default cursor and show a custom small ring cursor that scales when pressing? A soft dot that shows current pigment color. That's a nice craft touch. Custom cursor div following pointer (transform translate3d), ring with pigment color, mix-blend maybe. On touch devices hide it. Keep default cursor: none on canvas only... but UI buttons need cursor. I'll apply cursor:none on body but show custom cursor everywhere, and it grows over interactive elements? Simpler: custom cursor only over canvas area (which is full screen anyway); UI elements set cursor:pointer and the custom cursor fades when hovering UI (via CSS :hover on parent? JS mouseover checks). I'll do: custom cursor dot always follows; when hovering elements with [data-hover], the dot expands into a ring outline. Manageable.

- **Time-based subtle drift**: skip, idle system covers it.

- **Title interaction**: hovering the title could stir water? Cute but unnecessary.

Let me also make sure: no gradient decorations in UI. Pigment dots are flat colors. Buttons flat with hairlines. Good. Dark bg with paper-white text — high contrast, fine.

**Accessibility**: aria-labels on buttons, keyboard shortcuts, prefers-reduced-motion: reduce idle choreography + no intro animation? I can respect it by skipping intro splats and reducing idle activity. Nice touch.

**Performance**: pause rAF when document hidden. Cap dt at 1/60*? clamp dt to 0.0166*2. Standard.

Now let me write the code carefully. This will be long (~900-1100 lines). Let me draft the architecture:

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1">
<title>SUMI — a fluid pigment study</title>
<link Google Fonts: Fraunces (wght 300..600, ital), IBM Plex Mono (400,500), Noto Serif JP (500)>
<style> ... </style>
</head>
<body>
<canvas id="water"></canvas>
<div class="grain"></div> (maybe not needed if shader grain)
<header class="masthead"> title etc </header>
<div class="palette"> ... </div>
<div class="hint"> ... </div>
<div class="caption"> ... </div>
<button class="sound"> svg icons </button>
<div class="cursor"></div>
<div class="veil"></div> (intro black overlay? Actually canvas bg is already dark; intro handled by UI opacity + timed splats)
<script> everything </script>
</body>
</html>
```

CSS details:

- body: margin 0, background #0b0a08 (deep warm charcoal), overflow hidden, height 100dvh, cursor none (desktop only via media hover:hover).
- canvas: fixed inset 0, w/h 100%.
- .masthead: position fixed top-left, padding clamp. Title: Fraunces, font-weight 300, size clamp(3rem, 8vw, 6.5rem), letter-spacing 0.04em? "SUMI" spaced: maybe letter-spacing .35em uppercase light — elegant. Overline above: mono 10px letterspaced uppercase "墨 — A FLUID PIGMENT STUDY" with hairline. Sub below: Fraunces italic 300, 15px, max-width 34ch, color rgba(232,226,214,.66).
- Vertical kanji on right side: 墨 large (Noto Serif JP), opacity .1, size ~28vh, writing-mode vertical, position right, pointer-events none. Maybe with a thin vertical rule and vertical text "墨絵 · すみ · ink water memory" — nice detail. I'll add right-side vertical caption: writing-mode: vertical-rl; mono? Japanese in mono looks odd; use Noto Serif JP small, letterspaced, opacity .45. Text: "水はすべての動きを覚えている" ("the water remembers every movement")? Keep it: "水は記憶する — the water remembers". Hmm, keep Japanese short: "墨と水" plus english? I'll do vertical text: "墨 · 水 · 記憶" (ink · water · memory). Elegant.

- .palette: fixed bottom-left; label "PIGMENT — 顔料" tiny mono; row of 5 dots (buttons 20px, border-radius 50%, background pigment display color, box-shadow subtle ring when active via outline offset). Then divider, then "still the water" button: mono uppercase 10px letterspaced, color muted, border-bottom hairline on hover. 
- .hint bottom-right: mono 10px, muted; parts separated by "·". Keyboard hints maybe in slightly boxed kbd style? kbd with hairline border, 1px, radius 3px, padding 1px 5px — tasteful.
- .sound top-right: 32px ghost button with inline SVG (speaker with waves / muted). stroke currentColor.
- .cursor: fixed, 10px dot, background: currentPigment, border-radius 50%, pointer-events none, mix-blend-mode: screen, transition transform .18s, plus a trailing ring? Keep single dot with scale on press (1.8) and ring on data-hover (outline ring 28px). Implement ring as ::after border circle scaling in. 

- Intro animations: elements start opacity 0, translateY(8px); JS adds .is-in with staggered transitions. Title letters: wrap each letter in span, stagger transition-delay. I'll do title reveal via clip: each letter span, translateY(110%) → 0 inside overflow hidden mask. Classic editorial reveal — tasteful.

- prefers-reduced-motion: disable transitions/animations.

Media queries: on small screens, shrink title, move vertical kanji hidden or smaller, palette bottom-left smaller, hint hidden or simplified (touch: show "touch to pour").

Now the JS. Let me write it thoroughly and correctly. I'll base the fluid algorithm on the well-known stable fluids GPU implementation, writing my own code.

Key components:

```js
'use strict';
/* ---------- config ---------- */
const isMobile = matchMedia('(pointer: coarse)').matches || innerWidth < 768;
const config = {
  SIM_RES: isMobile ? 96 : 144,
  DYE_RES: isMobile ? 512 : 1024,
  DENSITY_DISSIPATION: 0.8,
  VELOCITY_DISSIPATION: 0.22,
  PRESSURE: 0.8,
  PRESSURE_ITERATIONS: 20,
  CURL: 26,
  SPLAT_RADIUS: 0.23,
  SPLAT_FORCE: 5200,
  HOVER_INTENSITY: 0.14,   // dye multiplier while moving
  POUR_INTENSITY: 0.55,
};
```

Pigments:
```js
const PIGMENTS = [
  { key:'ai', en:'INDIGO', jp:'藍', ui:'#4a63d8', dye:[0.16,0.30,0.92] },
  { key:'shu', en:'VERMILION', jp:'朱', ui:'#e04b2f', dye:[0.98,0.26,0.14] },
  { key:'kin', en:'OCHRE', jp:'金', ui:'#d9a13b', dye:[0.98,0.66,0.18] },
  { key:'midori', en:'JADE', jp:'翠', ui:'#2fae7d', dye:[0.10,0.78,0.48] },
  { key:'tsuki', en:'MOON', jp:'白', ui:'#c9d2e0', dye:[0.82,0.87,0.96] },
];
```
Wait — dye values: when splatting, Pavel multiplies random HSV color by 0.15. His display then shows dye directly. If I splat dye=[0.16,0.30,0.92]*intensity(0.55) → adds ~[0.09,0.17,0.5] per splat at center gaussian; accumulates with overlaps. Display adds background. Should be visible. Might need tuning but reasonable. Actually Pavel's splat: color * 0.15 where V=1 colors → e.g. [0.15,0,0]. And it looks vivid after a few overlapping move-splats. My hover 0.14 multiplier on base ~ similar magnitude. Pour 0.5 stronger. OK.

Also slight per-splat variation: multiply each channel by 0.9+0.2*random.

WebGL boilerplate:

```js
const canvas = document.getElementById('water');
const { gl, ext } = getWebGLContext(canvas);
```

with ext = { formatRGBA, formatRG, formatR, halfFloatTexType, supportLinearFiltering }.

getSupportedFormat(gl, internalFormat, format, type): if supportRenderTextureFormat → return {internalFormat, format}; else fallback (WebGL2: RG16F→R16F→null etc.).

Compile shaders, Program class (with uniforms map).

blit function: fullscreen quad with two triangles via single triangle strip or element array. Standard:
```js
const blit = (() => {
  gl.bindBuffer(gl.ARRAY_BUFFER, gl.createBuffer());
  gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1,-1,-1,1,1,1,1,-1]), gl.STATIC_DRAW);
  gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER, gl.createBuffer());
  gl.bufferData(gl.ELEMENT_ARRAY_BUFFER, new Uint16Array([0,1,2,0,2,3]), gl.STATIC_DRAW);
  gl.vertexAttribPointer(0, 2, gl.FLOAT, false, 0, 0);
  gl.enableVertexAttribArray(0);
  return (target, clear=false) => {
    if (target == null){ gl.viewport(0,0,gl.drawingBufferWidth, gl.drawingBufferHeight); gl.bindFramebuffer(gl.FRAMEBUFFER, null); }
    else { gl.viewport(0,0,target.width,target.height); gl.bindFramebuffer(gl.FRAMEBUFFER, target.fbo); }
    if (clear){ gl.clearColor(0,0,0,1); gl.clear(gl.COLOR_BUFFER_BIT); }
    gl.drawElements(gl.TRIANGLES, 6, gl.UNSIGNED_SHORT, 0);
  };
})();
```
Note: must bindAttribLocation(program, 0, 'aPosition') before linking so attribute 0 is aPosition consistently. I'll do that in Program creation.

FBO creation:
```js
function createFBO(w,h,internalFormat,format,type,filterParam){ ... texParams wrap CLAMP_TO_EDGE ... framebuffer ... return {texture, fbo, width:w, height:h, texelSizeX:1/w, texelSizeY:1/h, attach(id){...}} }
function createDoubleFBO(...){ read/write, swap() }
function resizeFBO / resizeDoubleFBO using copyProgram
```

Shaders (GLSL 100):

baseVertexShader:
```glsl
precision highp float;
attribute vec2 aPosition;
varying vec2 vUv, vL, vR, vT, vB;
uniform vec2 texelSize;
void main(){
  vUv = aPosition * 0.5 + 0.5;
  vL = vUv - vec2(texelSize.x, 0.0);
  vR = vUv + vec2(texelSize.x, 0.0);
  vT = vUv + vec2(0.0, texelSize.y);
  vB = vUv - vec2(0.0, texelSize.y);
  gl_Position = vec4(aPosition, 0.0, 1.0);
}
```

copyShader: output texture2D(uTexture, vUv).
clearShader: `gl_FragColor = value * texture2D(uTexture, vUv);` with uniform float value.

splatShader:
```glsl
precision highp float;
varying vec2 vUv;
uniform sampler2D uTarget;
uniform float aspectRatio;
uniform vec3 color;
uniform vec2 point;
uniform float radius;
void main(){
  vec2 p = vUv - point;
  p.x *= aspectRatio;
  vec3 splat = exp(-dot(p,p)/radius) * color;
  vec3 base = texture2D(uTarget, vUv).xyz;
  gl_FragColor = vec4(base + splat, 1.0);
}
```

advectionShader (with MANUAL_FILTERING define):
```glsl
precision highp float;
precision highp sampler2D;
varying vec2 vUv;
uniform sampler2D uVelocity, uSource;
uniform vec2 texelSize, dyeTexelSize;
uniform float dt, dissipation;
vec4 bilerp(sampler2D sam, vec2 uv, vec2 tsize){
  vec2 st = uv / tsize - 0.5;
  vec2 iuv = floor(st), fuv = fract(st);
  vec4 a = texture2D(sam, (iuv + vec2(0.5,0.5)) * tsize);
  vec4 b = texture2D(sam, (iuv + vec2(1.5,0.5)) * tsize);
  vec4 c = texture2D(sam, (iuv + vec2(0.5,1.5)) * tsize);
  vec4 d = texture2D(sam, (iuv + vec2(1.5,1.5)) * tsize);
  return mix(mix(a,b,fuv.x), mix(c,d,fuv.x), fuv.y);
}
void main(){
#ifdef MANUAL_FILTERING
  vec2 coord = vUv - dt * bilerp(uVelocity, vUv, texelSize).xy * texelSize;
  vec4 result = bilerp(uSource, coord, dyeTexelSize);
#else
  vec2 coord = vUv - dt * texture2D(uVelocity, vUv).xy * texelSize;
  vec4 result = texture2D(uSource, coord);
#endif
  float decay = 1.0 + dissipation * dt;
  gl_FragColor = result / decay;
}
```

divergence, curl, vorticity, pressure, gradientSubtract — standard from the stable fluids GPU pipeline:

divergence:
```glsl
precision mediump float; precision mediump sampler2D;
varying vec2 vUv, vL, vR, vT, vB;
uniform sampler2D uVelocity;
void main(){
  float L = texture2D(uVelocity, vL).x;
  float R = texture2D(uVelocity, vR).x;
  float T = texture2D(uVelocity, vT).y;
  float B = texture2D(uVelocity, vB).y;
  vec2 C = texture2D(uVelocity, vUv).xy;
  if (vL.x < 0.0) L = -C.x;
  if (vR.x > 1.0) R = -C.x;
  if (vT.y > 1.0) T = -C.y;
  if (vB.y < 0.0) B = -C.y;
  float div = 0.5 * (R - L + T - B);
  gl_FragColor = vec4(div, 0.0, 0.0, 1.0);
}
```

curl:
```glsl
float L = texture2D(uVelocity, vL).y;
float R = texture2D(uVelocity, vR).y;
float T = texture2D(uVelocity, vT).x;
float B = texture2D(uVelocity, vB).x;
float vorticity = R - L - T + B;
gl_FragColor = vec4(0.5 * vorticity, 0.0, 0.0, 1.0);
```

vorticity:
```glsl
precision highp float;
varying vec2 vUv, vL, vR, vT, vB;
uniform sampler2D uVelocity, uCurl;
uniform float curl, dt;
void main(){
  float L = texture2D(uCurl, vL).x;
  float R = texture2D(uCurl, vR).x;
  float T = texture2D(uCurl, vT).x;
  float B = texture2D(uCurl, vB).x;
  float C = texture2D(uCurl, vUv).x;
  vec2 force = 0.5 * vec2(abs(T) - abs(B), abs(R) - abs(L));
  force /= length(force) + 0.0001;
  force *= curl * C;
  force.y *= -1.0;
  vec2 velocity = texture2D(uVelocity, vUv).xy;
  velocity += force * dt;
  velocity = min(max(velocity, -1000.0), 1000.0);
  gl_FragColor = vec4(velocity, 0.0, 1.0);
}
```

pressure:
```glsl
precision mediump float;
varying vec2 vUv, vL, vR, vT, vB;
uniform sampler2D uPressure, uDivergence;
void main(){
  float L = texture2D(uPressure, vL).x;
  float R = texture2D(uPressure, vR).x;
  float T = texture2D(uPressure, vT).x;
  float B = texture2D(uPressure, vB).x;
  float divergence = texture2D(uDivergence, vUv).x;
  float pressure = (L + R + B + T - divergence) * 0.25;
  gl_FragColor = vec4(pressure, 0.0, 0.0, 1.0);
}
```

gradientSubtract:
```glsl
precision mediump float;
varying vec2 vUv, vL, vR, vT, vB;
uniform sampler2D uPressure, uVelocity;
void main(){
  float L = texture2D(uPressure, vL).x;
  float R = texture2D(uPressure, vR).x;
  float T = texture2D(uPressure, vT).x;
  float B = texture2D(uPressure, vB).x;
  vec2 velocity = texture2D(uVelocity, vUv).xy;
  velocity.xy -= vec2(R - L, T - B);
  gl_FragColor = vec4(velocity, 0.0, 1.0);
}
```

displayShader:
```glsl
precision highp float;
precision highp sampler2D;
varying vec2 vUv, vL, vR, vT, vB;
uniform sampler2D uTexture;
uniform vec2 texelSize;
uniform vec3 uBackground;
uniform float uTime;

float hash(vec2 p){ return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453); }

void main(){
  vec3 c = texture2D(uTexture, vUv).rgb;
  // soft shading from dye gradients
  vec3 lc = texture2D(uTexture, vL).rgb;
  vec3 rc = texture2D(uTexture, vR).rgb;
  vec3 tc = texture2D(uTexture, vT).rgb;
  vec3 bc = texture2D(uTexture, vB).rgb;
  float dx = length(rc) - length(lc);
  float dy = length(tc) - length(bc);
  vec3 n = normalize(vec3(dx, dy, length(texelSize)));
  float diffuse = clamp(dot(n, vec3(0.0, 0.0, 1.0)) + 0.7, 0.7, 1.0);
  c *= diffuse;

  vec3 col = uBackground + c;

  // gentle filmic curve to keep highlights soft
  col = col / (1.0 + col * 0.22) * 1.18;  // hmm — check math
  ...
}
```
Wait, careful: col/(1+0.22col)*1.18 at col=0 → 0 ✓; at col=1 → 1/1.22*1.18=0.967; at col=3 → 3/1.66*1.18=2.13 (still >1, will clip at display). It softens highs a bit. Fine, or simpler: `col = 1.0 - exp(-col * 1.35);`? That maps 0→0, 1→0.74, 2→0.93 — too compressive for vivid dye; dye often exceeds 1 in accumulations and looks nice glowing. Let me use mild: `col = 1.0 - exp(-col * 1.6);` maps 1→0.80, 2→0.96. Hmm that dims single-layer dye to 0.8. I could pre-multiply dye intensities up. Honestly simplest robust: soft knee only above 1: skip fancy tone map; just clamp naturally (implicit). I'll include a very gentle curve: `col = pow(col, vec3(0.98))`? negligible. 

Decision: skip tone mapping; rely on shading + vignette + grain. Keep display simple and punchy.

Vignette: `float d = distance(vUv, vec2(0.5)); col *= 1.0 - 0.45 * smoothstep(0.45, 0.95, d);` Hmm compute: at center d=0 → 1; at corner d≈0.707 → smoothstep(0.45,0.95,0.707)=~0.5 → *0.775. Slight. Maybe stronger: 0.55 factor. Also vertical subtle darkening at very top/bottom edges? Vignette enough.

Grain: `col += (hash(vUv * vec2(1231.0, 917.0) + fract(uTime)*7.0) - 0.5) * 0.028;` Also maybe grain stronger in darks — fine as is.

Also I want the background not pure flat: add extremely subtle radial warm lift at center: `col += uBackground * ...` skip — vignette creates it.

One more display nicety: dithering to avoid banding in dark bg — the grain covers banding. 

Now sim step function:

```js
function step(dt){
  gl.disable(gl.BLEND);

  curlProgram.bind();
  gl.uniform2f(curlProgram.uniforms.texelSize, velocity.texelSizeX, velocity.texelSizeY);
  gl.uniform1i(curlProgram.uniforms.uVelocity, velocity.read.attach(0));
  blit(curl);

  vorticityProgram.bind();
  ... uVelocity, uCurl, curl=config.CURL, dt
  blit(velocity.write); velocity.swap();

  divergenceProgram.bind(); ... blit(divergence);

  clearProgram.bind();
  gl.uniform1i(uTexture, pressure.read.attach(0));
  gl.uniform1f(value, config.PRESSURE);
  blit(pressure.write); pressure.swap();

  pressureProgram.bind();
  gl.uniform2f(texelSize,...);
  gl.uniform1i(uDivergence, divergence.attach(0));
  for(i<ITERATIONS){ uniform uPressure = pressure.read.attach(1); blit(pressure.write); pressure.swap(); }

  gradienSubtractProgram.bind(); ... blit(velocity.write); velocity.swap();

  advectionProgram.bind();
  gl.uniform2f(texelSize, velocity.texelSizeX, velocity.texelSizeY);
  if(!ext.supportLinearFiltering) gl.uniform2f(dyeTexelSize, velocity.texelSizeX, velocity.texelSizeY);
  let velocityId = velocity.read.attach(0);
  gl.uniform1i(uVelocity, velocityId);
  gl.uniform1i(uSource, velocityId);
  gl.uniform1f(dt, dt);
  gl.uniform1f(dissipation, config.VELOCITY_DISSIPATION);
  blit(velocity.write); velocity.swap();

  if(!ext.supportLinearFiltering) gl.uniform2f(dyeTexelSize, dye.texelSizeX, dye.texelSizeY);
  gl.uniform1i(uVelocity, velocity.read.attach(0));
  gl.uniform1i(uSource, dye.read.attach(1));
  gl.uniform1f(dissipation, config.DENSITY_DISSIPATION);
  blit(dye.write); dye.swap();
}
```

render:
```js
function render(){
  displayProgram.bind();
  gl.uniform2f(texelSize, 1.0/dye.width... ) — actually shading texel size should be dye res
  gl.uniform1i(uTexture, dye.read.attach(0));
  gl.uniform3f(uBackground, r,g,b of bg);
  gl.uniform1f(uTime, time);
  blit(null);
}
```

Background color: I want canvas bg to match page bg #0b0a08 → rgb(11,10,8)/255 = (0.043,0.039,0.031). Pass those.

Splat:
```js
function splat(x, y, dx, dy, color, radius){
  splatProgram.bind();
  gl.uniform1i(uTarget, velocity.read.attach(0));
  gl.uniform1f(aspectRatio, canvas.width/canvas.height);
  gl.uniform2f(point, x, y);
  gl.uniform3f(color, dx, dy, 0);
  gl.uniform1f(radius, correctRadius(radius/100? ...));
```
Pavel: SPLAT_RADIUS config 0.25, then `correctRadius(config.SPLAT_RADIUS / 100.0)`. So radius uniform = 0.0025 base. In shader exp(-dot(p,p)/radius) — with radius 0.0025, sigma² ~0.0025 → radius ~0.05 uv. OK I'll keep same convention: pass radius = config.SPLAT_RADIUS/100 scaled.

Velocity splat then dye splat (two blits: one on velocity with color=(dx,dy,0), one on dye with pigment color).

correctRadius:
```js
function correctRadius(radius){
  const aspect = canvas.width / canvas.height;
  if (aspect > 1) radius *= aspect;
  return radius;
}
```
Hmm wait — in shader p.x *= aspectRatio, which stretches splat horizontally back to circular when aspect>1... Actually if p.x multiplied by aspect (e.g. 2), then distances in x doubled → gaussian narrower in x on screen? uv space: screen width = 1 uv = aspect*height physically. Multiplying p.x by aspect makes gaussian circular in physical space. Then correctRadius multiplies radius by aspect when aspect>1 to keep area. Both together — that's Pavel's approach; keep it.

Pointer handling:

```js
const pointers = new Map(); // pointerId -> {x,y,px,py,dx,dy,down,moved}
canvas listeners on window? Use pointer events on window for move (so dragging outside keeps working), pointerdown on canvas? UI buttons are above canvas; pointerdown on them shouldn't pour. Attach pointerdown to window but check event.target — if target is canvas (or body), start pour. Simpler: attach pointerdown to canvas element; UI has pointer-events auto and sits above, so clicks on UI won't hit canvas. pointermove/up on window.
```

Pointer state per move:
```js
function updatePointer(p, e){
  const w = canvas.clientWidth, h = canvas.clientHeight? use innerWidth/innerHeight
  const x = e.clientX / innerWidth;
  const y = 1 - e.clientY / innerHeight;
  p.dx = (x - p.x) * config.SPLAT_FORCE;
  p.dy = (y - p.y) * config.SPLAT_FORCE;
  p.x = x; p.y = y;
  p.moved = Math.abs(p.dx) > 0 || Math.abs(p.dy) > 0; // always true-ish
}
```
In frame loop, for each pointer with moved: applyInputs → splat with intensity depending on down (pour) vs hover. Hover splats every move event could be too dense; frame-based: mark moved, in frame apply once and reset. That's Pavel's approach — splat once per frame while moving. Good.

Hover intensity scaling: also scale hover dye by pointer speed? Splat force already scales with speed via dx,dy. Dye amount: constant multiplier; maybe scale slightly with speed: `amt = hover * clamp(speed*..., .3, 1)`. Keep constant — simpler, looks fine.

Also throttle hover trail: Pavel splats on every frame while moving — the trail is continuous. Good.

pointerdown: create a "drop": splat with dye intensity pour*1.4, radius slightly larger, velocity (0, -something)? A drop falling: velocity downward in uv = negative y (since y up). Small: dx=0, dy=-120? Actually a tap should just bloom: give tiny random velocity. I'll do: on down, splat with pour intensity and velocity = (rand small, -30) — subtle.

Multi-touch: pointers Map keyed by pointerId; on pointerdown (canvas) add with down=true; on pointerup/cancel remove (or keep for hover? mouse: keep as hover pointer; touch: remove). Distinguish: if e.pointerType === 'mouse' keep pointer with down=false after up; else delete.

Also first pointerdown initializes audio.

Keyboard: keys '1'-'5' select pigment; 'c'/'C' clear (fade). Clear implementation: rather than instant black, run clearProgram with value like 0.0? Instant. Graceful: temporarily boost DENSITY_DISSIPATION for ~1.2s (e.g., set dissipation 6 for a moment) so ink washes away like draining — poetic "still the water". Implement: clearUntil = now + 1000; in step, effectiveDensityDissipation = clearActive ? 8 : config value. Also damp velocity similarly (velocity dissipation 4) so motion calms. Nice.

Idle choreography ("the water dreams"):
```js
let lastInteraction = performance.now();
let nextDream = lastInteraction + 3000;
function dream(now){
  if (now < nextDream || now - lastInteraction < 3500) return;
  if (reducedMotion) { nextDream = now + 8000; return; }
  // choose behavior
  const r = Math.random();
  if (r < 0.55) drip(); else current();
  nextDream = now + 2600 + Math.random()*3200;
}
function drip(){
  const pig = random pigment (maybe weighted to selected?) random any;
  const x = 0.2 + Math.random()*0.6, y = 0.25 + Math.random()*0.5;
  splat(x, y, (Math.random()-0.5)*80, -60 - Math.random()*120, color(pig, 0.35), radius*0.8);
  audio.plink();
}
function current(){
  // a slow stroke: series of splats over time
  schedule 6-10 mini splats along a bezier-ish path using setTimeout or a queue processed in frame loop.
}
```
For currents, I'll implement a simple "strokes" queue: each stroke = {points, i, pig, intensity}; per frame advance 1-2 points, splat with small force along tangent. Path: random start, random angle, arc via slight curvature, length ~0.25–0.45 uv. Intensity low (0.12) — like a ghost hand stirring. Also each stroke point applies force (dx,dy from tangent * force*0.6). This will look like invisible brush strokes — beautiful idle behavior.

Audio design:
```js
const audio = {
  ctx:null, master:null, noise:{src,filter,gain}, enabled:true, started:false,
  start(){ if started return; create AudioContext; master gain 0.0 → ramp to 0.5; 
    noise: bufferSource with generated brown noise loop (2s buffer) → biquad lowpass 220Hz → gain 0.05 → master. Actually water: pink-ish noise through lowpass ~400 with slow LFO on cutoff for wave-like motion.
    Also a very low sine drone 55Hz? Might muddy. Skip drone; noise bed + plinks enough.
  },
  stir(speed){ // called each frame with pointer energy
    target cutoff = 180 + speed*..., target gain = 0.02 + min(speed*...,0.14)
    smooth via setTargetAtTime
  },
  plink(pitch){ // sine osc freq 660*rand → drop to *0.5, gain env 0.12 → 0 over 0.4s, plus a second harmonic
  },
  pour(){ // on pointerdown: slightly bigger plop: lower pitch
  },
  toggle()
}
```
Brown noise generation: 
```js
const len = ctx.sampleRate * 2; buffer; let last=0; for i: white=Math.random()*2-1; last = (last + 0.02*white)/1.02; data[i]=last*3.5;
```
Lowpass filter freq modulated by stir energy + slow LFO (osc 0.07Hz → gain 60 → filter.frequency base 260). Water-ish. Keep gain low (~0.03-0.1). 

plink: 
```js
const t = ctx.currentTime;
osc sine, freq start f (e.g., 520 + Math.random()*500, or pigment-based), exponentialRampToValueAtTime(f*0.55, t+0.35);
gain: 0.0001 → linearRamp 0.08 at t+0.008 → exponentialRamp 0.0001 at t+0.5;
connect via a highpass? fine direct to master.
Also add a tiny triangle an octave up at 0.03 gain for shimmer.
```
Pour (pointerdown): plink with lower f (180–260) and slightly longer.

stir energy: compute pointer speed per frame: sum |dx|,dy|/force → uv speed. Smooth: energy = lerp(energy, speed, 0.1). Map to filter freq 200→900 and noise gain 0.015→0.09. When idle, decays to near-silent. This makes stirring audible — "the water listens". 

Mute toggle: suspend/resume ctx or ramp master to 0. Icon swaps. Default: enabled=true but only starts after first gesture (browser policy). Show icon state accordingly. Also add title/aria-label.

Custom cursor:
```js
const cursorEl; on pointermove update transform via translate. Use rAF-synced lerp for trailing smoothness? A dot that lags slightly (lerp 0.35) feels liquid — nice. Press: scale 2.2 with ring. Over [data-hover] elements: expand ring. Implementation: listen pointerover/out on interactive elements to toggle class. Also set cursor color to current pigment (CSS var --pig). mix-blend-mode: screen so it glows over dye. Hide on touch (pointer: coarse → display none, and body cursor auto).
```
Body cursor none only when (hover:hover) and (pointer:fine). UI buttons also cursor:none then (custom cursor covers). But if custom cursor fails... it's simple enough, fine.

Hint fade: after 12s or after first pour, hint dims to lower opacity? Keep visible but subtle. I'll fade hint in at intro and reduce opacity to 0.55 after first interaction... minor. Keep simple: static after intro.

Pigment selection UI updates: active class, --pig var on :root for cursor, and label showing current pigment name ("藍 INDIGO") next to palette? I'll show a small line under palette label: current pigment in mono, e.g. "INDIGO · 藍". Updates on change. Also pressing number keys updates UI.

Intro sequence code:
```js
const intro = [
  {t:300, fn: revealTitle},
  {t:1000, fn: ()=> drop(0.50, 0.62, 'ai', strong)},  // indigo
  {t:1500, fn: ()=> drop(0.44, 0.70, 'shu')},
  {t:1900, fn: ()=> drop(0.56, 0.66, 'kin')},
  {t:2600, fn: revealUI},
];
```
drop(x,y,pig): sequence of 4 splats descending: for i in 0..3: setTimeout i*40: splat(x + tiny jitter, y - i*0.02, 0, -400, color, radius*1.1). Actually falling drop: start above and move down each frame with downward velocity — the splats themselves placed progressively lower with strong dy. dy negative = downward (uv y up). Force -400*? SPLAT force units: velocity deltas like dx = deltaUV * 5200; a drop velocity ~ -300 (uv/s *?) Hmm velocity texture stores uv/sec-ish; advection: coord = vUv - dt * velocity * texelSize... wait: `vUv - dt * velocity.xy * texelSize` — velocity multiplied by texelSize?? That means velocity is in texels/sec? In Pavel's advection: `vec2 coord = vUv - dt * texture2D(uVelocity, vUv).xy * texelSize;` — yes velocity in "sim texels per second". Splat adds dx = deltaX(uv) * SPLAT_FORCE(6000) to velocity. Sim texelSize = 1/128. So velocity 6000*0.01=60 uv delta → 60 texels/sec at sim res 128 → moves 60/128 uv per sec ≈ 0.47 uv/s. OK so typical velocities ~ hundreds. A falling drop dy = -400 gives fast downward streak. Fine — I'll tune drop with dy ≈ -250 and see (mentally): 250 texels/s at 144 sim = 1.7 uv/s — fast streak. Good for a pour.

For intro drops, make them elegant: radius slightly larger (0.3), dye intensity 0.5, plus a tiny plink sound? Audio can't start before gesture — skip sound in intro (or attempt start on first gesture only). Fine, silent intro.

Also on load, before intro splats, water is still — good contrast.

Title reveal: I'll do letters of "SUMI" each in span with overflow hidden wrapper; CSS .is-in span { transform: none; opacity 1; transition delay per index via inline style --i }. Also the kanji watermark fades in.

Edge: Noto Serif JP font weight — load 400 & 600? Kanji watermark uses weight 400? Use 500. Fonts link:
```
https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,300;0,9..144,400;0,9..144,500;1,9..144,300&family=IBM+Plex+Mono:wght@400;500&family=Noto+Serif+JP:wght@400;500&display=swap
```

Now — the "veil": I want a slightly nicer intro than raw start. Option: start with page bg exactly = canvas bg so canvas blends; UI hidden; then everything choreographed. That's clean. Also a 1px hairline frame around viewport? A thin inset border (like a plate border) could add editorial craft: fixed inset 12px, 1px solid rgba(232,226,214,0.08), pointer-events none. Subtle museum-mat feel. On mobile inset 8px. I like it.

Grain: shader grain animated. Also CSS grain overlay unnecessary.

Let me also handle context loss: canvas.addEventListener('webglcontextlost', prevent default + show message?) — minor; I'll add a simple reload hint. Actually keep minimal: prevent default and try restore? Skip complexity; add listener to display a styled message "the water froze — refresh". Low priority but cheap:
```js
canvas.addEventListener('webglcontextlost', e => { e.preventDefault(); messageEl.show });
```
Eh, I'll skip to control scope. Actually one line with a small overlay is fine... skip.

WebGL unsupported fallback: if !gl → show centered styled message. Simple.

Now, DPI: canvas.width = innerWidth * dpr (dpr = min(devicePixelRatio, 2)). Display blit to null uses drawingBufferWidth. Dye res fixed at DYE_RES regardless — fine.

Resize: 
```js
function resizeCanvas(){
  const w = Math.round(innerWidth * dpr), h = Math.round(innerHeight * dpr);
  if (canvas.width !== w || canvas.height !== h){ canvas.width = w; canvas.height = h; return true; }
  return false;
}
```
In frame loop: if resized → initFramebuffers (with resize preserving dye). initFramebuffers uses resizeDoubleFBO for dye/velocity if they exist.

getResolution(res): Pavel's:
```js
function getResolution(resolution){
  let aspect = gl.drawingBufferWidth / gl.drawingBufferHeight;
  if (aspect < 1) aspect = 1/aspect;
  const min = Math.round(resolution), max = Math.round(resolution * aspect);
  if (gl.drawingBufferWidth > gl.drawingBufferHeight) return {width:max, height:min};
  return {width:min, height:max};
}
```

FBO texel filtering: linear if supported else NEAREST.

Now UI structure detail:

```html
<canvas id="water" aria-label="Interactive ink water — move your pointer to stir"></canvas>
<div class="frame" aria-hidden="true"></div>

<header class="masthead">
  <p class="overline"><span class="kanji-inline">墨</span> A STUDY IN FLUID PIGMENT</p>
  <h1 class="title" aria-label="SUMI">
    <span class="mask"><span style="--i:0">S</span></span>... 
  </h1>
  <p class="sub">Five mineral pigments suspended in dark water.<br>Stir gently — the water keeps every gesture, then forgets.</p>
</header>

<aside class="scroll" aria-hidden="true">
  <span class="scroll-kanji">墨</span>
  <span class="scroll-line"></span>
  <span class="scroll-text">水 · 墨 · 記憶</span>
</aside>

<nav class="palette" aria-label="Pigment selection">
  <p class="palette-label">PIGMENT <span id="pigName">— 藍 INDIGO</span></p>
  <div class="dots"> five buttons </div>
  <button class="still" id="stillBtn">still the water</button>
</nav>

<p class="hint" id="hint">
  <span>move to stir</span><i>·</i><span>press to pour</span><i>·</i>
  <kbd>1</kbd>–<kbd>5</kbd><span>pigment</span><i>·</i><kbd>C</kbd><span>still</span>
</p>

<button class="sound" id="soundBtn" aria-label="Toggle sound" aria-pressed="true"> svg </button>

<div class="cursor" id="cursor" aria-hidden="true"></div>
```

Hint on touch devices: replace content via JS if coarse pointer: "touch to pour · drag to stir". I'll set text conditionally.

Sound icon SVGs: speaker-on:
```svg
<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
 <path d="M11 5 6 9H3v6h3l5 4V5z"/> (speaker)
 <path d="M15.5 8.5a5 5 0 0 1 0 7"/> <path d="M18 6a8.5 8.5 0 0 1 0 12"/>
</svg>
```
Muted: speaker + line through: `<line x1="16" y1="9" x2="21" y2="14"/><line x1="21" y1="9" x2="16" y2="14"/>` (an X). Toggle by swapping two svg elements' display.

CSS palette dots colors from PIGMENTS ui values — I'll hardcode in HTML style attr or CSS. Buttons with aria-label "Indigo pigment" etc.

Now, about avoiding "generated" feel in copy — write it with care:

- overline: "墨 — A STUDY IN FLUID PIGMENT" 
- title: SUMI
- sub: "Five mineral pigments, suspended in dark water. Move slowly: the water keeps every gesture — then forgets it."
- palette label: "PIGMENT" + current name
- still button: "still the water"
- hint: as above
- bottom-right small line? Maybe a timestamp-ish caption "no two moments repeat" — place bottom-center? Might clutter with hint bottom-right. Put it in the vertical scroll aside on the right instead. The right aside: vertical text "水 · 墨 · 記憶" + english small vertical "the water remembers". Keep just Japanese + thin line.

Check contrast: text rgba(233,227,214, x) on #0b0a08 — good.

Title styling: Fraunces 300, font-size clamp(64px, 11vw, 128px), letter-spacing 0.28em (with trailing space issue — add padding-right compensation or text-indent). Use letter-spacing .3em and margin-right -0.3em trick. Color #ece6d8. Maybe mix: "SU" regular + "MI" italic? A single elegant word is better. Add small superscript "墨" after? The overline already has 墨. Keep title pure.

Actually — even more distinctive: title as "S U M I" with the four letters revealed with stagger, and a thin horizontal rule extending from the title to the right edge? Editorial flourish: after title, a hairline that draws itself (scaleX 0→1) — nice motion. I'll add rule under overline or between title and sub: .rule { height:1px; background: rgba(...,0.25); transform-origin left; }.

Layout positions:
- masthead: top: 44px; left: 48px (clamp with vw: clamp(24px, 5vw, 56px)).
- scroll aside: right: 44px, top 50% translateY(-50%), vertical.
- palette: left: 48px, bottom: 44px.
- hint: right: 48px, bottom: 48px.
- sound: top: 44px, right: 44px. Conflicts with scroll aside? Aside is vertically centered; sound top-right corner — fine.

Mobile: masthead top 24 left 24, title smaller; hide scroll aside; palette bottom 24 left 24 (dots smaller); hint: bottom center? Move hint to bottom-right smaller or hide keyboard hints (touch). Sound top right 20.

Now audio + reduced motion + pause on hidden. Also prevent context menu on long-press? touch-action: none on canvas to prevent scroll/zoom gestures interfering. body { overscroll-behavior: none; }.

Also `user-select: none` on UI.

Pointer events: I'll attach:
```js
window.addEventListener('pointerdown', e => { if (e.target.closest('button, nav, .hint, a')) return; ... down })
```
Since canvas is behind UI, pointerdown target = canvas when not on UI. Check `e.target === canvas` — but the .frame overlay and cursor have pointer-events none. scroll aside pointer-events none. So `e.target === canvas` works. But masthead text — should dragging over the title pour ink? Title is text; making it non-interactive (pointer-events none) lets gestures pass through — better UX. Set masthead, hint, scroll: pointer-events: none; keep palette buttons + sound interactive. Then pointerdown handler on window: if target is canvas → pour. pointermove on window: update hover pointer regardless (even over UI? if over UI, maybe still stir lightly — fine, keep stirring; it's charming). Actually when hovering over palette, stirring behind it is fine.

Mouse pointer persists across UI hover — good.

Pointerup: mouse → down=false; touch → delete pointer (and its hover trail ends). Also pointercancel.

Now hover splat: only when pointer moved since last frame; store moved flag & dx dy accumulated. On frame: for each pointer, if moved: 
```js
const intensity = p.down ? POUR : HOVER;
splat(p.x, p.y, p.dx, p.dy, pigmentColor(selected, intensity), radius(p.down? 1 : 0.6));
p.moved = false; p.dx = p.dy = 0? 
```
Pavel keeps dx until applied then resets moved. Deltas recomputed each event. If multiple move events per frame, later deltas overwrite — loses some force; acceptable (Pavel's approach: he accumulates delta? He sets deltaX = x - prevX per event, and moved=true; frame applies once). Fine.

Hover should also work without pressing: yes — HOVER intensity 0.12 dye, radius 0.55x, and force full (dx,dy) so stirring works. Actually hover with full force might churn too much; scale force 0.7 for hover, 1.0 pour.

Energy for audio: from applied deltas: speed = length(dx,dy)/FORCE per frame → uv/frame ~ convert. I'll compute `inst = Math.hypot(p.dx, p.dy) / config.SPLAT_FORCE` (uv moved this frame); energy = max over pointers; smooth.

Plink on pointerdown (pour start) + occasionally on dream drips. Also tiny plink when pigment changes? Cute: soft high tick. Sure — very quiet.

Now let me also double check the "clear/still" behavior: stillBtn click → stillWater(): clearUntil = now+1100; audio: soft low "whoom"? A gentle filtered noise swell downward — implement as plink-like with low freq sine 90Hz quiet? Or noise gain burst with lowpass sweep down. Simple: schedule noiseGain bump + filter freq ramp 600→120 over 0.8s. Nice.

During clear: in step(), dissipation values: density = clearActive? 7 : config; velocity = clearActive? 5 : config. exp(-7*0.016)=0.89 per frame → over 66 frames (1.1s) → 0.89^66 ≈ e^-4.6 ≈ 0.01. 

Also on pigment change via keys/UI: update selected index, UI active states, cursor color var, pigName text.

Now write display background: uBackground = (0.043, 0.039, 0.031)? #0b0a08 → r 11/255=0.0431, g 10/255=0.0392, b 8/255=0.0314. Slightly warmer/darker maybe #0a0908. Keep.

Wait — one issue: page bg (#0b0a08) vs canvas bg from shader: shader outputs uBackground + grain + vignette-darkened. Vignette darkens edges below uBackground, so canvas edges darker than page — but canvas covers whole viewport, so no seam. Frame hairline sits on top. Good.

Also add subtle top-light? skip.

Let me now also consider the "signature moment" beyond intro: the "still the water" drain + the dreaming strokes + sound-on-stir. Plenty.

Potential pitfalls to be careful about:
1. `gl.getExtension('OES_texture_half_float')` null in WebGL1-less case — handle.
2. In WebGL2, formatRG = RG16F requires EXT_color_buffer_float for renderability; getSupportedFormat tests FBO completeness and falls back: RG16F→(fallback RG16F? Pavel tries internalFormat-1?) His code: for WebGL2, formatRGBA=RGBA16F, formatRG=RG16F, formatR=R16F; supportRenderTextureFormat test; if RG16F fails, he falls back to RGBA16F for RG? He has `formatRG = getSupportedFormat(gl, gl.RG16F, gl.RG, halfFloat)` and getSupportedFormat returns null if not renderable, and then... he does fallback chain: if format == null → if internalFormat === gl.R16F? Hmm his code:
```js
function getSupportedFormat(gl, internalFormat, format, type){
  if (!supportRenderTextureFormat(gl, internalFormat, format, type)){
    switch (internalFormat){
      case gl.R16F: return getSupportedFormat(gl, gl.RG16F, gl.RG, type);
      case gl.RG16F: return getSupportedFormat(gl, gl.RGBA16F, gl.RGBA, type);
      default: return null;
    }
  }
  return {internalFormat, format};
}
```
Wait that maps R16F→RG16F→RGBA16F escalation. Yes. I'll include that.
3. Linear filtering of half float: WebGL2 OES_texture_float_linear is for FLOAT; for half float in WebGL2, linear filtering of HALF_FLOAT textures is core? In WebGL2, texture filtering for 16F is supported core (OpenGL ES 3.0 supports linear filtering on half float). Yes — ES 3.0 allows LINEAR on RGBA16F. So supportLinearFiltering = true on WebGL2 always? Pavel checks `gl.getExtension('OES_texture_float_linear')` for WebGL2 — that's for 32F. Half-float linear is core in WebGL2. But Pavel sets supportLinearFiltering = !!OES_texture_float_linear in WebGL2 branch — hmm, that would wrongly report false on devices without float-linear but with half-float-linear (all WebGL2 devices support half-float linear per spec). Actually his code:
```js
if (isWebGL2) { gl.getExtension('EXT_color_buffer_float'); supportLinearFiltering = gl.getExtension('OES_texture_float_linear'); }
```
Hmm that seems off but harmless (he'd use manual filtering unnecessarily). To be correct: in WebGL2, half-float linear filtering is core → supportLinearFiltering = true. I'll set true for WebGL2. (Renderability needs EXT_color_buffer_float; if missing, getSupportedFormat fails → null → we should fallback to... if RGBA16F not renderable in WebGL2 (rare), fallback to WebGL1 path? I'll just show fallback message if formats null. Extremely rare.)

Actually to be safe: if WebGL2 and EXT_color_buffer_float missing, try rendering to half float anyway via test (some browsers support via EXT_color_buffer_half_float). supportRenderTextureFormat test handles it: I test with actual FBO. For WebGL2 I'll test RGBA16F renderability directly; if fails, test RGBA4/RGBA8? Fluid needs >8bit ideally but RGBA8 could work with reduced quality... Pavel doesn't do that; if null he proceeds with... he returns null and code guards `if (!ext.formatRGBA) bloom off`? For simplicity: if formatRGBA null → show graceful error overlay. Rare enough.

4. blit with attribute binding: I must ensure aPosition location 0: call gl.bindAttribLocation(program, 0, 'aPosition') before linkProgram. I'll do in Program constructor.

5. Advection dyeTexelSize uniform only exists when MANUAL_FILTERING defined — guard uniform setting by program.activeUniforms? Setting a non-existent uniform location (null) is silently ignored in WebGL (gl.uniform2f(null,...) generates error? Actually passing null location is a no-op per spec? WebGL: "If location is null, the data passed will be silently ignored and no error generated." Yes, safe.) I'll still guard with the define flag for clarity.

6. iOS Safari: WebGL2 supported since 15; half float render via EXT_color_buffer_float present in WebGL2 iOS 15+. OK. Also devicePixelRatio 3 → cap 2. DYE 512 on mobile.

7. `100dvh` fallback: use height: 100vh with dvh override.

8. Fonts flash: fine with display=swap.

Let me also think about whether to add a very subtle "caustic light" — no, restraint.

One more consideration on aesthetics of dye: to feel like ink not neon, I can slightly desaturate via display shader: mix(col, vec3(luma), 0.08)? Slight. And the shading gives depth. Also DENSITY_DISSIPATION 0.8 might leave persistent murk; combined with the filmic... I'll go 0.85. Velocity dissipation 0.2 keeps swirls long. Curl 25.

Splat radius: hover 0.14 (radius/100), pour 0.28. In config SPLAT_RADIUS 0.24 base; multiply per case.

Dream strokes intensity: dye 0.10, radius 0.5x, force ~ tangent*0.5.

Intro drop: radius 1.2x, dye 0.5, dy -260, plus after drop a "bloom": a second splat same pos with zero velocity, radius 2x, dye 0.25, delayed 250ms — creates a bloom ring feel. Nice.

Alright — also the pigment "MOON" white dye [0.82,0.87,0.96]*0.5 = [0.41,...] — bright silver streaks. 

Let me write out UI copy final:

Hint (fine pointer): `move to stir · press to pour · [1–5] pigment · [C] still` — with kbd tags. 
Touch: `drag to stir · tap to pour`.

Sound button default state: enabled (aria-pressed true) but audio starts on first gesture. Icon shows "on". If user toggles off before start, enabled=false and start() skipped.

Also I should honor `prefers-reduced-motion`: skip intro choreography (show UI immediately, no drops — or a single gentle drop?), disable dream strokes, keep direct manipulation (that's user-initiated, fine). I'll: if reducedMotion → reveal UI at t=0, no auto drops, dream disabled.

Now — writing the actual code. Let me be meticulous. I'll write the whole file now mentally section by section.

HTML skeleton + CSS (~250 lines) + JS (~700 lines). Let me draft.

CSS variables:
```css
:root{
  --paper: #ece6d9;
  --paper-dim: rgba(236,230,217,0.62);
  --paper-faint: rgba(236,230,217,0.38);
  --hairline: rgba(236,230,217,0.14);
  --bg: #0b0a08;
  --pig: #4a63d8;
  --mono: 'IBM Plex Mono', monospace;
  --serif: 'Fraunces', serif;
  --jp: 'Noto Serif JP', serif;
}
```

Title letters: I'll generate spans in HTML directly:
```html
<h1 class="title">
  <span class="mask"><span class="ltr" style="--i:0">S</span></span>
  <span class="mask"><span class="ltr" style="--i:1">U</span></span>
  <span class="mask"><span class="ltr" style="--i:2">M</span></span>
  <span class="mask"><span class="ltr" style="--i:3">I</span></span>
</h1>
```
CSS: .mask{display:inline-block; overflow:hidden; vertical-align:bottom} .ltr{display:inline-block; transform:translateY(115%); transition: transform 1.1s cubic-bezier(.19,1,.22,1) calc(var(--i)*90ms + 200ms)} body.is-in .ltr{transform:none}.

Other reveals: .fade { opacity:0; transform: translateY(10px); transition: opacity .9s ease, transform .9s cubic-bezier(.19,1,.22,1); transition-delay: var(--d, 0ms) } body.is-in .fade{opacity:1; transform:none}.

Assign --d inline: overline 0ms, rule 300ms, sub 500ms, palette 900ms, hint 1100ms, scroll 1200ms, sound 1000ms.

Kanji watermark: .scroll-kanji big; fade with delay.

Frame: .frame{position:fixed; inset:14px; border:1px solid var(--hairline); pointer-events:none; z-index:5} — with intro scaleX? Keep simple fade.

Cursor:
```css
.cursor{position:fixed; left:0; top:0; width:8px; height:8px; border-radius:50%; background:var(--pig); pointer-events:none; z-index:50; mix-blend-mode:screen; transform:translate(-100px,-100px); transition: width .25s, height .25s, opacity .3s; will-change:transform}
```
Hmm transform used for position via JS with translate3d(x,y,0) then centering offset: I'll position with left/top = -4px margin? Use transform = `translate(${x}px,${y}px) translate(-50%,-50%) scale(s)`. Scale via separate var. Manage in JS: cursor.style.transform = ... with scale factor variable; transitions on width/height for ring expansion instead: when hovering interactive → width/height 34px, background transparent, border 1px solid var(--pig). Good: class .cursor.is-link. Press: .cursor.is-down scale via extra inner? Simplify: JS composes scale into transform: scale = down?2.4:1. And is-link changes size/border via CSS. transform transition would lag position... position updates every frame (no transition on transform!). Use two elements: .cursor (position, no transition) containing .cursor-dot (visual, transitions size). 

```html
<div class="cursor"><div class="cursor-dot"></div></div>
```
.cursor{position:fixed; z-index:60; pointer-events:none; left:0; top:0} JS sets transform translate. .cursor-dot{width:7px;height:7px;border-radius:50%;background:var(--pig); box-shadow:0 0 12px 0 color-mix? no — keep flat; margin auto; transition: width .22s ease, height .22s ease, background-color .22s, border-color .22s; border:1px solid transparent}
states: body.cursor-down .cursor-dot{width:16px;height:16px} — hmm scale look: pressed → bigger dot. link hover → .cursor-link .cursor-dot{width:30px;height:30px;background:transparent;border-color:var(--pig)}.
Hide when pointer leaves window (mouseleave on document → opacity 0).
Media (pointer:coarse): display none; body cursor auto.
Body cursor: none on (hover:hover) and (pointer:fine). Also buttons cursor: none inherited? cursor none on * within that media: `@media (hover:hover) and (pointer:fine){ *{cursor:none !important} }` — acceptable.

Palette dots: 
```css
.dots{display:flex; gap:14px; align-items:center}
.dot{width:16px;height:16px;border-radius:50%;border:none;padding:0; position:relative; background:var(--c); opacity:.85; transition: transform .25s cubic-bezier(.34,1.56,.64,1), opacity .2s}
.dot:hover{transform:scale(1.25); opacity:1}
.dot.active{opacity:1; transform:scale(1.15)}
.dot.active::after{content:''; position:absolute; inset:-5px; border:1px solid rgba(236,230,217,.5); border-radius:50%}
```
Wait — dots row with gap 14 and ::after inset -5 overlaps neighbors slightly? -5px ring around 16px dot → ring diameter 26 > gap 14+16... gap 14 means centers 30 apart; ring 26 wide → edges 15 from center — fine, no overlap (neighbor dot edge at 30-8=22 from center... ring at 13 — ok no visual collision).

Focus styles: .dot:focus-visible{outline:1px solid var(--paper-faint); outline-offset:4px}.

Still button:
```css
.still{margin-top:18px; background:none; border:none; padding:2px 0; font:500 10px/1 var(--mono); letter-spacing:.22em; text-transform:uppercase; color:var(--paper-faint); border-bottom:1px solid transparent; transition: color .3s, border-color .3s}
.still:hover{color:var(--paper); border-color:var(--hairline)}
```

Palette label:
```css
.palette-label{font:500 9px/1 var(--mono); letter-spacing:.28em; color:var(--paper-faint); margin-bottom:14px; text-transform:uppercase}
#pigName{color:var(--paper-dim); letter-spacing:.2em}
```

Hint:
```css
.hint{position:fixed; right:clamp(24px,4vw,52px); bottom:clamp(24px,4vw,46px); font:400 10px/1.9 var(--mono); letter-spacing:.14em; color:var(--paper-faint); text-transform:uppercase; text-align:right}
.hint kbd{font:inherit; border:1px solid var(--hairline); border-radius:3px; padding:1px 5px; margin:0 2px; color:var(--paper-dim)}
.hint i{font-style:normal; margin:0 8px; color:rgba(236,230,217,.2)}
```

Masthead:
```css
.masthead{position:fixed; top:clamp(28px,5vh,52px); left:clamp(24px,4.5vw,56px); z-index:10; pointer-events:none; user-select:none}
.overline{font:500 10px/1 var(--mono); letter-spacing:.34em; color:var(--paper-dim); text-transform:uppercase; display:flex; align-items:center; gap:12px}
.overline .kanji-inline{font-family:var(--jp); font-size:13px; color:var(--paper)}
.title{font-family:var(--serif); font-weight:300; font-size:clamp(58px,10vw,124px); line-height:.95; letter-spacing:.22em; margin:18px 0 14px -0.04em; color:var(--paper)}
.rule{width:min(320px,34vw); height:1px; background:linear-gradient? NO — flat: background:var(--hairline); margin:0 0 16px; transform:scaleX(0); transform-origin:left; transition: transform 1.4s cubic-bezier(.19,1,.22,1) .45s}
body.is-in .rule{transform:none}
.sub{font-family:var(--serif); font-style:italic; font-weight:300; font-size:clamp(13px,1.35vw,16px); line-height:1.75; color:var(--paper-dim); max-width:36ch; letter-spacing:.02em}
```
Hmm .rule flat hairline — good (no gradient).

Wait — overline has kanji 墨 + text "A STUDY IN FLUID PIGMENT". With a small horizontal hairline between? Keep gap.

Scroll aside:
```css
.scroll{position:fixed; right:clamp(20px,3.4vw,46px); top:50%; transform:translateY(-50%); display:flex; flex-direction:column; align-items:center; gap:16px; z-index:10; pointer-events:none}
.scroll-kanji{font-family:var(--jp); font-size:clamp(64px,11vh,110px); line-height:1; color:rgba(236,230,217,.10); font-weight:500}
.scroll-line{width:1px; height:56px; background:var(--hairline)}
.scroll-text{writing-mode:vertical-rl; font-family:var(--jp); font-size:11px; letter-spacing:.5em; color:var(--paper-faint)}
```
Note: transform translateY(-50%) conflicts with .fade transform. Give scroll its own reveal (opacity only): .fade-o{opacity:0; transition: opacity 1.2s ease var(--d)} body.is-in .fade-o{opacity:1}. Use fade-o for scroll & kanji watermark.

Sound button:
```css
.sound{position:fixed; top:clamp(24px,4vh,44px); right:clamp(20px,3.4vw,46px); z-index:20; width:38px;height:38px; display:grid; place-items:center; background:none; border:1px solid transparent; border-radius:50%; color:var(--paper-faint); transition: color .3s, border-color .3s}
.sound:hover{color:var(--paper); border-color:var(--hairline)}
.sound svg{width:17px;height:17px}
```
Conflict: scroll aside is at right center; sound top right — ok. But on short screens the kanji might reach top? kanji ~110px + line + text total ~ 300px centered — fine.

Mobile adjustments:
```css
@media (max-width:640px){
  .scroll{display:none}
  .title{font-size:clamp(52px,16vw,80px)}
  .sub{max-width:30ch; font-size:13px}
  .hint{left:24px; right:auto; text-align:left; bottom:calc(24px + 70px)?}
```
Hmm palette bottom-left and hint would collide. On mobile: palette bottom-left; hint — move to bottom above palette? Or hide hint's keyboard parts and place bottom-right small. Palette width ~ 5 dots*16 + gaps ~ 130px. Hint right-bottom with text-align right, max-width 40vw. Let me: mobile hint { right:20px; bottom:28px; max-width:42vw; } palette { left:20px; bottom:24px }. Title area fine. Sound top-right 16px. Frame inset 8px.

Also masthead on mobile top 20 left 20.

Now JS. Full write-up:

```js
(() => {
'use strict';

/* ---------------------------------------------------------- setup */
const canvas = document.getElementById('water');
const reducedMotion = matchMedia('(prefers-reduced-motion: reduce)').matches;
const coarsePointer = matchMedia('(pointer: coarse)').matches;
const dpr = Math.min(window.devicePixelRatio || 1, 2);

const PIGMENTS = [...as above...];
let pigmentIndex = 0;

const config = {...};

/* WebGL context */
function getWebGLContext(canvas){ ... returns {gl, ext} }
const ctx = getWebGLContext(canvas);
if (!ctx) { showFallback(); return; }
const { gl, ext } = ctx;
```

showFallback: create a div with message styled. 

Shader sources as template strings. compileShader helper with error log. Program class:

```js
class Program{
  constructor(vs, fs){
    this.program = createProgram(vs, fs);
    this.uniforms = getUniforms(this.program);
  }
  bind(){ gl.useProgram(this.program); }
}
function createProgram(vs, fs){
  const program = gl.createProgram();
  gl.attachShader(program, vs);
  gl.attachShader(program, fs);
  gl.bindAttribLocation(program, 0, 'aPosition');
  gl.linkProgram(program);
  return program;
}
function getUniforms(program){
  const uniforms = {};
  const count = gl.getProgramParameter(program, gl.ACTIVE_UNIFORMS);
  for (let i=0;i<count;i++){
    const name = gl.getActiveUniform(program, i).name;
    uniforms[name] = gl.getUniformLocation(program, name);
  }
  return uniforms;
}
```

Programs list: copy, clear, splat, advection (with #define maybe), divergence, curl, vorticity, pressure, gradientSubtract, display.

Compile advection with MANUAL_FILTERING if !ext.supportLinearFiltering:
```js
const advectionShaderSource = ext.supportLinearFiltering ? base : '#define MANUAL_FILTERING\n' + base;
```

FBOs:
```js
let dye, velocity, divergence, curl, pressure;
function createFBO(w,h,internalFormat,format,type,filter){
  gl.activeTexture(gl.TEXTURE0);
  const texture = gl.createTexture();
  gl.bindTexture(gl.TEXTURE_2D, texture);
  gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, filter);
  gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, filter);
  gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE);
  gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
  gl.texImage2D(gl.TEXTURE_2D, 0, internalFormat, w, h, 0, format, type, null);
  const fbo = gl.createFramebuffer();
  gl.bindFramebuffer(gl.FRAMEBUFFER, fbo);
  gl.framebufferTexture2D(gl.FRAMEBUFFER, gl.COLOR_ATTACHMENT0, gl.TEXTURE_2D, texture, 0);
  gl.viewport(0,0,w,h);
  gl.clearColor(0,0,0,1); // wait clear needs alpha 0? dye alpha irrelevant; use 0,0,0,0? Pavel clears with 0,0,0,1? He uses clearColor(0,0,0,1)? Hmm his clear uses (0,0,0,1) for pressure etc. For dye, alpha doesn't matter since display reads rgb. Fine either.
  gl.clear(gl.COLOR_BUFFER_BIT);
  return { texture, fbo, width:w, height:h, texelSizeX:1/w, texelSizeY:1/h,
    attach(id){ gl.activeTexture(gl.TEXTURE0+id); gl.bindTexture(gl.TEXTURE_2D, texture); return id; } };
}
```

Double FBO with read/write/swap.

resizeDoubleFBO: create new FBO, copy old read into it via copyProgram blit, set as read; write = fresh; delete old textures? (memory: gl.deleteTexture/Framebuffer — Pavel doesn't bother much; I'll delete properly for craft.)

Actually simpler: implement `resizeFBO(target,w,h,...)` = copyProgram blit old→new; and resizeDoubleFBO uses it for read, creates fresh write. Include deletion of old.

initFramebuffers:
```js
function initFramebuffers(){
  const simRes = getResolution(config.SIM_RES);
  const dyeRes = getResolution(config.DYE_RES);
  const texType = ext.halfFloatTexType;
  const rgba = ext.formatRGBA, rg = ext.formatRG, r = ext.formatR;
  const filtering = ext.supportLinearFiltering ? gl.LINEAR : gl.NEAREST;
  gl.disable(gl.BLEND);
  if (!dye) dye = createDoubleFBO(dyeRes.width, dyeRes.height, rgba.internalFormat, rgba.format, texType, filtering);
  else dye = resizeDoubleFBO(dye, dyeRes.width, dyeRes.height, rgba.internalFormat, rgba.format, texType, filtering);
  if (!velocity) velocity = createDoubleFBO(simRes.width, simRes.height, rg.internalFormat, rg.format, texType, filtering);
  else velocity = resizeDoubleFBO(velocity, simRes.width, simRes.height, rg.internalFormat, rg.format, texType, filtering);
  divergence = createFBO(simRes.width, simRes.height, r.internalFormat, r.format, texType, gl.NEAREST);
  curl = createFBO(...NEAREST);
  pressure = createDoubleFBO(..., gl.NEAREST);
}
```
(divergence/curl/pressure recreated fresh each resize — fine.)

Note: on repeated resizes, old divergence/curl/pressure leak — delete before recreate. I'll add deletes.

Pointer logic:

```js
const pointers = new Map();
let hoverPointer = null; // mouse persistent pointer
```
Simplify: 
```js
function makePointer(){ return {x:-1, y:-1, dx:0, dy:0, down:false, moved:false}; }
const mouse = makePointer();
const touches = new Map();

window.addEventListener('pointerdown', e => {
  if (e.target !== canvas) return;
  audio.unlock();
  const x = e.clientX/innerWidth, y = 1 - e.clientY/innerHeight;
  if (e.pointerType === 'mouse'){
    mouse.down = true; mouse.x = x; mouse.y = y; mouse.dx = 0; mouse.dy = 0;
    pour(x, y);
    document.body.classList.add('is-down');
  } else {
    const p = makePointer(); p.down = true; p.x = x; p.y = y;
    touches.set(e.pointerId, p);
    pour(x, y);
  }
  interacted();
});
window.addEventListener('pointermove', e => {
  const x = e.clientX/innerWidth, y = 1 - e.clientY/innerHeight;
  if (e.pointerType === 'mouse'){
    if (mouse.x < 0){ mouse.x = x; mouse.y = y; return; }
    mouse.dx += (x - mouse.x) * config.SPLAT_FORCE * ... 
```
Hmm accumulate deltas between frames: mouse.dx += (x-mouse.x)*FORCE. Then moved=true. Cap accumulated to avoid explosive force after tab switch: clamp length.

For touch: update corresponding touch pointer similarly (create on move if missing? touch always downs first). 

pointerup/cancel: mouse.down=false; remove class; touches.delete(id).

Also mouse leaving window: pointerout with relatedTarget null → could reset? Fine without.

pour(x,y): 
```js
function pour(x, y){
  const c = pigmentColor(pigmentIndex, config.POUR_INTENSITY * 1.15);
  splat(x, y, (Math.random()-0.5)*60, -140 - Math.random()*80, c, config.SPLAT_RADIUS * 1.6);
  audio.pour();
}
```
Hmm pour with downward velocity — like ink dropped from above. 

Frame input application:
```js
function applyInputs(){
  if (mouse.moved){
    mouse.moved = false;
    const k = mouse.down ? 1 : 0.55;
    const amt = mouse.down ? config.POUR_INTENSITY : config.HOVER_INTENSITY;
    splat(mouse.x, mouse.y, mouse.dx * k, mouse.dy * k, pigmentColor(pigmentIndex, amt), config.SPLAT_RADIUS * (mouse.down ? 1 : 0.55));
    energy = Math.max(energy, Math.hypot(mouse.dx, mouse.dy)/config.SPLAT_FORCE);
    mouse.dx = 0; mouse.dy = 0;
  }
  touches.forEach(p => { if (p.moved){ p.moved=false; splat(p.x,p.y,p.dx,p.dy, pigmentColor(pigmentIndex, config.POUR_INTENSITY*0.8), config.SPLAT_RADIUS*0.9); energy...; p.dx=p.dy=0; } });
}
```

pigmentColor(i, amt): base dye * amt with slight random variation:
```js
function pigmentColor(i, amt){
  const c = PIGMENTS[i].dye;
  const v = 0.85 + Math.random()*0.3;
  return [c[0]*amt*v, c[1]*amt*v, c[2]*amt*v];
}
```

splat(x,y,dx,dy,color,radius):
```js
function splat(x,y,dx,dy,color,radius){
  splatProgram.bind();
  gl.uniform1i(splatProgram.uniforms.uTarget, velocity.read.attach(0));
  gl.uniform1f(splatProgram.uniforms.aspectRatio, canvas.width/canvas.height);
  gl.uniform2f(splatProgram.uniforms.point, x, y);
  gl.uniform3f(splatProgram.uniforms.color, dx, dy, 0);
  gl.uniform1f(splatProgram.uniforms.radius, correctRadius(radius/100));
  blit(velocity.write); velocity.swap();
  gl.uniform1i(splatProgram.uniforms.uTarget, dye.read.attach(0));
  gl.uniform3f(splatProgram.uniforms.color, color[0], color[1], color[2]);
  blit(dye.write); dye.swap();
}
```

Dream system:
```js
let lastInteraction = performance.now();
let nextDream = performance.now() + 4000;
let strokes = []; // active idle strokes
function interacted(){ lastInteraction = performance.now(); }

function dream(now){
  if (reducedMotion) return;
  if (now - lastInteraction < 3200 || now < nextDream) return;
  nextDream = now + 2800 + Math.random()*3600;
  if (Math.random() < 0.6) dreamDrip(); else dreamStroke();
}
function dreamDrip(){
  const i = Math.floor(Math.random()*PIGMENTS.length);
  const x = 0.18 + Math.random()*0.64, y = 0.3 + Math.random()*0.45;
  splat(x, y, (Math.random()-0.5)*50, -90 - Math.random()*120, pigmentColor(i, 0.32), config.SPLAT_RADIUS * 0.9);
  audio.plink(1.4 + Math.random());
}
function dreamStroke(){
  const i = Math.floor(Math.random()*PIGMENTS.length);
  const x0 = 0.15 + Math.random()*0.7, y0 = 0.2 + Math.random()*0.6;
  const ang = Math.random()*Math.PI*2;
  const len = 0.18 + Math.random()*0.3;
  const curve = (Math.random()-0.5)*1.6;
  const n = 14 + Math.floor(Math.random()*10);
  strokes.push({ i, x:x0, y:y0, ang, len, curve, n, t:0, amt: 0.09 + Math.random()*0.05 });
}
function stepStrokes(){
  for (let s of strokes... iterate backwards){
    s.t += 1;
    const f = s.t / s.n;
    if (f >= 1){ strokes.splice(idx,1); continue; }
    const ang = s.ang + s.curve * f;
    const step = s.len / s.n;
    const nx = s.x + Math.cos(ang)*step, ny = s.y + Math.sin(ang)*step;
    splat(nx, ny, Math.cos(ang)*step*config.SPLAT_FORCE*0.65, Math.sin(ang)*step*config.SPLAT_FORCE*0.65, pigmentColor(s.i, s.amt), config.SPLAT_RADIUS*0.5);
    s.x = nx; s.y = ny;
  }
}
```
Velocity magnitude: step ~ 0.3/18 ≈ 0.0167 uv per frame * FORCE*0.65 (5200*0.65=3380) → 56 velocity units — gentle. Good.

Wait — velocity units: dx passed to splat = deltaUV * SPLAT_FORCE. For mouse moving 0.01 uv/frame → 52. Hmm that's much smaller than my drop (-140..-260). Mouse fast move 0.03/frame → 156. OK so drop -140..-260 ≈ fast falling. Fine.

Also dream drip plink only if audio started & enabled.

Clear:
```js
let stillUntil = 0;
function stillWater(){ stillUntil = performance.now() + 1200; audio.still(); interacted(); }
```
In step: 
```js
const stilling = performance.now() < stillUntil;
... gl.uniform1f(advection dissipation, stilling ? 6.5 : config.DENSITY_DISSIPATION) for dye; velocity: stilling ? 4 : config.VELOCITY_DISSIPATION.
```

Keyboard:
```js
window.addEventListener('keydown', e => {
  if (e.repeat) return;
  const k = e.key.toLowerCase();
  if (k >= '1' && k <= '5'){ setPigment(+k - 1); }
  else if (k === 'c'){ stillWater(); }
  else if (k === 'm'){ audio.toggle(); }
});
```
Add M for mute — mention in hint? Hint getting long. Keep hint: move/press/1–5/C. M discoverable via button.

setPigment(i): update index, dots active class, pigName text `— ${jp} ${en}`, cursor var --pig, audio.tick().

Audio implementation (careful):

```js
const audio = {
  ctx: null, master: null, filter: null, noiseGain: null, enabled: true, started: false, energy: 0,
  unlock(){
    if (!this.enabled) return;
    if (!this.started){ this.start(); return; }
    if (this.ctx.state === 'suspended') this.ctx.resume();
  },
  start(){
    try{
      const AC = window.AudioContext || window.webkitAudioContext;
      if (!AC) return;
      this.ctx = new AC();
      const ctx = this.ctx;
      this.master = ctx.createGain();
      this.master.gain.value = 0;
      this.master.connect(ctx.destination);
      this.master.gain.setTargetAtTime(0.9, ctx.currentTime, 1.2);

      // water bed: filtered brown noise
      const len = ctx.sampleRate * 2;
      const buf = ctx.createBuffer(1, len, ctx.sampleRate);
      const data = buf.getChannelData(0);
      let last = 0;
      for (let i=0;i<len;i++){ const white = Math.random()*2-1; last = (last + 0.02*white)/1.02; data[i] = last*3.2; }
      const src = ctx.createBufferSource();
      src.buffer = buf; src.loop = true;
      this.filter = ctx.createBiquadFilter();
      this.filter.type = 'lowpass'; this.filter.frequency.value = 220; this.filter.Q.value = 0.6;
      this.noiseGain = ctx.createGain(); this.noiseGain.gain.value = 0.035;
      src.connect(this.filter).connect(this.noiseGain).connect(this.master);
      src.start();

      // slow swell LFO on the filter
      const lfo = ctx.createOscillator(); lfo.frequency.value = 0.06;
      const lfoGain = ctx.createGain(); lfoGain.gain.value = 70;
      lfo.connect(lfoGain).connect(this.filter.frequency);
      lfo.start();

      this.started = true;
    }catch(e){ /* audio unavailable — stay silent */ }
  },
  stir(dt){ // called every frame with current energy 0..~0.05
    if (!this.started || !this.enabled) return;
    const e = Math.min(1, energy * 14); // energy = uv moved per frame (~0.01 typical, 0.05 fast)
    const t = this.ctx.currentTime;
    this.filter.frequency.setTargetAtTime(200 + e*900, t, 0.12);
    this.noiseGain.gain.setTargetAtTime(0.03 + e*0.10, t, 0.18);
  },
  blip(freq, dur, vol, type='sine'){
    if (!this.started || !this.enabled) return;
    try{
      const ctx = this.ctx, t = ctx.currentTime;
      const osc = ctx.createOscillator(); osc.type = type;
      osc.frequency.setValueAtTime(freq, t);
      osc.frequency.exponentialRampToValueAtTime(freq*0.55, t+dur);
      const g = ctx.createGain();
      g.gain.setValueAtTime(0.0001, t);
      g.gain.exponentialRampToValueAtTime(vol, t+0.012);
      g.gain.exponentialRampToValueAtTime(0.0001, t+dur);
      osc.connect(g).connect(this.master);
      osc.start(t); osc.stop(t+dur+0.05);
    }catch(e){}
  },
  pour(){ this.blip(150+Math.random()*70, 0.5, 0.16); this.blip(420+Math.random()*160, 0.22, 0.05, 'triangle'); },
  plink(p=1){ this.blip((520+Math.random()*420)*p, 0.38, 0.07); },
  tick(){ this.blip(880, 0.09, 0.03, 'sine'); },
  still(){
    if (!this.started || !this.enabled) return;
    const t = this.ctx.currentTime;
    this.filter.frequency.cancelScheduledValues(t);
    this.filter.frequency.setTargetAtTime(110, t, 0.3);
    this.noiseGain.gain.setTargetAtTime(0.09, t, 0.1);
    this.noiseGain.gain.setTargetAtTime(0.03, t+0.9, 0.4);
    this.blip(72, 1.1, 0.12, 'sine');
  },
  toggle(){
    this.enabled = !this.enabled;
    soundBtn.setAttribute('aria-pressed', String(this.enabled));
    soundBtn.classList.toggle('muted', !this.enabled);
    if (this.enabled){ this.unlock(); if (this.started){ this.master.gain.setTargetAtTime(0.9, this.ctx.currentTime, 0.4); } }
    else if (this.started){ this.master.gain.setTargetAtTime(0.0001, this.ctx.currentTime, 0.15); }
  }
};
```
Note exponentialRamp cannot target 0 → use 0.0001. gain.setValueAtTime(0.0001...) fine.

Energy variable shared: I'll keep a module-level `let energy = 0;` decayed each frame: energy *= Math.pow(0.001? use exp decay: energy *= Math.exp(-dt*4). Applied inputs set energy = max(energy, inst).

Sound button icons: two SVGs, toggle .muted class shows muted icon:
```html
<svg class="icon-on">...</svg>
<svg class="icon-off">...</svg>
```
CSS: .sound .icon-off{display:none} .sound.muted .icon-on{display:none} .sound.muted .icon-off{display:block}.

Main loop:

```js
let lastTime = performance.now();
let time = 0;
function frame(now){
  requestAnimationFrame(frame);
  const dt = Math.min((now - lastTime)/1000, 1/30);
  lastTime = now;
  if (document.hidden) return; // hmm rAF doesn't fire when hidden anyway
  time += dt;
  if (resizeCanvas()) initFramebuffers();
  applyInputs();
  stepStrokes();
  dream(now);
  energy *= Math.exp(-dt*3.5);
  audio.stir();
  step(dt);
  render();
}
```
dt clamp 1/30 — when tab returns, big dt clamped. Also lastTime reset on visibilitychange to avoid jump: document.addEventListener('visibilitychange', () => { lastTime = performance.now(); }).

Intro scheduler:
```js
function intro(){
  if (reducedMotion){ document.body.classList.add('is-in'); return; }
  const drops = [
    [1000, 0.50, 0.60, 0, 1.0],
    [1450, 0.435, 0.68, 1, 0.8],
    [1850, 0.565, 0.64, 2, 0.7],
  ];
  drops.forEach(([t,x,y,pi,s]) => setTimeout(() => introDrop(x,y,pi,s), t));
  setTimeout(() => document.body.classList.add('is-in'), 250);
  setTimeout(interacted? no...
}
function introDrop(x, y, pi, s){
  // falling streak
  for (let i=0;i<4;i++){
    setTimeout(() => {
      splat(x + (Math.random()-0.5)*0.004, y - i*0.018, 0, -240 - i*40, pigmentColor(pi, 0.5*s), config.SPLAT_RADIUS * 0.9 * s);
    }, i*45);
  }
  // bloom at rest
  setTimeout(() => splat(x, y - 0.07, (Math.random()-0.5)*20, -10, pigmentColor(pi, 0.28*s), config.SPLAT_RADIUS * 2.2 * s), 220);
}
```
Wait the falling: y decreases (moving down in uv = down screen? uv y up: y - i*0.018 moves down). dy negative = downward velocity. Position starts at y (0.60) and steps down to 0.60-0.054. Then bloom at y-0.07. Hmm bloom below the streak end — like the drop hit and pooled. OK reasonable. Actually a falling drop should leave the streak behind it and pool at the bottom — yes that's what this does.

Also lastInteraction should start at load so dreams don't fire immediately during intro: lastInteraction = now; nextDream = now + 6000.

UI wiring:
```js
const dots = [...document.querySelectorAll('.dot')];
dots.forEach((d,i) => d.addEventListener('click', () => { setPigment(i); audio.unlock(); }));
stillBtn.addEventListener('click', () => { stillWater(); });
soundBtn.addEventListener('click', () => audio.toggle());
```
Note: clicking a dot also triggers window pointerdown? pointerdown target = button ≠ canvas → ignored. Good. But the click on UI should count as interaction? Not necessary.

Cursor JS:
```js
const cursor = document.getElementById('cursor');
let cx = -100, cy = -100, tx = -100, ty = -100;
window.addEventListener('pointermove', e => { tx = e.clientX; ty = e.clientY; }, {passive:true});
```
But I already have a pointermove handler; combine. In frame: cx += (tx-cx)*0.35... but frame might be paused? It runs always. Actually simpler: direct set with slight lerp in rAF — I'll lerp inside main frame loop (always running). cursor.style.transform = `translate3d(${cx}px, ${cy}px, 0)`; dot centered via CSS (dot positioned with translate(-50%,-50%)? .cursor-dot{position:absolute; left:0; top:0; transform:translate(-50%,-50%)} inside cursor container).

Hover detection: elements matching 'button, .dot' → pointerover/out:
```js
document.querySelectorAll('button').forEach(el => {
  el.addEventListener('pointerenter', () => cursor.classList.add('is-link'));
  el.addEventListener('pointerleave', () => cursor.classList.remove('is-link'));
});
```
is-down class on body from pointerdown/up (any). CSS: .is-down .cursor-dot{...}. Also hide cursor until first move (start at -100).

Touch: media query hides cursor and restores cursors.

Also: when pointer over canvas only (not UI), dot small; fine.

Now the display shader — also consider adding very subtle chromatic offset? Skip.

Double-check advection dissipation formula: decay = 1 + dissipation*dt; result/decay. With dissipation 0.85, dt 1/60: decay=1.0142 → per second factor (1+0.85/60)^60 ≈ e^0.85 ≈ 2.34 → dye halves every ~0.8s?? Wait e^-0.85 per second → after 1s dye is 42%. That's fast-ish fade. Pavel default DENSITY_DISSIPATION=1 → 37% per second. His demos look good with that. For lingering ink memory, 0.6 → 55%/s. Hmm but then trails vanish quickly. The "keeps every gesture then forgets" copy suggests moderate persistence. I'll pick 0.7. Velocity 0.22 → slow decay of motion, swirls continue. Curl 26.

Hmm, one more idea for depth: make dye colors slightly "multiply" over time toward their hue? Overkill. Keep.

Pressure iterations 20 at sim res 144 — fine perf-wise (each iteration is cheap at 144p).

Performance estimate: sim 144p (~ 144*aspect x 144), dye 1024. Advection on dye at 1024 with linear filtering — fine on most GPUs. Mobile 512.

getResolution uses gl.drawingBufferWidth — after canvas sized. initFramebuffers called after initial resizeCanvas().

Order of init:
```js
resizeCanvas();
initFramebuffers();
intro();
requestAnimationFrame(frame) with lastTime init.
```
Also gl.clearColor default? Display draws every pixel (blit null covers full screen) so no clear needed.

One catch: blit() binds element array & array buffers once at setup — but other code (none) doesn't touch buffers. Also vertexAttribPointer bound once — fine since single VAO-less setup and no other buffers. But careful: on WebGL2 default VAO exists? WebGL2 has default VAO like WebGL1 — fine.

Another catch: `gl.viewport` set per blit — good.

Half float type in WebGL2: gl.HALF_FLOAT; internal formats RGBA16F etc. In WebGL1: ext.halfFloat = OES_texture_half_float; type = halfFloat.HALF_FLOAT_OES; internalFormat = gl.RGBA (must use unsized), format gl.RGBA. For RG in WebGL1: not available → fallback: use RGBA for RG and R formats. Pavel's getSupportedFormat in WebGL1: formatRGBA = (RGBA, RGBA), formatRG = (RGBA, RGBA), formatR = (RGBA, RGBA) — all RGBA. And supportRenderTextureFormat tests. Implement:

```js
function getWebGLContext(canvas){
  const params = { alpha: false, depth: false, stencil: false, antialias: false, preserveDrawingBuffer: false };
  let gl = canvas.getContext('webgl2', params);
  const isWebGL2 = !!gl;
  if (!gl) gl = canvas.getContext('webgl', params) || canvas.getContext('experimental-webgl', params);
  if (!gl) return null;
  let halfFloatTexType, supportLinearFiltering;
  if (isWebGL2){
    gl.getExtension('EXT_color_buffer_float');
    supportLinearFiltering = true; // half-float linear filtering is core in ES3
    halfFloatTexType = gl.HALF_FLOAT;
  } else {
    const halfFloat = gl.getExtension('OES_texture_half_float');
    if (!halfFloat) return null;
    halfFloatTexType = halfFloat.HALF_FLOAT_OES;
    supportLinearFiltering = !!gl.getExtension('OES_texture_half_float_linear');
  }
  gl.clearColor(0,0,0,1);
  const formatRGBA = isWebGL2 ? getSupportedFormat(gl, gl.RGBA16F, gl.RGBA, halfFloatTexType)
                              : getSupportedFormat(gl, gl.RGBA, gl.RGBA, halfFloatTexType);
  const formatRG  = isWebGL2 ? getSupportedFormat(gl, gl.RG16F, gl.RG, halfFloatTexType) : formatRGBA;
  const formatR   = isWebGL2 ? getSupportedFormat(gl, gl.R16F, gl.RED, halfFloatTexType) : formatRGBA;
  if (!formatRGBA) return null? 
```
Hmm if WebGL2 without EXT_color_buffer_float: RGBA16F not renderable → getSupportedFormat falls through switch (default: return null) → formatRGBA null → then what? Fallback: could try half float via WebGL1-style? Simpler: if !formatRGBA → try creating with gl.FLOAT type? OES_texture_float in WebGL2? Messy. Practical approach: if WebGL2 and !EXT_color_buffer_float, also request 'EXT_color_buffer_half_float' and test. My supportRenderTextureFormat test covers actual capability. If still null → return null → show graceful fallback overlay ("Your browser can't float-render; the water needs it"). Rare (all modern browsers support). Acceptable.

getSupportedFormat with fallback chain:
```js
function getSupportedFormat(gl, internalFormat, format, type){
  if (supportRenderTextureFormat(gl, internalFormat, format, type)) return { internalFormat, format };
  if (isWebGL2){
    switch (internalFormat){
      case gl.R16F: return getSupportedFormat(gl, gl.RG16F, gl.RG, type);
      case gl.RG16F: return getSupportedFormat(gl, gl.RGBA16F, gl.RGBA, type);
      default: return null;
    }
  }
  return null;
}
function supportRenderTextureFormat(gl, internalFormat, format, type){
  const texture = gl.createTexture();
  gl.bindTexture(gl.TEXTURE_2D, texture);
  gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.NEAREST);
  gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.NEAREST);
  gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE);
  gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
  gl.texImage2D(gl.TEXTURE_2D, 0, internalFormat, 4, 4, 0, format, type, null);
  const fbo = gl.createFramebuffer();
  gl.bindFramebuffer(gl.FRAMEBUFFER, fbo);
  gl.framebufferTexture2D(gl.FRAMEBUFFER, gl.COLOR_ATTACHMENT0, gl.TEXTURE_2D, texture, 0);
  const status = gl.checkFramebufferStatus(gl.FRAMEBUFFER);
  return status === gl.FRAMEBUFFER_COMPLETE;
}
```
Need isWebGL2 visible — pass flag or restructure. I'll keep isWebGL2 in closure.

Note: WebGL1 internalFormat must equal format (unsized). Using gl.RGBA both — correct.

alpha:false in context params — canvas opaque, page bg behind irrelevant. Good, avoids blending issues.

Now display shader texelSize: baseVertexShader uses uniform texelSize for varyings vL etc. For display I bind displayProgram and set texelSize = dye texel — used both in vertex (for neighbor varyings) and fragment (for normal z). Same uniform name shared — good.

For pressure/curl etc., set texelSize = velocity texel each bind (Pavel sets per program). Since vertex shader varyings need correct texelSize per pass, set after each program.bind().

Let me now also handle: `blit` clear parameter for pressure init? Not needed (clear program handles).

Potential issue: `velocity.read.attach(0)` then in splat second pass `dye.read.attach(0)` — attach reuses texture unit 0, fine.

Pressure loop: divergence attach(0) once; pressure.read.attach(1) each iteration; blit write; swap. Standard.

Vorticity: uVelocity attach(0), uCurl attach(1).

Gradient subtract: uPressure attach(0), uVelocity attach(1).

Advection: velocity self-advect: uVelocity=uSource=velocity.read.attach(0); then dye: uVelocity=velocity.read.attach(0), uSource=dye.read.attach(1).

Wait — after velocity swap, velocity.read is the advected one. Order in Pavel: curl→vorticity→divergence→pressure→gradient→advect velocity→advect dye. Yes as I wrote.

dt uniform per pass.

Now — the display fragment shader final:

```glsl
precision highp float;
precision highp sampler2D;
varying vec2 vUv;
varying vec2 vL, vR, vT, vB;
uniform sampler2D uTexture;
uniform vec2 texelSize;
uniform vec3 uBackground;
uniform float uTime;

float hash(vec2 p){
  return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453123);
}

void main(){
  vec3 c = texture2D(uTexture, vUv).rgb;

  vec3 lc = texture2D(uTexture, vL).rgb;
  vec3 rc = texture2D(uTexture, vR).rgb;
  vec3 tc = texture2D(uTexture, vT).rgb;
  vec3 bc = texture2D(uTexture, vB).rgb;

  float dx = length(rc) - length(lc);
  float dy = length(tc) - length(bc);
  vec3 n = normalize(vec3(dx, dy, length(texelSize)));
  float diffuse = clamp(dot(n, vec3(0.0, 0.0, 1.0)) + 0.72, 0.72, 1.0);
  c *= diffuse;

  vec3 col = uBackground + c;

  // vignette
  float d = distance(vUv, vec2(0.5, 0.5));
  col *= 1.0 - 0.42 * smoothstep(0.42, 0.92, d);

  // living grain
  float g = hash(vUv * vec2(1613.0, 907.0) + fract(uTime * 0.61) * 43.7) - 0.5;
  col += g * 0.021;

  gl_FragColor = vec4(col, 1.0);
}
```
Grain static per-pixel pattern moving with time — hash of vUv*big + time offset → animated noise. Amplitude 0.021 subtle. Good.

Hmm — grain of ±0.01 on background 0.04 → visible slight shimmer, filmic. OK.

Also maybe slight desaturation to feel mineral: `float lum = dot(col, vec3(0.299,0.587,0.114)); col = mix(col, vec3(lum), 0.06);` — subtle. Include.

Copy check for sub: "Five mineral pigments, suspended in dark water. Move slowly — the water keeps every gesture, then forgets it." Good.

Overline: "墨 · A STUDY IN FLUID PIGMENT".

Hint text final (fine): `move to stir · press to pour · 1–5 pigment · C still the water` with kbds around 1–5 and C. Actually "1–5" as single kbd? `<kbd>1</kbd>–<kbd>5</kbd>`. Fine.

Touch hint: `drag to stir · tap to pour` — set via JS if coarsePointer: hint.innerHTML = 'drag to stir <i>·</i> tap to pour'.

Sound button initial: enabled (not muted). aria-pressed="true".

Fallback overlay for no WebGL:
```js
function fatal(message){
  const el = document.createElement('div');
  el.className = 'fatal';
  el.innerHTML = `<p class="fatal-kanji">墨</p><p>${message}</p>`;
  document.body.appendChild(el);
}
```
CSS .fatal: fixed inset 0 grid place-items center, text center, serif italic paper-dim.

Message: "This piece needs WebGL with floating-point textures — your browser declined. Try a recent Chrome, Firefox or Safari."

Also body.is-in still added so UI shows? If fatal, skip intro. Fine.

Title aria: h1 aria-label="SUMI" with spans aria-hidden. 

Let me reconsider the palette label text: "PIGMENT" + `<span id="pigName">藍 · INDIGO</span>`. On setPigment: pigName.textContent = `${p.jp} · ${p.en}`.

Wait, one more detail — the `.dot` background colors: use PIGMENTS ui hex inline: style="--c:#4a63d8". CSS .dot{background:var(--c)}.

UI hex choices (display colors, slightly lifted for visibility on dark):
- Indigo: #5468d4 (visible) — dye [0.16,0.30,0.92]? That dye renders as fairly saturated blue. UI #4f63d2.
- Vermilion: #d94f33 / dye [0.98,0.26,0.14] → renders bright orange-red. UI #d84a2f.
- Ochre: #d29a3a / dye [0.98,0.66,0.18] → golden. UI #d09a3c.
- Jade: #37b07f / dye [0.10,0.78,0.48]. UI #35ab7c.
- Moon: #c8d0dd / dye [0.82,0.87,0.96]. UI #c8d0dd.

Default pigment: Indigo (index 0). Cursor --pig set to ui of selected.

Hmm — the overall page first impression: dark warm field, big elegant "SUMI" serif, kanji watermark right, palette bottom-left. Then indigo drop blooms. That's a strong, authored look. 

One concern: "SUMI" + Japanese aesthetic — is it pastiche? I think it's respectful and coherent: the whole piece is about ink/water; naming and copy support it. The typography (Fraunces is a Latin serif) with Japanese accents is a common editorial pairing. Fine.

Now — is there anything in my plan that trips my own quality bar?
- No gradients in UI (hairlines flat, dots flat). ✓
- No blue/purple default scheme — palette is curated multi-pigment; default indigo is a deliberate pigment choice, not a Tailwind-blue theme. The page chrome is warm paper on charcoal. ✓
- No emoji; icons are inline SVG. ✓
- No alert/confirm. ✓
- Real interactivity everywhere. ✓
- Distinctive fonts. ✓
- Single memorable concept. ✓
- Signature moments: intro drops, dreaming strokes, sound-of-water. ✓

Let me also double-check pointermove handler combining cursor + fluid:
```js
window.addEventListener('pointermove', e => {
  tx = e.clientX; ty = e.clientY;
  const x = e.clientX / innerWidth, y = 1 - e.clientY / innerHeight;
  if (e.pointerType === 'mouse'){
    if (mouse.x < -0.5){ mouse.x = x; mouse.y = y; return; }  // hmm initial -1 sentinel: use mouse.active flag
    ...
```
Use `mouse.active` flag set on first move. Actually pointerdown sets position too; for mouse, pointerdown might occur before any move? Rare. I'll init mouse.x=-1; on move if mouse.x<0 → set and return.

Delta accumulation:
```js
mouse.dx += (x - mouse.x) * config.SPLAT_FORCE;
mouse.dy += (y - mouse.y) * config.SPLAT_FORCE;
mouse.x = x; mouse.y = y;
mouse.moved = true;
```
Cap: if hypot(dx,dy) > 800 clamp scale (prevents teleport spikes on window re-entry):
```js
const m = Math.hypot(mouse.dx, mouse.dy);
if (m > 1200){ mouse.dx *= 1200/m; mouse.dy *= 1200/m; }
```

Touches: on pointermove for touch pointer: same accumulation (they're always "down"). If pointerId not in map and pointerType touch → ignore (shouldn't happen since down creates).

pointerup: 
```js
window.addEventListener('pointerup', e => {
  if (e.pointerType === 'mouse'){ mouse.down = false; }
  else touches.delete(e.pointerId);
  document.body.classList.remove('is-down');
});
window.addEventListener('pointercancel', e => { touches.delete(e.pointerId); document.body.classList.remove('is-down'); });
```

Multi-touch pinch → two touches splatting — fun. touch-action:none on canvas & body prevents browser gestures. Set html,body{touch-action:none; overscroll-behavior:none}.

Hmm — touch-action none on body also blocks scrolling — page is fixed viewport anyway. OK.

Keyboard focus: buttons reachable via Tab; Enter triggers click → setPigment. Good.

Edge: keydown 'c' while typing? No inputs on page. Fine.

Now — write final CSS with care about z-index: canvas z-0; frame z-5; UI z-10..20; cursor z-60; fatal z-100.

Fonts: preconnect + stylesheet link.

Let me also add `<meta name="theme-color" content="#0b0a08">`.

Title of page: "SUMI · a study in fluid pigment".

Also small favicon via data URI? Nice touch: an SVG circle indigo. 
```html
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'><circle cx='16' cy='16' r='10' fill='%234f63d2'/></svg>">
```
Cheap and polished.

Now assemble everything. Also remember: after the code block, a brief explanation. And start response without a # heading, in English, no leaks about instructions.

Let me now write the complete file carefully, keeping code clean and commented lightly.

Additional careful bits:

1. `blit` — need `gl.bindBuffer` before `vertexAttribPointer`; done once at init. But `createProgram` binds attrib location before link — I must ensure blit's buffer setup happens after context creation. Fine.

2. In `stepStrokes`, iterate copy since splat doesn't mutate strokes. Fine with index loop.

3. `dream` uses performance.now() timing; frame `now` param from rAF is same timebase. ✓.

4. On resize, dye content preserved via copy with linear filtering (if supported) — copyProgram uses baseVertex + copyShader; needs texelSize uniform? copyShader only samples vUv — texelSize uniform in vertex affects vL..vB only, unused. But uniform must be set? Unset uniform defaults 0 — fine.

resizeFBO:
```js
function resizeFBO(old, w, h, internalFormat, format, type, filter){
  const newFBO = createFBO(w, h, internalFormat, format, type, filter);
  copyProgram.bind();
  gl.uniform1i(copyProgram.uniforms.uTexture, old.attach(0));
  blit(newFBO);
  // free old
  gl.deleteTexture(old.texture); gl.deleteFramebuffer(old.fbo);
  return newFBO;
}
function resizeDoubleFBO(old, w, h, ...){
  if (old.width === w && old.height === h) return old;
  const read = resizeFBO(old.read, ...);
  gl.deleteTexture(old.write.texture); gl.deleteFramebuffer(old.write.fbo);
  const write = createFBO(w,h,...);
  return { read, write, width:w, height:h, texelSizeX:1/w, texelSizeY:1/h, swap(){ const t=this.read; this.read=this.write; this.write=t; } };
}
```
DoubleFBO shape: I'll construct via createDoubleFBO returning object with read/write/swap/width/height/texelSizeX/Y. For consistency, resizeDoubleFBO returns same shape.

createDoubleFBO:
```js
function createDoubleFBO(w,h,internalFormat,format,type,filter){
  let fbo1 = createFBO(...), fbo2 = createFBO(...);
  return {
    width:w, height:h, texelSizeX:1/w, texelSizeY:1/h,
    get read(){ return fbo1; }, set read(v){ fbo1 = v; },
    get write(){ return fbo2; }, set write(v){ fbo2 = v; },
    swap(){ const t = fbo1; fbo1 = fbo2; fbo2 = t; }
  };
}
```

5. Deleting divergence/curl/pressure on re-init: track and delete.

```js
function initFramebuffers(){
  ...
  if (divergence){ gl.deleteTexture(divergence.texture); gl.deleteFramebuffer(divergence.fbo); }
  ... same curl; pressure is double: delete both.
}
```
I'll write a small helper deleteFBO(f).

6. The `still` keyboard 'c' + button both call stillWater.

7. `interacted()` also called on pointermove? If user just hovers, dream shouldn't fire — yes, any pointer movement counts as interaction. Call interacted() in pointermove (throttle? it's just a timestamp assignment — cheap).

8. Audio `stir` uses `energy` module var — define before audio object or reference via closure at call time (function body evaluates at call — fine as long as declared with let at module scope before use in execution order; hoisting with let — audio.stir called after declaration anyway).

9. iOS: AudioContext resume within gesture — unlock called on pointerdown → start() creates ctx (state 'running' if in gesture). Also add 'touchend'? pointerdown counts as gesture. OK.

10. `matchMedia('(pointer: coarse)')` — also check 'ontouchstart' fallback. Fine as is.

11. Prevent double-tap zoom on iOS: touch-action none + viewport maximum-scale=1 (some a11y concerns but standard for interactive pieces; I'll use user-scalable=no? Keep maximum-scale=1 — acceptable here given the piece is a full-viewport instrument).

Actually accessibility-wise, blocking zoom is questionable, but for a canvas instrument it prevents gesture conflicts. I'll keep touch-action:none (handles it) and drop maximum-scale to respect pinch-zoom for a11y? Pinch would zoom the page over the canvas... With touch-action none on body, browser pinch-zoom is prevented anyway on touch. Keep viewport standard then (width=device-width, initial-scale=1). Good compromise.

12. `resizeCanvas` uses innerWidth/innerHeight; canvas CSS 100vw/100dvh. Use `document.documentElement.clientWidth` to avoid scrollbar issues — no scrollbars (overflow hidden). innerWidth fine.

13. rAF loop starts immediately; intro splats via setTimeout — if tab hidden during load, timeouts fire with rAF paused → splats queue into texture while no frames — fine, they'll appear on return.

14. Ensure `gl.pixelStorei(gl.UNPACK_ALIGNMENT, 1)`? Not needed for float textures with null data... Pavel sets it? Not necessary here.

15. Blend disabled globally; display writes opaque. ✓

16. For NEAREST filtering on pressure/divergence/curl — correct.

17. Advection MANUAL_FILTERING variant needs dyeTexelSize set for source sampling; for velocity self-advect, dyeTexelSize = velocity texel; for dye pass, dye texel. Handle via uniform set before each blit. In non-manual path, texelSize uniform (vertex + frag) = velocity texel for both passes? Careful: fragment uses `texelSize` for coord scaling: `coord = vUv - dt * velocity * texelSize` — this must be the VELOCITY texel size in both passes (velocity in sim-texels/sec). And vertex texelSize also sim. But sampling uSource (dye at higher res) with vUv — fine, uv-space. So set gl.uniform2f(texelSize, velocity.texelSizeX, velocity.texelSizeY) once for advection program per frame; dyeTexelSize only used in manual path for uSource bilerp: set to dye texel for dye pass, velocity texel for velocity pass. ✓ (Matches Pavel.)

18. Splat radius passed = radius/100 with correctRadius multiplying aspect when >1. My radii: config.SPLAT_RADIUS 0.24 → base 0.0024. Hover 0.55×, pour 1×, drop 1.6×, bloom 2.2×, dream 0.5×. Reasonable.

19. One more visual idea: make hover trail slightly transparent-thin and pour rich — handled via intensity/radius.

20. Title kerning: letter-spacing .22em on uppercase Fraunces light — check "SUMI" width at 124px * ~4 chars * (0.8+0.22)em ≈ 500px — fine.

21. The `.sub` line breaks: use <br> after first sentence? max-width 36ch handles.

22. `--pig` var update: document.documentElement.style.setProperty('--pig', p.ui).

23. pigName initial text set in HTML: 藍 · INDIGO.

24. Dots aria-pressed or aria-current? Use aria-label + .active class; add aria-pressed true/false for state. Fine.

Also — small extra flourish: the overline could have a live "water state" word? Over-engineering; skip.

Let me also reconsider DYE_RES 1024 vs 768: 1024 gives crisper tendrils; modern GPUs handle. Desktop 1024, mobile 512. SIM 144/96. OK.

CURL 26 might make ink too swirly/turbulent; ink is elegant at ~20-30. Keep 26. Vorticity force formula standard.

DENSITY_DISSIPATION: 0.72. VELOCITY_DISSIPATION: 0.24. PRESSURE 0.8, ITER 20.

SPLAT_FORCE 5200.

HOVER_INTENSITY 0.14, POUR_INTENSITY 0.55.

Hmm hover at 0.14 with radius 0.55×0.24/100 — thin faint trail. Pour 0.55 rich. Intro drop 0.5*s with s 1.0/0.8/0.7.

Dream drip amt 0.32 — quite visible; maybe 0.25. Stroke 0.09-0.14 faint. OK.

Bloom splat in introDrop: amt 0.28*s radius 2.2 — soft halo. 

Now, sound default ON might annoy? It's gentle and starts only after user interacts; toggle visible. Acceptable, and it's part of the experience ("the water listens"). Default enabled=true.

Edge: `audio.stir()` when started but ctx suspended (autoplay blocked despite gesture? unlock resumes). Fine.

Write the sound icons:

on:
```html
<svg class="icon-on" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
  <path d="M11 5L6 9H2v6h4l5 4V5z"></path>
  <path d="M15.5 8.5a5 5 0 0 1 0 7"></path>
  <path d="M18.5 5.5a9 9 0 0 1 0 13"></path>
</svg>
```
off:
```html
<svg class="icon-off" ...>
  <path d="M11 5L6 9H2v6h4l5 4V5z"></path>
  <line x1="16" y1="9" x2="22" y2="15"></line>
  <line x1="22" y1="9" x2="16" y2="15"></line>
</svg>
```

Now the fatal CSS:
```css
.fatal{position:fixed; inset:0; z-index:100; display:grid; place-items:center; background:var(--bg); text-align:center; padding:32px}
.fatal-kanji{font-family:var(--jp); font-size:64px; color:rgba(236,230,217,.18); margin-bottom:16px}
.fatal p:last-child{font-family:var(--serif); font-style:italic; color:var(--paper-dim); max-width:40ch; line-height:1.7}
```

Assemble HTML body order: canvas, frame, masthead, scroll, palette, hint, sound, cursor, (fatal appended by JS).

Also add noscript? Minor; skip... actually one line noscript styled message is cheap and thoughtful:
```html
<noscript><div class="fatal"><p class="fatal-kanji">墨</p><p>This piece needs JavaScript — the water cannot move without it.</p></div></noscript>
```

Now write everything out. I'll aim for clean formatting. Also add concise comments in English.

One more check on the vertex shader attribute name 'aPosition' consistent.

Also `getUniforms` — names like uniforms['texelSize'] shared vertex+fragment — single location. ✓

Double-check curl program texelSize: vertex varyings need sim texel. Set for curl, divergence, vorticity, pressure, gradientSubtract, advection: velocity texel. Display: dye texel. Splat/copy/clear: unused (set nothing).

Wait — splat vertex: vUv needed; vL etc. computed with texelSize=0 → vUv±0 — unused in splat fragment. Fine.

Copy: uses vUv only. Clear: vUv only. ✓

Now — the frame loop's `if (document.hidden) return;` — rAF doesn't fire when hidden, so unnecessary; but visibilitychange resets lastTime. Keep both harmless (remove the hidden check, keep visibilitychange handler).

Also handle `window.addEventListener('resize', ...)` — handled per-frame via resizeCanvas() check. Fine.

Blur of tab with audio: ctx keeps playing water bed when tab hidden? rAF stops but audio continues — should suspend on hidden:
```js
document.addEventListener('visibilitychange', () => {
  lastTime = performance.now();
  if (audio.started){ document.hidden ? audio.ctx.suspend() : audio.ctx.resume(); }
});
```
But resume only if enabled — ctx.resume when enabled. If muted, master gain ~0 anyway. Add guard: resume only if audio.enabled. Also on return, if enabled and ctx suspended → resume.

Alright, also the cursor lerp inside frame — but frame returns early never (no hidden check now). ✓

Cursor initial position offscreen: tx=ty=-100; also on pointerleave document → hide: 
```js
document.addEventListener('pointerleave'? use document.documentElement mouseleave: cursor.style.opacity=0; mouseenter → 1.
```
Simpler: on pointermove set opacity 1 once. And `window blur` hide. Minor; implement mouseleave on document:
```js
document.addEventListener('mouseleave', () => cursor.style.opacity = '0');
document.addEventListener('mouseenter', () => cursor.style.opacity = '1');
```
mouseenter on document fires? Use document.documentElement.addEventListener('mouseleave'...). I'll attach to window 'mouseout' with !relatedTarget check... Keep simple: window.addEventListener('blur') hide; pointermove shows. Plus initial opacity 0 until first move. Good enough:
```js
let cursorShown = false;
in move handler: if(!cursorShown){cursor.style.opacity='1'; cursorShown=true;}
window.addEventListener('blur', () => { cursor.style.opacity = '0'; cursorShown = false; });
```

is-down class: add on pointerdown (canvas only? any press should feedback — any pointerdown on window). Add on window pointerdown, remove on up. But pressing UI buttons also scales dot — fine, nice feedback.

is-link: pointerenter/leave on all buttons (dots, still, sound).

Now finalize pigment dye values with a bit more thought for how they render additively:

- Indigo dye [0.16, 0.30, 0.92] — renders strong blue. ✓
- Vermilion [0.98, 0.24, 0.13] ✓
- Ochre [0.99, 0.64, 0.16] ✓
- Jade [0.08, 0.75, 0.46] ✓
- Moon [0.80, 0.86, 0.97] ✓

Variation multiplier per splat: v per splat (not per channel) — per channel gives nicer color shimmer: v_i = 0.85+rand*0.3 per channel. I'll do per channel.

Also — a subtle idea: after long idle (say 45s+ of no interaction), do a bigger "event": a triple drop like intro, so a screen left alone keeps composing beautifully. The dream system with drips+strokes every ~3-6s already composes. Add: every ~7th dream is a "trio" — three drips in a loose diagonal. Simple: in dream(), 15% chance → dreamTrio(): 3 drips staggered via strokes-like queue or setTimeout. I'll add setTimeout-based trio. Nice.

Also cap total strokes length (avoid runaway): if strokes.length > 4 skip new.

I think the design is complete. Let me also sanity check the pressure clear value: clearProgram: `gl_FragColor = value * texture2D(uTexture, vUv);` with value=0.8 → multiplies existing pressure — standard.

Write final code now. I'll be careful with GLSL string escaping (template literals fine).

Also — `precision mediump float` in some fragment shaders (divergence, pressure, gradient, curl) as Pavel does — mediump fine for those; keep highp where needed (vorticity uses highp in his). I'll mirror: divergence mediump, curl mediump, pressure mediump, gradient mediump, vorticity highp, advection highp, splat highp, display highp, copy/clear mediump.

One subtle bug risk: in WebGL1, `precision highp sampler2D`? Not valid in GLSL 100? `precision highp sampler2D` isn't a thing in ES 1.00? Actually precision qualifiers apply to float/int only... In ES 1.00, you can declare `precision mediump sampler2D`? Hmm — sampler precision: GLSL ES 1.00 does NOT allow precision qualifiers on sampler2D? Actually it does: "precision qualifier can be applied to... sampler types"? Let me recall Pavel's shaders: his advection has `precision highp float; precision highp sampler2D;` — yes he includes that and it compiles in WebGL1 (sampler2D precision is allowed in ES 1.00? In GLSL ES 1.00, sampler2D has default lowp and precision statements are allowed for opaque types? I believe `precision highp sampler2D;`... hmm, actually GLSL ES 1.00 spec: precision qualifiers apply to int, float and sampler types — yes, samplers can have precision qualifiers (lowp default for sampler2D). It's valid.) Keep as Pavel-style; safe.

For WebGL2 compiling GLSL 100 shaders — allowed. ✓

Now, sizes: SIM_RES 144 → getResolution returns max rounded by aspect; e.g. 16:9 → 256x144. DYE 1024 → 1820x1024? That's ~1.9M texels dye — fine.

Hmm wait, getResolution(res): min = res, max = res*aspect. For ultrawide 21:9 dye = 2380x1024 ≈ 2.4M — still OK.

Mobile portrait: aspect <1 → inverted: width=min? For portrait, drawingBufferWidth<height → return {width:min,height:max} where aspect=height/width. E.g. 390x844 → aspect 2.16 → sim: width 96*? min=96, max=208 → portrait: width=min? drawingBufferWidth < height → {width:min(96)? no wait: width:max? Pavel: `if (gl.drawingBufferWidth > gl.drawingBufferHeight) return { width: max, height: min }; else return { width: min, height: max };` Portrait → width=min=96, height=max=208. ✓

Alright. Also the initial `gl.viewport` in createFBO sets viewport — harmless.

Potential issue: createFBO binds texture to TEXTURE0 and leaves it; attach() manages active units later. ✓

Let me also make sure the intro's first paint isn't pure black-empty awkward: UI reveals at 250ms (overline+title animating in), first drop at 1000ms. Good pacing.

Also add `body{background:var(--bg)}` so pre-canvas paint matches.

Font loading: title uses Fraunces 300 — ensure requested: family=Fraunces:ital,opsz,wght@0,9..144,300;0,9..144,400;1,9..144,300 — include italic 300 for sub, regular 300/400. Also 500 for maybe still button? Button uses mono. OK: Fraunces `0,9..144,300;0,9..144,400;1,9..144,300`.

IBM Plex Mono 400;500. Noto Serif JP 400;500 — Noto Serif JP is a big font; only used for 墨/水/記憶 glyphs + fallback. Google Fonts serves subsetted via unicode-range — fine.

Let me write the final HTML now, mentally proofreading as I go.

Also: the `.overline` uses flex with gap; include a tiny 24px hairline before text? `.overline::before{content:''; width:24px; height:1px; background:var(--hairline)}` — nice detail.

Hint content with separators `<i>·</i>`.

Palette label: `PIGMENT — <span id="pigName">藍 · INDIGO</span>` — em dash spacing.

Wait: palette-label is uppercase via CSS; Japanese unaffected. pigName letterspacing .2em.

Now, code order in <script>:
1. helpers/DOM refs
2. constants (pigments, config)
3. WebGL context + ext
4. shader sources
5. compile programs
6. blit
7. FBO helpers + initFramebuffers
8. simulation functions (step, render, splat, correctRadius)
9. pointers/input
10. dream system
11. audio
12. UI wiring (pigments, still, sound, cursor, keyboard)
13. intro
14. main loop + start

Also guard entire script: if (!gl) fatal(...) & skip rest — wrap in function main() and early return.

Let me carefully write `step(dt)` with stilling adjustments:

```js
function step(dt){
  gl.disable(gl.BLEND);
  const now = performance.now();
  const stilling = now < stillUntil;
  const velDiss = stilling ? 4.0 : config.VELOCITY_DISSIPATION;
  const dyeDiss = stilling ? 7.0 : config.DENSITY_DISSIPATION;

  curlProgram.bind();
  gl.uniform2f(curlProgram.uniforms.texelSize, velocity.texelSizeX, velocity.texelSizeY);
  gl.uniform1i(curlProgram.uniforms.uVelocity, velocity.read.attach(0));
  blit(curl);

  vorticityProgram.bind();
  gl.uniform2f(vorticityProgram.uniforms.texelSize, velocity.texelSizeX, velocity.texelSizeY);
  gl.uniform1i(vorticityProgram.uniforms.uVelocity, velocity.read.attach(0));
  gl.uniform1i(vorticityProgram.uniforms.uCurl, curl.attach(1));
  gl.uniform1f(vorticityProgram.uniforms.curl, config.CURL);
  gl.uniform1f(vorticityProgram.uniforms.dt, dt);
  blit(velocity.write);
  velocity.swap();

  divergenceProgram.bind();
  gl.uniform2f(divergenceProgram.uniforms.texelSize, velocity.texelSizeX, velocity.texelSizeY);
  gl.uniform1i(divergenceProgram.uniforms.uVelocity, velocity.read.attach(0));
  blit(divergence);

  clearProgram.bind();
  gl.uniform1i(clearProgram.uniforms.uTexture, pressure.read.attach(0));
  gl.uniform1f(clearProgram.uniforms.value, config.PRESSURE);
  blit(pressure.write);
  pressure.swap();

  pressureProgram.bind();
  gl.uniform2f(pressureProgram.uniforms.texelSize, velocity.texelSizeX, velocity.texelSizeY);
  gl.uniform1i(pressureProgram.uniforms.uDivergence, divergence.attach(0));
  for (let i = 0; i < config.PRESSURE_ITERATIONS; i++){
    gl.uniform1i(pressureProgram.uniforms.uPressure, pressure.read.attach(1));
    blit(pressure.write);
    pressure.swap();
  }

  gradientProgram.bind();
  gl.uniform2f(gradientProgram.uniforms.texelSize, velocity.texelSizeX, velocity.texelSizeY);
  gl.uniform1i(gradientProgram.uniforms.uPressure, pressure.read.attach(0));
  gl.uniform1i(gradientProgram.uniforms.uVelocity, velocity.read.attach(1));
  blit(velocity.write);
  velocity.swap();

  advectionProgram.bind();
  gl.uniform2f(advectionProgram.uniforms.texelSize, velocity.texelSizeX, velocity.texelSizeY);
  if (!ext.supportLinearFiltering)
    gl.uniform2f(advectionProgram.uniforms.dyeTexelSize, velocity.texelSizeX, velocity.texelSizeY);
  const velId = velocity.read.attach(0);
  gl.uniform1i(advectionProgram.uniforms.uVelocity, velId);
  gl.uniform1i(advectionProgram.uniforms.uSource, velId);
  gl.uniform1f(advectionProgram.uniforms.dt, dt);
  gl.uniform1f(advectionProgram.uniforms.dissipation, velDiss);
  blit(velocity.write);
  velocity.swap();

  if (!ext.supportLinearFiltering)
    gl.uniform2f(advectionProgram.uniforms.dyeTexelSize, dye.texelSizeX, dye.texelSizeY);
  gl.uniform1i(advectionProgram.uniforms.uVelocity, velocity.read.attach(0));
  gl.uniform1i(advectionProgram.uniforms.uSource, dye.read.attach(1));
  gl.uniform1f(advectionProgram.uniforms.dissipation, dyeDiss);
  blit(dye.write);
  dye.swap();
}
```

render():
```js
function render(){
  displayProgram.bind();
  gl.uniform2f(displayProgram.uniforms.texelSize, dye.texelSizeX, dye.texelSizeY);
  gl.uniform1i(displayProgram.uniforms.uTexture, dye.read.attach(0));
  gl.uniform3f(displayProgram.uniforms.uBackground, 0.043, 0.039, 0.031);
  gl.uniform1f(displayProgram.uniforms.uTime, time);
  blit(null);
}
```

OK. Also `time` accumulates.

Cursor transform: `cursor.style.transform = translate3d(...)`. And is-down scaling via CSS on .cursor-dot using body.is-down. Also is-link.

CSS for cursor dot states:
```css
.cursor{position:fixed; left:0; top:0; z-index:60; pointer-events:none; opacity:0; transition:opacity .4s ease; will-change:transform}
.cursor-dot{position:absolute; left:0; top:0; width:7px; height:7px; border-radius:50%; background:var(--pig); transform:translate(-50%,-50%); transition:width .25s cubic-bezier(.19,1,.22,1), height .25s cubic-bezier(.19,1,.22,1), background-color .25s, border-color .25s; border:1px solid transparent}
body.is-down .cursor-dot{width:18px; height:18px}
.cursor.is-link .cursor-dot{width:34px; height:34px; background:transparent; border-color:var(--pig)}
@media (hover:none), (pointer:coarse){ .cursor{display:none} }
```
And cursor:none media:
```css
@media (hover:hover) and (pointer:fine){ html, body, button, a {cursor:none} }
```
Simpler: `*{cursor:none!important}` inside that media. I'll scope: `@media (hover:hover) and (pointer:fine){ body, button{cursor:none} }` — body covers canvas etc.

Hmm — but if custom cursor is the only cursor and JS fails... acceptable.

Also on touch, body cursor default fine.

Pigment dots HTML:
```html
<div class="dots" role="group" aria-label="Choose a pigment">
  <button class="dot active" style="--c:#4f63d2" data-i="0" aria-label="Indigo pigment" aria-pressed="true"></button>
  <button class="dot" style="--c:#d84a2f" data-i="1" aria-label="Vermilion pigment" aria-pressed="false"></button>
  <button class="dot" style="--c:#d09a3c" data-i="2" aria-label="Ochre pigment" aria-pressed="false"></button>
  <button class="dot" style="--c:#35ab7c" data-i="3" aria-label="Jade pigment" aria-pressed="false"></button>
  <button class="dot" style="--c:#c8d0dd" data-i="4" aria-label="Moon pigment" aria-pressed="false"></button>
</div>
```

setPigment:
```js
function setPigment(i){
  pigmentIndex = i;
  const p = PIGMENTS[i];
  dots.forEach((d, j) => {
    d.classList.toggle('active', j === i);
    d.setAttribute('aria-pressed', String(j === i));
  });
  pigName.textContent = `${p.jp} · ${p.en}`;
  document.documentElement.style.setProperty('--pig', p.ui);
  audio.tick();
}
```

Keyboard: also arrow keys cycle pigment? 1-5 enough.

Now — write the intro reveal for `.rule` handled by body.is-in CSS.

Also: after intro completes (~3s), add class 'settled'? Not needed.

Double-check `dreamTrio`:
```js
function dreamTrio(){
  const baseX = 0.3 + Math.random()*0.4;
  const pis = [Math.floor(Math.random()*5), Math.floor(Math.random()*5), Math.floor(Math.random()*5)];
  [0,1,2].forEach(k => setTimeout(() => {
    const x = baseX + (k-1)*0.07 + (Math.random()-0.5)*0.03;
    const y = 0.35 + Math.random()*0.25;
    for (let i=0;i<3;i++) setTimeout(() => splat(x, y - i*0.02, (Math.random()-0.5)*30, -160, pigmentColor(pis[k], 0.3), config.SPLAT_RADIUS*0.8), i*40);
    audio.plink(1.1 + Math.random()*0.6);
  }, k*420));
}
```

Fine. In dream(): r<0.5 drip; <0.8 stroke; else trio.

Also dream should not fire while stilling active — check now<stillUntil skip.

Now audio.stir called every frame — guard started. energy computed in applyInputs; also strokes could add tiny energy? Skip.

Also: audio.pour on pointerdown — nice plop. audio.plink on dream drips only if started&enabled (blip guards internally). ✓

Sound toggle initial icon: enabled → icon-on shown. muted class toggles.

Also unlock on first pointerdown anywhere (window) not just canvas? If user's first gesture is clicking a pigment dot, audio should start: dots click → audio.unlock() (already). soundBtn click → toggle handles. Canvas pointerdown → unlock. Also keydown → unlock? Add in keydown handler: audio.unlock(). Good.

Now — final review of the advection shader for WebGL1 highp sampler2D — fine.

One more possible issue: on WebGL1 without linear filtering (rare), NEAREST advection with manual bilerp — implemented via define. ✓

Also `ext.supportLinearFiltering` for WebGL2 set true — but what if WebGL2 context returns null for EXT_color_buffer_float AND device doesn't render 16F → formatRGBA null → fatal message. Fine.

Hmm, also in WebGL2, `gl.RG16F` etc. constants exist. In the fallback switch inside getSupportedFormat referencing gl.R16F etc. — need isWebGL2 guard to avoid undefined constants in WebGL1 (gl.R16F undefined in WebGL1 — comparing internalFormat (gl.RGBA) to undefined → no match → default → null). Safe.

Let me also decide DYE_RES desktop: 1024. If devicePixelRatio high & 4K screen, dye 1024 upscaled — soft but fine (ink is soft anyway).

Edge: `canvas.width/canvas.height` for aspectRatio in splat uses drawing buffer size — ✓.

Now — the copy for hint on coarse pointers: 
```js
if (coarsePointer) hint.innerHTML = 'drag to stir <i>·</i> tap to pour';
```

Also title `SUMI` — hmm should I include a thin "the" or subtitle word? Keep.

I also want to add one subtle typographic detail: the title's "I" could be vermilion? A single accent — e.g., last letter colored with current pigment? That ties UI to state: title letters paper, but the period/kanji accent... Let me color the inline kanji in overline with var(--pig) — it updates when pigment changes, a living detail. `.overline .kanji-inline{color:var(--pig)}` — indigo initially. Nice touch, restrained.

Hmm wait — is --pig on :root updated by setPigment — yes.

Also cursor dot uses --pig. Dots use their own --c.

Final check of masthead z vs canvas: masthead pointer-events none so dragging over title stirs water behind — delightful.

The scroll aside pointer-events none too.

Frame pointer-events none.

Everything set. Let me also handle `contextmenu` long-press on touch: canvas{-webkit-user-select:none; -webkit-touch-callout:none}. Add user-select none globally.

Now write it all. I'll produce the final file (~850 lines). Let me write with care, then a brief explanation after.

Also remember: response must not start with a heading; start with a short sentence about what I built, then code, then explanation. Language: English.

Let me write the GLSL strings exactly.

baseVertexShader:
```glsl
precision highp float;
attribute vec2 aPosition;
varying vec2 vUv;
varying vec2 vL;
varying vec2 vR;
varying vec2 vT;
varying vec2 vB;
uniform vec2 texelSize;
void main () {
    vUv = aPosition * 0.5 + 0.5;
    vL = vUv - vec2(texelSize.x, 0.0);
    vR = vUv + vec2(texelSize.x, 0.0);
    vT = vUv + vec2(0.0, texelSize.y);
    vB = vUv - vec2(0.0, texelSize.y);
    gl_Position = vec4(aPosition, 0.0, 1.0);
}
```

All good. Time to write the final answer. I'll keep comments concise. Also double-check no stray identity/system references.

One more thought on the title size vs mobile: clamp(56px, 15vw, 124px)? At 390px → 58px, letter-spacing .22em → width ≈ 4*58*1.02 ≈ 236px fits. OK use clamp(54px, 14vw, 122px).

Sub font: clamp(13px, 1.3vw, 16px).

Let me also confirm hint doesn't overlap palette on narrow: mobile hint max-width 40vw right side; palette left. OK.

Sound button on mobile top-right 14px; scroll hidden.

Also masthead left on mobile 22px top 22px.

Frame inset mobile 8px.

Write CSS carefully. Also `.palette{position:fixed; left:clamp(24px,4.5vw,56px); bottom:clamp(26px,5vh,46px); z-index:10}`.

Also add slight text-shadow? No.

Alright — also the "still the water" id="stillBtn".

Also `#hint kbd` styling.

Final: write answer.

Length: the file is long; that's expected and fine.

Let me also double check `blit` initial setup executes after programs compiled (needs gl only). Order: context → shaders/programs → blit setup → framebuffers → events → loop.

Also careful: `gl.bindAttribLocation` before link — in createProgram ✓.

`compileShader(type, source)` with error throw + console.error; if a shader fails the piece breaks — but these are tested-standard shaders.

Also for WebGL1, `gl.RG` etc not used. ✓

In display shader I use `varying vec2 vL...` — vertex provides. ✓

hash function precision on some mobile GPUs — sin-based hash fine.

Also, IMPORTANT: In the fragment shaders using vL/vR/vT/vB (divergence, curl, pressure, gradient, display, vorticity) — vertex texelSize must be set. I do. ✓

For splat program fragment: uses vUv only. ✓

Edge case: `pressure.read.attach(1)` inside loop — attach binds texture unit 1 each iteration; divergence stays unit 0. ✓

`gradientProgram` uniforms named uPressure/uVelocity ✓.

Now the JS for audio.still uses this.filter possibly null if start failed — guard started flag. ✓

Also `audio.toggle` when never started & enabling → unlock starts it. When disabling before start: enabled=false; start skipped later since unlock checks enabled. ✓ unlock(): `if (!this.enabled) return;` ✓

Keyboard 'm' → audio.toggle() — also update button UI (toggle does). ✓

visibilitychange resume guard: `if (!document.hidden && audio.enabled && audio.started) audio.ctx.resume();`

OK. Also add `canvas.addEventListener('webglcontextlost', e => e.preventDefault())` — prevents weird states; without restore handler the piece freezes, acceptable... Actually preventing default without restore does nothing useful. Skip entirely.

Also — small polish: `title` hover could show pointer? masthead pointer-events none. fine.

Double-check the intro drop coordinates relative to title position: title top-left; drops at center (0.5, 0.6) — visible in open water right of title. Good.

Also initial `nextDream` set in main after intro: `nextDream = performance.now() + 9000; lastInteraction = performance.now();`

Write final now.

For the explanation after code: brief — concept, the fluid solver, interactions list, sound, craft details. Keep concise (short paragraphs/bullets).

One last naming detail: page `<title>SUMI — a study in fluid pigment</title>`.

Also I realize I should double check `.dot` size 16px might be small tap targets on mobile — bump to 18px and add padding hit area via ::before? Buttons 18px with 8px transparent border? Use width 18, and `box-sizing:content-box; border:6px solid transparent; background-clip:padding-box` — clever: transparent border extends hit area while background-clip keeps color circle. Let me do: .dot{width:12px;height:12px;border:7px solid transparent;background-clip:padding-box;border-radius:50%} → visual 12px circle, hit area 26px. active ring ::after inset:-9px (relative to border box 26px → ring just outside 12px circle: inset should be -(7+? ) Let me compute: ::after positioned inset relative to padding box? ::after inset is relative to the button's padding box (border box minus border). With border 7 transparent, padding box = 12px circle area. inset:-5px → ring 22px diameter around circle — sits within transparent border zone. Good: ::after{inset:-5px}. Hover scale transform on button scales whole incl. border — fine.

Actually simpler: keep width/height 14px + border 6px transparent, background-clip:padding-box. Ring ::after inset -4px.

Gap between dots: centers 14+12=26px apart... gap:10px → 26px spacing, ring 22px — no overlap. OK.

Focus-visible outline offset 3px.

Now finalize everything. Writing the response.

Also — I must not use gradients anywhere in CSS. Check: none used. The vignette/grain are in-shader (that's rendering, not decorative CSS gradient — it's part of the water's lighting; fine and appropriate).

Also ensure no emoji anywhere. ✓ Icons are SVG. ✓

Also the separator "·" is punctuation, fine.

Let me write the code.

Additional micro-decision: `--paper:#ece6d9`.

Also add `::selection` styling? user-select none mostly; skip.

Also I'll add `aria-hidden="true"` to decorative elements.

Final structure done — write it.

Counting the advection shader `dyeTexelSize` uniform: declared always but only used in MANUAL_FILTERING branch — GLSL compiler may optimize it out → uniform location null → guarded by `if (!ext.supportLinearFiltering)` before setting. ✓ (When linear supported, we never set it.)

Similarly `uTime` in display always used. ✓

Write out. Also I'll make sure `main()` invoked and fatal handled before using gl.

Let me draft the full script in final form (being careful about every referenced variable):

Variables: canvas, reducedMotion, coarsePointer, dpr, PIGMENTS, pigmentIndex, config, gl, ext, isWebGL2 (closure), programs, blit, dye/velocity/divergence/curl/pressure, stillUntil, lastInteraction, nextDream, strokes, energy, time, lastTime, mouse, touches, cursor vars, audio, DOM refs (dots, pigName, stillBtn, soundBtn, hint, cursorEl).

Order matters: audio referenced by handlers defined later — define audio object before wiring events. energy defined before audio.stir usage at runtime. ✓

Also `interacted()` defined before use in handlers (function declaration hoisted — I'll use function declarations for most helpers, so hoisting saves me).

I'll use `function` declarations throughout for safety.

Now writing for real. I'll also add a `try{}` around whole init? If shader compile fails, console error + fatal? compileShader throws → catch in main → fatal('...'). Wrap main body in try/catch calling fatal. Good robustness.

Also one more flourish I want to include: document title updates? no.

Estimated final size ~30KB. Good.

Writing the response now. After code: explanation ~10 lines. Also mention controls.

For the intro reveal timing constants, ensure reducedMotion path adds is-in immediately and skips drops.

Also — `hint` element gets class fade with --d 1100ms; body.is-in triggers.

The `.sound` button also fade with --d 1000ms.

Palette fade --d 900ms; scroll fade-o --d 1200ms.

Kanji watermark inside scroll uses scroll-kanji.

OK writing.

Wait — one more check on `.mask` inline-block with letter-spacing: parent h1 letter-spacing .22em applies inside spans; trailing spacing after each letter adds gaps — fine consistent.

h1 line-height .95, masks inline-block — descenders? uppercase no descenders. overflow hidden could clip right edge of letter italic? Not italic. Fine.

Also add `will-change: transform` on .ltr? Minor; skip.

Also for performance add `contain`? skip.

Now, one important last look at the "strokes" step function indices — implement:

```js
function stepStrokes(){
  for (let i = strokes.length - 1; i >= 0; i--){
    const s = strokes[i];
    s.t++;
    if (s.t >= s.n){ strokes.splice(i, 1); continue; }
    const f = s.t / s.n;
    const ang = s.ang + s.curve * f;
    const stepLen = s.len / s.n;
    const nx = s.x + Math.cos(ang) * stepLen;
    const ny = s.y + Math.sin(ang) * stepLen;
    const force = config.SPLAT_FORCE * 0.6;
    splat(nx, ny, Math.cos(ang) * stepLen * force, Math.sin(ang) * stepLen * force, pigmentColor(s.i, s.amt), config.SPLAT_RADIUS * 0.5);
    s.x = nx; s.y = ny;
  }
}
```
stepLen ~0.3/20=0.015; force 3120 → velocity ~47. Gentle drift. ✓

And strokes spawn only when idle; if user interacts mid-stroke, strokes continue briefly — harmless (they're faint). Could clear strokes on interacted() — yes, clear for responsiveness: in interacted(): strokes.length = 0. Good.

Done planning. Write final answer.