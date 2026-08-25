The user wants the most beautiful and stunning single HTML file I can possibly imagine. This is a creative carte blanche. I need to create something truly memorable — a signature piece with real craft.

Let me think about what would be genuinely stunning, not just "AI-generated pretty page". Common AI tells: purple gradient hero, glowing text, generic cards, emoji decorations. I want to avoid all of that.

Ideas for a stunning single HTML file:

1. **A generative art experience** — canvas-based, interactive, alive. Something like flowing particles forming organic structures.
2. **A typographic masterpiece** — huge editorial typography with kinetic type, scroll-driven narrative.
3. **An immersive "digital garden" or "aurora" scene** — WebGL shader-based fluid/aurora.
4. **A "museum of light" concept** — an editorial site about light itself, with a WebGL shader background that responds to cursor.

I think the strongest play: combine editorial typography (real design craft) with an interactive generative canvas centerpiece. A concept gives it soul. Let me pick a concept: **"EPHEMERA" / "LUMEN" / "AURA"** — something about light, time, impermanence.

Concept idea: **"SOLSTICE" — a study of light.** Or maybe better: a fictional digital exhibition called **"ÆTHER"** or **"NOCTURNE"** — an interactive nocturne: night sky, drifting luminous particles like fireflies/dust, elegant serif typography, chapters you scroll through where the scene transforms.

Let me think about what's technically achievable in one file with high polish:

- Custom WebGL shader background? Risky but doable. Alternatively Canvas 2D with careful particle systems can look gorgeous and is more reliable.
- Actually, a really striking approach: **Canvas 2D flow field particles** with additive blending ("lighter" composite), thousands of particles following curl noise, creating silk-like ribbons of light. This is proven to look stunning. Add mouse interaction — particles react to cursor, cursor leaves trails of disturbance.
- Layer on top: refined typography — a display serif (e.g., "Cormorant Garamond", "Fraunces", "Italiana") paired with a mono (e.g., "Space Grotesk" isn't mono... use "IBM Plex Mono" or "JetBrains Mono"). Fraunces is characterful. Cormorant is elegant. Let me go with a distinctive pairing.

Structure/narrative: Make it feel authored — like a piece titled something evocative. Let me write it as **"LUMEN — an elegy for light"** or **"NOCTURNE No. 1"**. 

Actually here's a stronger concept: **"THE SHAPE OF WIND"** or **"BREATHE"** — hmm. Or make it about time: a living clock-piece. 

Let me settle: **"AURELIA — a meditation on impermanence"**. Hmm, or simpler and punchier: **"EPHEMERAL"**.

Design plan:

1. **Opening**: Black (near-black warm charcoal) screen. Centered: a thin line draws itself, then large serif title letters fade/rise in one by one with staggered animation. Small mono caption above/below. Subtle grain overlay for texture (SVG noise). This first impression must land instantly.

2. **The living canvas**: Full-screen flow-field particle system running behind everything throughout. Particles are fine luminous threads (drawn as short line segments from previous position to current) in a restrained palette — not rainbow. Palette idea: deep ink black background (#0a0a0c or warm #0d0b09), particles in warm gold/amber + faint ivory, occasionally a deep ember red. That avoids blue/purple defaults. Amber-on-black feels candlelit, luxurious. Mouse acts as attractor/repulsor; clicking creates a bloom burst.

3. **Scroll journey**: Sections that read like poem stanzas / exhibit plaques:
   - Hero: title
   - Chapter I — "Dust" : text about particles
   - Chapter II — "Flow": 
   - Chapter III — "Stillness"
   - Finale: a signature moment — maybe pressing and holding anywhere "gathers" the light into a sphere that then releases.
   
   Scroll-driven: as you scroll through chapters, the particle system's behavior morphs (flow field parameters change: turbulence, speed, palette temperature). Text blocks positioned asymmetrically (editorial layout, big whitespace, oversized chapter numerals).

4. **Signature moment**: Hold-to-gather interaction — press and hold mouse/touch: particles converge toward cursor forming a dense glowing orb; release: they explode outward in a shockwave. That's memorable and interactive. Also maybe a "constellation" mode... keep scope sane.

5. **Details**: custom cursor (small circle + dot that scales on hover), smooth scroll with lerp (or keep native scroll but animate sections via IntersectionObserver reveals), progress indicator as a thin vertical line with chapter ticks, top-left wordmark, bottom-right coordinates/time readout in mono for that instrument feel. Grain overlay. Vignette.

6. **Typography**: Google Fonts: "Cormorant Garamond" (light italic for poetry) + "Fraunces"? Two serifs may clash. Better: Display serif = "Italiana" (very elegant, high contrast) or "Cormorant Garamond" 300. Mono = "Space Mono" or "IBM Plex Mono". I'll use Cormorant Garamond for display/body-poetry and IBM Plex Mono for labels/HUD. Maybe add "Marcellus" ... no, keep two fonts.

Actually let me reconsider — "Italiana" only has one weight, very chic for the big title. Cormorant Garamond has italics which are beautiful for poetry lines. Could do: Title in Italiana (letterspaced uppercase), poetry in Cormorant Garamond italic, HUD in IBM Plex Mono. Three fonts is okay if disciplined.

7. **Color**: Background #08080a → slightly warm #0b0a08. Ink text: #e8e3d8 (warm ivory). Accent: amber/gold #d4a24e / #e0b15c. Muted: #6b6558. Particle colors sampled between ivory, gold, ember (#c96f3b). Restrained.

Technical implementation details:

**Particle system (Canvas 2D)**:
- ~1200–1800 particles depending on device (scale by area, cap).
- Flow field via pseudo-curl-noise: use layered sine/cosine functions of position+time (cheap, no need for full simplex — though I could inline a small simplex implementation for quality). Inline simplex noise 2D/3D would give much more organic flow. I'll include a compact simplex noise implementation (classic Stefan Gustavson port, ~60 lines) — worth it for beauty.
- Each particle: position, velocity, hue index, life. Force = angle from noise(x*s, y*s, t) mapped to direction. Speed varies. Draw as line from prev to new pos with low alpha, composite 'lighter'. Fade canvas each frame using semi-transparent fillRect with bg color at low alpha (trails!). Trail length controlled by fill alpha (~0.05–0.12).
- Mouse: repulsion/attraction radius; also injects velocity swirl. Hold: strong attraction (gather). Release after gather: radial impulse.
- Behavior states driven by scroll progress: interpolate params {noiseScale, speed, trailFade, paletteShift, drift}. E.g., Chapter "Stillness" slows everything down, longer trails; finale speeds up.

Performance: use `ctx.globalCompositeOperation='lighter'` for drawing strokes; fade pass uses 'source-over' with rgba(bg, alpha). Cap DPR at 1.5–2. Use offscreen? Not necessary.

**Scroll**: Native scroll with body height set by content sections (each 100vh+). IntersectionObserver adds `.in` class for reveal animations (translateY + opacity, staggered via CSS transition-delay). Also track overall scrollY → target behavior params, lerped each frame for smoothness.

Maybe add a subtle parallax on section content? Keep it simple: reveal transitions suffice, plus fixed HUD elements.

**HUD elements**:
- Top-left: wordmark "A U R E L I A" small mono letterspaced + tiny dot accent.
- Top-right: local time ticking (mono) + "N 41°23′ / E 2°10′"-style fake coords? Cute instrument detail. Or session elapsed time. I'll do live clock.
- Right edge: vertical chapter progress rail: thin line, moving marker, chapter roman numerals clickable to scroll.
- Bottom-left: current state readout: "FIELD · TURBULENCE 0.42 / VELOCITY ..." updating live — makes the page feel alive/instrumental. Updates from actual sim params. Nice touch.
- Bottom-right: hint "hold to gather the light" that fades after first use.

**Custom cursor**: dot + trailing ring, lerp follow; grows over interactive elements; hidden on touch devices. Also while holding, ring contracts.

**Intro sequence**: On load: brief black hold → thin horizontal rule expands → title letters rise (clip-path or overflow hidden spans) → captions fade → HUD fades in → canvas fades from pure black to visible. All timed with CSS animations + JS class toggles.

Title: "AURELIA" — letters individually wrapped for stagger. Subtitle: "a study of light in motion" italic serif. Above title small mono: "Nº 01 — GENERATIVE NOCTURNE".

Chapters copy (write real, evocative micro-copy, no lorem):

- Chapter I — DUST: "Every point of light here was born without purpose..." something poetic about ten thousand motes, each obeying a wind it cannot see.
- Chapter II — FLOW: about the invisible field, order without a commander.
- Chapter III — STILLNESS: invitation to stop scrolling, breathe; the field calms.
- COLOPHON/FINALE: "Nothing here repeats. The moment you leave, this exact configuration will never exist again." + credits line "set in Italiana & Cormorant Garamond · rendered live in your browser".

Also a final interactive note: "hold anywhere to gather — release to let go."

Layout per chapter: alternate alignment left/right, huge ghost numeral (outlined text, very low opacity) behind, small mono kicker, serif headline large, italic paragraph max-width ~34ch, thin rule accents. Generous whitespace. Avoid card grids entirely.

**Grain**: SVG feTurbulence data-uri as fixed overlay with low opacity + mix-blend overlay, plus slight animation? Animated grain via steps() background-position shifts. Keep opacity ~0.05.

**Vignette**: radial-gradient fixed overlay — wait, I'm cautious about gradients as decoration, but a vignette is functional atmosphere, extremely subtle darkening at edges — that's fine, it's not a decorative color gradient banner. I'll keep it barely-there. Similarly the canvas trails produce natural glow via 'lighter' blending — earned, not bolted-on.

**Reduced motion**: respect prefers-reduced-motion — reduce particle counts/speed, disable auto animations. Good craft signal.

**Resize handling**, **visibility pause** (pause rAF when tab hidden).

Let me now think about the noise implementation. Compact simplex 2D + time as third dimension — easier: use 3D simplex (x, y, t). I'll write a standard compact 3D simplex noise. It's long-ish (~100 lines) but reliable. Alternative: value noise with smoothing — cheaper to write but less organic. I'll include a well-known compact 3D simplex (Gustavson/Jonas Wagner style). Let me write it carefully from memory:

```js
// Simplex 3D noise
const grad3 = [[1,1,0],[-1,1,0],[1,-1,0],[-1,-1,0],[1,0,1],[-1,0,1],[1,0,-1],[-1,0,-1],[0,1,1],[0,-1,1],[0,1,-1],[0,-1,-1]];
```
perm table built from seeded shuffle. Then standard algorithm. I remember the structure well enough to reproduce correctly. Let me be careful with F3=1/3, G3=1/6.

Actually, to reduce risk of bugs, I can implement 2D simplex and simulate temporal evolution by rotating/morphing offsets: sample noise at (x*cos(t)+..., ...) — meh. Cleaner trick: use 2D noise but offset domain over time in a circular path: n(x,y,t) = noise2(x + cx(t), y + cy(t)) where cx,cy move slowly — but that translates the whole field uniformly, looks like drifting rather than evolving. Better: two octaves: n = noise2(x*s + t*a, y*s) * w1 + noise2(x*s - t*b, y*s + 50) ... still translation-y.

Honestly the 3D simplex is the right tool and I know it well. I'll write it carefully. Standard implementation (Jonas Wagner's simplex-noise.js style):

```js
class SimplexNoise {
  constructor(random=Math.random){
    this.p = new Uint8Array(256);
    for(let i=0;i<256;i++) this.p[i]=i;
    // shuffle
    for(let i=255;i>0;i--){ const n=Math.floor(random()*(i+1)); [this.p[i],this.p[n]]=[this.p[n],this.p[i]]; }
    this.perm = new Uint8Array(512); this.permMod12=new Uint8Array(512);
    for(let i=0;i<512;i++){ this.perm[i]=this.p[i&255]; this.permMod12[i]=this.perm[i]%12; }
  }
  noise3D(xin,yin,zin){
    const permMod12=this.permMod12, perm=this.perm;
    const grad3=SimplexNoise.grad3;
    const F3=1/3, G3=1/6;
    let n0,n1,n2,n3;
    const s=(xin+yin+zin)*F3;
    const i=Math.floor(xin+s), j=Math.floor(yin+s), k=Math.floor(zin+s);
    const t=(i+j+k)*G3;
    const X0=i-t, Y0=j-t, Z0=k-t;
    const x0=xin-X0, y0=yin-Y0, z0=zin-Z0;
    let i1,j1,k1,i2,j2,k2;
    if(x0>=y0){
      if(y0>=z0){ i1=1;j1=0;k1=0;i2=1;j2=1;k2=0; }
      else if(x0>=z0){ i1=1;j1=0;k1=0;i2=1;j2=0;k2=1; }
      else { i1=0;j1=0;k1=1;i2=1;j2=0;k2=1; }
    } else {
      if(y0<z0){ i1=0;j1=0;k1=1;i2=0;j2=1;k2=1; }
      else if(x0<z0){ i1=0;j1=1;k1=0;i2=0;j2=1;k2=1; }
      else { i1=0;j1=1;k1=0;i2=1;j2=1;k2=0; }
    }
    const x1=x0-i1+G3, y1=y0-j1+G3, z1=z0-k1+G3;
    const x2=x0-i2+2*G3, y2=y0-j2+2*G3, z2=z0-k2+2*G3;
    const x3=x0-1+3*G3, y3=y0-1+3*G3, z3=z0-1+3*G3;
    const ii=i&255, jj=j&255, kk=k&255;
    let t0=0.6-x0*x0-y0*y0-z0*z0;
    if(t0<0)n0=0; else{ const gi0=permMod12[ii+perm[jj+perm[kk]]]*3; t0*=t0; n0=t0*t0*(grad3[gi0]*x0+grad3[gi0+1]*y0+grad3[gi0+2]*z0); }
    ... similarly for n1 (ii+i1+perm[jj+j1+perm[kk+k1]]), n2, n3
    return 32*(n0+n1+n2+n3);
  }
}
```
With grad3 flattened array of 36 numbers. That's correct — I've written this before. Good.

**Field function**: angle = noise3D(x*ns, y*ns, t*ts) * π * curliness (+ maybe second octave). Velocity += (cos a, sin a)*force; damping ~0.96; clamp speed. Also gentle global drift upward? Keep neutral.

Particles respawn when out of bounds or life ends: reposition randomly, reset prev=pos to avoid streak lines across screen.

Drawing: strokeStyle with rgba including per-particle alpha (varies by palette weight). To reduce state changes, batch by color bucket: precompute e.g. 5 color buckets; group particles into buckets; per frame per bucket beginPath, moveTo/lineTo all segments, one stroke call. Big perf win. Alpha per-bucket fixed; vary lineWidth slightly? lineWidth per stroke call — could have 2 width classes too. Simpler: 6 buckets × fixed style. Trails come from canvas persistence anyway.

Colors (amber family):
- 'rgba(232,225,214,A)' ivory
- 'rgba(224,177,92,A)' gold  
- 'rgba(201,111,59,A)' ember
- 'rgba(158,132,90,A)' dim bronze
- 'rgba(120,110,95,A)' ash
Assign weights: ivory 30%, gold 30%, bronze 20%, ember 12%, ash 8%. With globalAlpha per bucket like 0.5 etc. Composite 'lighter' will accumulate nicely.

Fade pass: fillStyle 'rgba(8,8,9,0.08)' source-over each frame → trail ~ last ~40 frames. During "stillness" chapter lower alpha→longer trails; during bursts raise.

Hmm, one issue: fade with translucent black fill never fully clears (asymptotic), leaving ghost tint — acceptable on near-black bg; also periodically fine. Fine.

Mouse interactions:
- Track pointer pos + smoothed pos.
- Default: gentle vortex/swirl within radius R: tangential force + slight attraction, so cursor "stirs" the field. Radius ~140px.
- Hold (pointerdown ≥150ms): gather mode — attraction strength ramps up (ease), particles spiral inward (add tangential component for orbital effect — beautiful!). While gathered, count nearby particles, show counter in HUD? Ooh — HUD readout "MOTES GATHERED: 342". Lovely instrument detail.
- Release: impulse outward proportional to gather time & density, plus a temporary "shockwave" ring drawn expanding? Ring might be cheap-looking; instead just the physical explosion of particles reads beautifully with trails. Skip ring. Maybe brief increase of trail brightness.

Touch: same via pointer events; prevent default scrolling conflict — but we need scroll! Conflict: hold-to-gather vs scroll on touch. Solution: on touch devices, gather only works when touching the canvas… but canvas is behind everything. Alternative: dedicate a specific interaction zone? Or: on touch, tap-and-hold without moving gathers; if movement exceeds threshold, cancel gather and allow scroll. Implement: pointerdown starts potential gather; pointermove beyond 10px cancels it (and don't preventDefault so scroll proceeds naturally since we didn't preventDefault on down). Since we never preventDefault, native scroll works; hold-still triggers gather. Reasonable. On desktop, mouse hold doesn't scroll anyway.

Also keyboard: press-and-hold Space to gather at center? Nice accessibility flourish — spacebar hold gathers at screen center. Cheap to add: keydown/up listeners.

**Behavior morphing by scroll**: define keyframes at chapter boundaries: params = {speed, noiseScale, force, fade(alpha), curl}. Compute global scrollProgress p ∈ [0,1]; define param tracks as arrays of stops interpolated smoothly (smoothstep between stops). Chapters:

0. Hero (p 0): medium speed 1.0, scale 0.0016, calm.
1. Dust: slower, larger scale (big soft swirls).
2. Flow: faster, tighter scale (fine turbulent filaments), higher force.
3. Stillness: very slow, long trails (fade 0.03), almost frozen — meditative.
4. Finale: moderate, slightly warmer palette shift? Palette shifting is complex with batching; instead modulate globalAlpha and maybe swap bucket weights subtly. Skip palette morph; motion morph is enough.

Also intro (before scroll): hero has its own vibe.

**Section reveals**: IO threshold 0.35, once? Re-animate every entry is nicer (remove class when far out). I'll toggle both directions with rootMargin.

Ghost numerals: huge outlined Roman numerals using -webkit-text-stroke with transparent fill, opacity 0.07, absolutely placed, parallax slight via transform based on section scroll? Could compute in rAF from getBoundingClientRect — do lightweight parallax: translateY = rect.top * factor. Only for numeral elements. Fine.

**Clock**: setInterval 1s, format HH:MM:SS with blinking colon? Simple update.

**State readout**: update every ~150ms with current lerped params: `TURB 0.63 · VEL 1.42 · MOTES 1600` and during gather `GATHERED 214`. Monospace, tiny, muted.

**Progress rail**: right side fixed: vertical hairline 40vh centered; marker dot moves with scroll progress; four tick marks at chapter positions; clicking tick scrolls to section. Numerals I II III IV beside ticks? Keep minimal: ticks + current chapter label rotated? Minimal: line + dot + small roman numeral that updates. Clickable dots.

**Hint**: bottom-center small mono "press & hold — gather the light" pulsing gently; fades permanently after first successful gather (store flag).

**Intro overlay**: full-screen div bg #08080a covering everything, containing the title composition; after timeline completes, it doesn't disappear — actually make the hero BE the first section (not overlay). Simpler: hero section is normal document flow at top; entrance animations run on load via .loaded class on body with delays. Canvas fades in via its own opacity transition triggered after 600ms. Good — no overlay needed, but initial paint should be black: body bg black, canvas opacity 0 → 1.

Entrance timeline (CSS, triggered by adding .ready to body on window load + small delay):
- rule: scaleX 0→1, 1.2s cubic-bezier(.16,1,.3,1)
- kicker: fade up delay .2s
- title letters: each span translateY(110%)→0 rotate? classic mask reveal, stagger 45ms, duration 1.1s expo-out, starting .35s
- sub: delay 1.2s
- HUD items: fade delays 1.6–2.0s
- hint: 2.4s

Letter styling: "AURELIA" in Italiana, font-size clamp(64px, 14vw, 180px), letter-spacing 0.08em, color ivory. Maybe split coloring: "AUREL" ivory + "IA" gold? Subtle: the final period "." in gold. Or a thin gold underline segment under part of title. I'll add small gold diamond/asterisk mark. Keep type pure: all ivory, with a small gold superscript "†"? no. A gold middle dot before kicker suffices.

Hero composition: kicker top-center? Editorial asymmetry: place block slightly left-of-center? Centered hero is fine for a title piece; asymmetry lives in chapters. Actually let me do: hero centered vertically, left-aligned at 8vw margin with a huge right-side empty space where particles breathe — asymmetric editorial hero. Kicker above, title, then italic subline below, and a scroll cue at bottom ("scroll" + animated line). Left-aligned hero feels more authored than centered. Yes.

Scroll cue: bottom-left or bottom-center: mono "SCROLL" with a 1px vertical line that animates scaleY loop.

**Chapter layout details**:
- Section min-height 130vh, content block max-width 560px, padding-left 8vw (odd sections) / aligned right (padding-right 8vw, text-align left but positioned right side) alternating.
- Ghost numeral: font Italiana, size ~40vw, position absolute opposite side, stroke ivory @ 6% opacity.
- Kicker: mono 11px letterspaced gold: "CHAPTER I — DUST".
- Headline: Cormorant Garamond 500, clamp(40px,6vw,84px), ivory, tight leading. e.g., "Ten thousand motes, none of them twice."
- Body: Cormorant italic 20px, muted ivory 70%, max-width 46ch, line-height 1.7.
- A thin 1px rule 64px wide gold above kicker.

Copy drafts:

Chapter I — DUST
Headline: "Each mote begins in darkness."
Body: "Sixteen hundred points of light, scattered at random, carrying no memory and no destination. Watch any one of them and it seems lost. Watch all of them together and something like intention appears — a weather system made of nothing but obedience to an unseen wind."

Chapter II — FLOW
Headline: "Order, without anyone ordering."
Body: "There is no choreography here. A single mathematical breath — folded noise, curled into current — decides every turn. What you read as grace is just arithmetic repeated sixteen hundred times per frame, patiently, in the dark." 

Chapter III — STILLNESS
Headline: "Now, almost nothing."
Body: "Slow down. The field grows quiet, the light lingers a little longer before it fades. Stay here as long as you like — stillness is not the absence of motion, only motion you have stopped trying to predict."

Finale — AFTERGLOW (colophon)
Headline: "This exact moment will not return."
Body: "No frame of this page has ever existed before, and none will repeat. When you leave, these sixteen hundred small lives dissolve without record. Thank you for watching them burn." 
Then colophon row: mono small: "SET IN ITALIANA & CORMORANT GARAMOND — FIELD SIMULATED LIVE IN YOUR BROWSER — NOTHING HERE IS A VIDEO".

That colophon line "nothing here is a video" is a nice authored touch.

Finale also includes instruction recap: "HOLD ANYWHERE TO GATHER THE LIGHT — RELEASE TO LET IT GO" as a bordered pill? Not pill — plain mono line with gold rules either side.

Wordmark: "AURELIA — Nº 01" top-left. Top-right clock + "LOCAL TIME". 

Page title: "AURELIA — a generative nocturne".

**Custom cursor**: hide default cursor on desktop (media hover:hover & pointer:fine). Dot 4px ivory; ring 28px 1px border ivory 40%, lerp 0.18; hover targets ([data-hover]) scale ring 1.6 + gold border. Holding: ring shrinks to 12px. Blend mode difference? On dark bg difference does little; keep normal.

Interactive elements: nav ticks, maybe title letters hover? Make chapter kickers non-interactive. Provide data-hover on rail ticks and wordmark (click scrolls top).

**Grain overlay**: 
```css
.grain{position:fixed;inset:-100%;width:300%;height:300%;background-image:url("data:image/svg+xml,...feTurbulence...");opacity:.05;pointer-events:none;animation:grain 8s steps(10) infinite;}
@keyframes grain{ transforms translate small percentages }
```
Standard technique. SVG: `<svg xmlns='http://www.w3.org/2000/svg' width='300' height='300'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='2'/></filter><rect width='300' height='300' filter='url(%23n)' opacity='0.6'/></svg>` URL-encoded. z-index above canvas below text? Grain typically sits atop everything (pointer-events none) at low opacity — yes, z-index highest except cursor.

**Vignette**: fixed div, background: radial-gradient(ellipse at center, transparent 55%, rgba(0,0,0,.5) 100%). Subtle, atmospheric. Acceptable.

Also maybe a very subtle top gradient for HUD legibility? Not needed on black.

**Fonts loading**: Google Fonts link: Italiana, Cormorant Garamond ital wghts 400;500;600 + italic, IBM Plex Mono 400;500. Use display=swap.

**Selection color**: gold bg, black text. Scrollbar styling: thin, dark. Nice details.

**Meta viewport**, theme-color #08080a.

Edge cases:
- Mobile: reduce particle count (area/2200 capped 900?), DPR cap 1.75. Hide custom cursor & rail on narrow screens (or move rail). Font sizes clamp. Hero left margin smaller.
- prefers-reduced-motion: set fade higher (shorter trails), speed lower, disable grain animation & letter stagger (show immediately), skip smooth behaviors. Implement basic support: media query CSS for animations; JS check to reduce counts/speed.

Now, code architecture in one file:

```
<!DOCTYPE html><html lang="en"><head>
meta, title, fonts, <style>...</style></head>
<body>
<canvas id="field"></canvas>
<div class="vignette"></div>
<header class="hud hud-top">wordmark | clock</header>
<nav class="rail">...</nav>
<div class="readout" id="readout"></div>
<div class="hint" id="hint">PRESS & HOLD — GATHER THE LIGHT</div>
<main>
  <section class="hero">...</section>
  <section class="chapter" data-num="I" ...>×3</section>
  <section class="finale">...</section>
</main>
<div class="grain"></div>
<div class="cursor"><div class="cursor-dot"></div><div class="cursor-ring"></div></div>
<script>...</script>
</body></html>
```

Canvas fixed inset 0 z-index 0; main z-index 2 relative; hud z 5; grain z 8; cursor z 10.

Wait — pointer events: main sections cover canvas; pointer events attach to window so fine.

Text readability over bright particle areas: particles are dim (alpha low), text ivory — fine. Maybe add slight text-shadow? No—keep clean. Could add backdrop blur? No, heavy. It'll be fine given dark palette.

Let me also consider: the fade-fill approach means canvas has persistent trails even under static text — good.

One concern: 'lighter' composite with many strokes each frame — 1600 short line segments batched into ~6 path strokes = fast. 

Respawn logic: if particle exits bounds+margin or life<=0 → randomize position anywhere, prev=pos, life=random. Life decrements; also randomize occasionally to prevent clumping in attractors. During gather mode, don't respawn mid-hold too aggressively... life handles it.

Gather physics: 
```
if(gatherStrength>0){
  dx=mx-x; dy=my-y; d=hypot; 
  f = gatherStrength * 2.2 * Math.min(1, d/300) ... attraction accel toward mouse scaled;
  tangential: perpendicular (-dy,dx)/d * swirl*gatherStrength*0.6 → orbiting
}
```
On release: for particles within radius 400: impulse away magnitude ∝ (1-d/400)*(1+charge*2). charge = min(holdTime/2.5,1). Also temporarily boost fade alpha (shorter trails) for a crisp flash? Longer trails show explosion arcs — keep trails, maybe boost particle speed cap briefly.

Track gatheredCount = particles within 60px of cursor during hold → readout shows "MOTES HELD — 213". After release, readout returns to field stats. First gather hides hint.

Space key: gather at center of viewport.

Rail: compute chapter positions on resize; on scroll, find active chapter → highlight tick + update label. Marker top% = scrollProgress*100%.

Smooth scrolling for anchor jumps: element.scrollIntoView({behavior:'smooth'}).

Reveal CSS:
```
.rv{opacity:0;transform:translateY(36px);transition:opacity 1s var(--e), transform 1s var(--e);}
.in .rv{opacity:1;transform:none}
with transition-delay via inline style or nth-child.
```
IO toggles .in on section when intersecting ratio>0.25; remove when ratio<0.05 (so re-triggers). Use different thresholds via two observers or check boundingClientRect. Simple: observer with threshold [0, .3]: entry.isIntersecting && ratio>=.3 → add; !isIntersecting → remove. Removing when fully out allows replay. But partial-out keeps .in — fine.

Hero entrance handled separately with body.ready (on load). Hero also inside IO? Give hero its own always-on entrance; exclude hero children from .rv pattern (use .hr-* classes with delays keyed to body.ready).

Parallax numerals: in rAF loop, for each .ghost: rect = el.getBoundingClientRect() each frame is layout thrash ×4 elements — acceptable but better cache offsetTop & use scrollY. Compute: const r = sec.offsetTop; rel = (scrollY + vh - r) ; translate = (rel - vh/2)*-0.08 px. Cache tops on resize. OK.

Readout updates: every 8 frames update string. Content example:
`FIELD 001 · TURB 0.62 · DRIFT 1.38 · MOTES 1600`
during hold append ` · HELD 047`.
Use padded numbers for instrument feel.

Clock: `HH:MM:SS` + timezone offset? `UTC+02` computed. Nice.

Let me draft the palette variables:
```
--bg:#070707; (pure-ish black, warm)
--ink:#eae4d6;
--ink-dim:rgba(234,228,214,.55);
--mut:#8d8677;
--gold:#c9a15a; (slightly desaturated antique gold)
--gold-bright:#e3b96a;
--ember:#b06a3a;
--hair:rgba(234,228,214,.14);
```

Fonts: 
--serif-display:'Italiana', serif;
--serif-text:'Cormorant Garamond', Georgia, serif;
--mono:'IBM Plex Mono', monospace;

Hero title size: clamp(72px, 15vw, 210px)? "AURELIA" 7 chars at 15vw ≈ fits with letter-spacing. Italiana is narrow-ish. Try clamp(68px,13.5vw,190px), letter-spacing .06em, line-height .95.

Add a subtle detail: after title, an italic line: “a generative nocturne — light, folded into weather” hmm. Sub: "sixteen hundred motes of light, adrift in an invisible wind — painted live, never twice the same." Keep shorter: "a nocturne for sixteen hundred points of light". Then mono meta row: "SCROLL TO DESCEND ↓"? no arrows-as-decor concerns; a simple animated line + "SCROLL" text.

Actually count: I'll compute particle count dynamically; copy says "sixteen hundred" — make desktop target exactly 1600 (cap by performance: if area huge, still 1600; mobile fewer → copy mismatch. Adjust copy to "sixteen hundred" only on desktop? Simpler: copy says "a thousand motes" vague... or dynamic: set count = 1600 desktop, 700 mobile, and write copy as "Sixteen hundred" but on small screens it's fewer — nobody counts. Alternatively phrase: "Every mote of light on this page…" avoiding numbers in Ch.I, but readout shows real count — nice honesty. In Ch.I body I'd love the number though. I'll say "sixteen hundred" and ensure desktop = 1600 exactly; mobile gets 800 and copy remains poetic license. Fine.)

Hero also gets a thin gold rule that draws in. And maybe coordinates under sub: "41.3874° N — 2.1686° E" (Barcelona) as flavor? It's decorative flavor; the clock already gives instrument feel. Skip coords, avoid clutter.

Finale extra: a "restart" affordance? Wordmark click scrolls top — mention in colophon: "RETURN TO THE BEGINNING ↑" link. Good closure loop.

Now write ALL the code carefully. Sizeable but manageable. Let me be meticulous about JS correctness.

Key JS pieces:

```js
'use strict';
/* ---------- setup ---------- */
const canvas=document.getElementById('field'), ctx=canvas.getContext('2d');
let W,H,DPR;
function resize(){ DPR=Math.min(devicePixelRatio||1,1.75); W=innerWidth; H=innerHeight; canvas.width=W*DPR; canvas.height=H*DPR; ctx.setTransform(DPR,0,0,DPR,0,0); ctx.fillStyle='#070707'; ctx.fillRect(0,0,W,H); measureSections(); }
```
Note: resizing clears canvas → refill bg.

Simplex class as above.

Params via scroll:
```js
const STOPS=[ // p, speed, nscale, force, fade, swirl
 {p:0.00, v:1.0, ns:0.0016, f:0.55, fd:0.075, sw:0.4},
 {p:0.22, v:0.7, ns:0.0026, f:0.4, fd:0.06, sw:0.5},
 {p:0.48, v:1.5, ns:0.0034, f:0.9, fd:0.09, sw:0.7},
 {p:0.72, v:0.28,ns:0.0011, f:0.25,fd:0.028,sw:0.25},
 {p:1.00, v:1.1, ns:0.0022, f:0.65, fd:0.07, sw:0.5},
];
```
Interp with easing between neighbors: find segment, t=(p-a.p)/(b.p-a.p), te=t*t*(3-2*t), lerp fields.

Current values lerped toward targets each frame (k=0.04) for extra smoothness.

Particles:
```js
const COUNT = matchMedia('(max-width:720px)').matches?800:1600;
parts = Array.from({length:COUNT}, spawn);
function spawn(){ return {x:Math.random()*W, y:Math.random()*H, vx:0, vy:0, b:(Math.random()*BUCKETS)|0, life: 120+Math.random()*260}; }
```
Bucket assignment weighted: pick from weighted list.

Update per frame:
```js
time += 0.0035*v? // evolve noise slowly; tie to dt
for each p:
 const a = noise(p.x*ns, p.y*ns, tz)*TAU*curl; // curl~1.6
 p.vx += Math.cos(a)*f; p.vy += Math.sin(a)*f;
 // mouse stir
 dx=p.x-mx; dy=p.y-my; d2=dx*dx+dy*dy;
 if(d2<R2){ d=sqrt(d2)+.001; const fall=1-d/R; p.vx += (-dy/d)*fall*sw*1.4 + (dx/d)*fall*0.15; ... } // tangential swirl + slight push
 if(gStrength>0){ // gather toward gx,gy
   dx=gx-p.x; dy=gy-p.y; d=sqrt(dx*dx+dy*dy)+.001;
   const pull = gStrength*(1.6*Math.min(1,d/260));
   p.vx += (dx/d)*pull + (-dy/d)*pull*0.85; // spiral
   ...
 }
 p.vx*=damp(0.94 adjusted by v?) ...
 speed clamp: sp2>maxSp2 → scale.
 p.x+=p.vx*v; p.y+=p.vy*v;
 life--; if(life<0||out of bounds) respawn (also record prev=new)
 draw segment prev→cur into bucket path.
 p.px=p.x; p.py=p.y;
```
maxSpeed base ~2.2*v. damp constant 0.93.

Draw:
```js
ctx.globalCompositeOperation='source-over';
ctx.fillStyle=`rgba(7,7,7,${fade})`; ctx.fillRect(0,0,W,H);
ctx.globalCompositeOperation='lighter'; ctx.lineCap='round';
for b in buckets: ctx.strokeStyle=bucket.style; ctx.lineWidth=bucket.w; ctx.beginPath(); for seg in bucketSegs: moveTo(px*DPR?) — careful: we setTransform(DPR..) so use CSS pixel coords directly. yes coords already in CSS px due to transform.
stroke();
```
Collect segments per bucket in arrays reused (flat Float32Array or plain arrays reset each frame). Use plain arrays with length=0.

Bucket styles with alpha tuned so accumulation glows but text zones stay readable. Base alphas ~0.35–0.55, widths 1–1.4. With 'lighter', overlapping builds up. Should look like golden silk threads. lineWidth maybe 1.1 mostly, some 0.7 for fineness, few 1.6 for highlights.

Buckets definition (weighted):
```js
const BUCKETS=[
 {c:'231,225,212', a:.30, w:1.0, wt:.26}, // ivory
 {c:'227,185,106', a:.34, w:1.1, wt:.26}, // gold
 {c:'176,124,66',  a:.30, w:1.0, wt:.20}, // bronze
 {c:'196,110,58',  a:.30, w:.8,  wt:.12}, // ember
 {c:'146,134,112', a:.22, w:.7,  wt:.10}, // ash
 {c:'240,230,205', a:.5,  w:1.6, wt:.06}, // spark (few, brighter)
];
```

Pointer:
```js
let mx=W/2,my=H/2,pmx.., pointerActive=false;
window.addEventListener('pointermove',e=>{mx=e.clientX;my=e.clientY;pointerActive=true;});
pointerdown: pd=true; pdTime=now; gatherPending=true; moved=false; gx,gy set; also cursor ring shrink class.
pointermove during pending: if dist>12 → gatherPending=false (allow scroll on touch).
pointerup: if gathering → explode(charge); reset.
In loop: if(pd && gatherPending && now-pdTime>140) gStrength approaches 1 (lerp .06); charging+=dt.
```
Explode:
```js
function explode(){ const power=0.8+Math.min(charging/2.2,1)*2.4;
 for p: dx=p.x-gx...d<R=420: imp=(1-d/R)*power*(2+Math.random()*2); p.vx+=dx/d*imp; p.vy+=dy/d*imp + slight random;
 flash: set fadeBoost timer (fade *=?) Actually boost brightness: temporarily multiply bucket alpha? simpler: spawn quick radial velocity is enough; also bump v (speed) briefly via impulse variable decaying.
}
```
Also small ambient pulse on click without hold (quick tap): mini burst power 0.9. So taps always do something. Good feedback.

Keyboard space: keydown (repeat guard) sets kbGather at center; keyup explodes.

Cursor DOM follows mouse (desktop only): dot immediate, ring lerp in rAF.

Visibility: document.hidden → skip heavy frame (rAF continues but early return; also reset last timestamp to avoid dt jump). Use dt-based time increment clamped.

dt handling: const now=performance.now(); dt=min(now-last,50); last=now; time+=dt*0.00006*speedFactor? Noise evolution speed: tz increments ~ dt*0.00012*v. Tune: at 16ms frames, tz += 0.002/frame → full field morph cycle noticeable over ~10s. ok.

Velocity scaling by v: apply to integration p.x+=vx*dtN*v where dtN=dt/16.7 normalized.

measureSections: cache section elements' offsetTop & heights for rail mapping & parallax & chapter detection.

Rail build: chapters = [hero, c1,c2,c3,finale]? Rail ticks for 5 stops labeled ◦? Use numerals: ✦ no emoji — use roman text "O I II III IV"? Hero="∅"? Keep ticks as small 1px×8px lines; active becomes gold & taller. Label current chapter name next to rail? Put tiny rotated text? Simplify: ticks only + separate bottom-left readout includes "CH. II — FLOW". Yes! Readout shows chapter name — cleaner than rail text.

Click tick → scrollTo section.

IO reveals: sections observe.

Fine — also noscript? Minor, skip.

Accessibility basics: aria-hidden on decorative, alt-free (no imgs), buttons for ticks (real <button>). lang="en". Focus styles: outline gold on focus-visible.

Let me also handle: user asked "most beautiful and stunning" — I should present confidently and explain features briefly after code.

Now write final copy carefully (spelling, tone consistent, en dashes).

Hero:
- kicker: `Nº 01 — A GENERATIVE NOCTURNE` (mono, gold, tracked)
- Title: AURELIA
- sub (italic serif): “sixteen hundred motes of light, adrift in an invisible wind — painted live, never twice the same.”
- scroll cue bottom center: mono "SCROLL" + animated hairline.

Chapter I — DUST
h: “Each mote begins alone.”
p: “Scattered at random across the dark, carrying neither memory nor destination. Follow any single one and it appears utterly lost. Follow all of them together and something like intention surfaces — a weather system assembled from nothing but small obediences to a wind nobody can see.”

Chapter II — FLOW
h: “Order, with no one ordering.”
p: “There is no choreography here. One mathematical breath — noise, folded into current — decides every turn. What reads as grace is arithmetic, repeated sixteen hundred times per frame, patiently, in the dark.”

Chapter III — STILLNESS
h: “Now, almost nothing.”
p: “The field goes quiet. Light lingers a little longer before it fades. Stay as long as you wish — stillness is not the absence of motion, only motion you have stopped trying to predict.”

Finale — AFTERGLOW
h: “This exact moment will not return.”
p: “Not one frame of this page has ever existed before, and none will come again. When you leave, these small lives dissolve without record. Thank you for watching them burn.”
meta rows (mono):
“SET IN ITALIANA & CORMORANT GARAMOND”
“FIELD SIMULATED LIVE — NOT A VIDEO, NEVER A RECORDING”
link: “RETURN TO THE FIRST DARK” (scroll top)

Hint: “PRESS & HOLD — GATHER THE LIGHT”

Readout format: `CH·0 TURB 0.42 VEL 1.00 MOTES 1600` and held: `HELD 031`. Compose like: `II · FLOW — TURB 0.61 / VEL 1.42 / MOTES 1600`.

Wordmark: `AURELIA` + gold dot + `Nº 01`. Click → top.

Clock top-right: `21:47:03 UTC+1`.

CSS writing — be thorough with responsive.

Potential pitfall: Italiana has limited charset but fine for AURELIA + numerals. Roman numerals in ghost backgrounds use Italiana — supports letters obviously.

Ghost numeral styling:
```css
.ghost{position:absolute;font-family:var(--disp);font-size:min(52vw,560px);line-height:1;color:transparent;-webkit-text-stroke:1px rgba(234,228,214,.10);user-select:none;pointer-events:none;z-index:-1;}
```
text-stroke fallback: also `color:rgba(234,228,214,.04)` if stroke unsupported? Use @supports. Simple: set color transparent + stroke; Firefox supports -webkit-text-stroke actually. OK.

Alternating placement: .chapter:nth-of-type(odd) content left, ghost right; even reversed. Hero excluded (it's .hero). Use explicit classes .align-right on 2nd & finale? Manage manually: ch1 left, ch2 right, ch3 left, finale centered? Finale centered composition feels ceremonial. Yes finale: centered text-align center.

Spacing: sections padding: 22vh 8vw; min-height 120vh (finale 110vh centered flex).

Rules: .rule{width:56px;height:1px;background:var(--gold);}

Kicker letter-spacing .32em font-size 11px.

Headline font-weight 500 Cormorant, size clamp(44px, 5.6vw, 88px), line-height 1.02, letter-spacing -0.01em. Cormorant at 500 is elegant. Maybe mix italic word inside headline for flair: e.g., “Order, with no one *ordering.*” italic accent gold? Italic same color; gold might be nice for one word. Do: last word italic in gold-bright. Tasteful accent. Apply via <em>.

Body: 20px/1.75 italic? Full italic paragraphs in Cormorant are lovely but long italic can tire; body regular with italic pull? Choose: body in Cormorant 400 normal, 19–20px, color dim; opening words or a pull-line italic. Keep body roman, headlines mixed. Actually poetic voice suits italic; Cormorant italic is very legible at 20px. I'll set body italic — distinctive, matches "elegy" tone. Yes italic body.

Max-width 44ch.

Stagger delays: .rv:nth-child pattern won't work across mixed elems; assign inline style="--d:.1s" per element; transition-delay:var(--d).

Hero entrance similar with body.ready and --d values bigger.

Cursor CSS:
```css
@media (hover:hover) and (pointer:fine){ body{cursor:none;} a,button{cursor:none;} .cursor{display:block} }
.cursor-dot{position:fixed;width:5px;height:5px;border-radius:50%;background:var(--gold-bright);z-index:40;pointer-events:none;transform:translate(-50%,-50%);}
.cursor-ring{...28px;border:1px solid rgba(234,228,214,.35);transition:width .3s,height .3s,border-color .3s;}
.cursor.holding .ring{width:14px;height:14px;border-color:var(--gold)}
.cursor.hovering .ring{width:44px;height:44px;border-color:var(--gold)}
```
Position via left/top style in JS (transform translate3d). Set ring pos lerp.

Hide native cursor everywhere incl. iframe-none. Also hide when leaving window (mouseout to null → opacity 0).

Scrollbar: 
```css
::-webkit-scrollbar{width:10px} thumb bg #1c1a16 border-radius; track transparent.
```

Selection: background:var(--gold);color:#0a0908.

Focus-visible: outline:1px solid var(--gold);outline-offset:3px.

Grain keyframes translate combos.

Media reduced motion:
```css
@media (prefers-reduced-motion:reduce){ .rv,.hero-*{transition:none!important;animation:none!important;opacity:1!important;transform:none!important} .grain{animation:none} .cue-line{animation:none} }
```
JS: const RM=matchMedia('(prefers-reduced-motion: reduce)').matches → reduce COUNT to 600, speed multiplier .5, fade .12 (short trails).

Mobile tweaks (@media max-width:720px): hide .rail? Keep rail but thinner & closer edge; hide readout? Readout is charming — keep but smaller, maybe hide clock seconds? Keep all, shrink. Hide custom cursor automatically via media query (already). Hero title 17vw. Section padding-inline 7vw. Ghost numerals 70vw opacity lower.

Also iOS Safari: 100vh issues → use min-height:100svh where supported with fallback. Use `min-height:100vh; min-height:100svh;`.

Prevent overscroll bounce visual weirdness: html{background:#070707}.

touch-action: manipulation on body? We rely on native scroll; pointer events passive listeners default fine. Don't preventDefault anywhere except maybe double-tap zoom prevention via touch-action:manipulation on html. Add.

user-select:none on HUD; allow selecting body copy? Poetry selectable is nice; keep selection styled. HUD & ghosts unselectable.

Now assemble the JS fully & carefully. Let me write it mentally end-to-end to catch bugs.

```js
(() => {
'use strict';
const $=(s,c=document)=>c.querySelector(s), $$=(s,c=document)=>[...c.querySelectorAll(s)];
const RM = matchMedia('(prefers-reduced-motion: reduce)').matches;
const TOUCH = matchMedia('(hover: none)').matches;

/* Simplex */
class Simplex{constructor(seed=Math.random()){const p=new Uint8Array(256);for(let i=0;i<256;i++)p[i]=i;let n=seed*65537|0;const rnd=()=>((n=(n*1664525+1013904223)|0)>>>0)/4294967296;for(let i=255;i>0;i--){const j=(rnd()*(i+1))|0;const t=p[i];p[i]=p[j];p[j]=t;}this.perm=new Uint8Array(512);this.pm12=new Uint8Array(512);for(let i=0;i<512;i++){this.perm[i]=p[i&255];this.pm12[i]=this.perm[i]%12;}}
noise(x,y,z){const G=[[1,1,0],[-1,1,0],[1,-1,0],[-1,-1,0],[1,0,1],[-1,0,1],[1,0,-1],[-1,0,-1],[0,1,1],[0,-1,1],[0,1,-1],[0,-1,-1]];...
```
Putting grad inside noise allocates per call — bad. Define static GRAD outside. Write properly:

```js
const G3=[1,1,0,-1,1,0,1,-1,0,-1,-1,0,1,0,1,-1,0,1,1,0,-1,-1,0,-1,0,1,1,0,-1,1,0,1,-1,0,-1,-1];
class Simplex{
 constructor(){const p=new Uint8Array(256);for(let i=0;i<256;i++)p[i]=i;let s=1337;const rnd=()=>(s=(s*16807)%2147483647)/2147483647;
  for(let i=255;i>0;i--){const j=(rnd()*(i+1))|0,t=p[i];p[i]=p[j];p[j]=t;}
  this.perm=new Uint8Array(512);this.pm=new Uint8Array(512);
  for(let i=0;i<512;i++){this.perm[i]=p[i&255];this.pm[i]=this.perm[i]%12;}}
 noise(x,y,z){
  const F=1/3,G=1/6,{perm,pm}=this;
  const sk=(x+y+z)*F, i=Math.floor(x+sk), j=Math.floor(y+sk), k=Math.floor(z+sk);
  const t=(i+j+k)*G, x0=x-(i-t), y0=y-(j-t), z0=z-(k-t);
  let i1,j1,k1,i2,j2,k2;
  if(x0>=y0){ if(y0>=z0){i1=1;j1=0;k1=0;i2=1;j2=1;k2=0;} else if(x0>=z0){i1=1;j1=0;k1=0;i2=1;j2=0;k2=1;} else {i1=0;j1=0;k1=1;i2=1;j2=0;k2=1;} }
  else { if(y0<z0){i1=0;j1=0;k1=1;i2=0;j2=1;k2=1;} else if(x0<z0){i1=0;j1=1;k1=0;i2=0;j2=1;k2=1;} else {i1=0;j1=1;k1=0;i2=1;j2=1;k2=0;} }
  const x1=x0-i1+G,y1=y0-j1+G,z1=z0-k1+G;
  const x2=x0-i2+2*G,y2=y0-j2+2*G,z2=z0-k2+2*G;
  const x3=x0-0.5,y3=y0-0.5,z3=z0-0.5;
  const ii=i&255,jj=j&255,kk=k&255;
  let n=0,t0=0.6-x0*x0-y0*y0-z0*z0;
  if(t0>0){const g=pm[ii+perm[jj+perm[kk]]]*3;t0*=t0;n+=t0*t0*(G3[g]*x0+G3[g+1]*y0+G3[g+2]*z0);}
  let t1=0.6-x1*x1-y1*y1-z1*z1;
  if(t1>0){const g=pm[ii+i1+perm[jj+j1+perm[kk+k1]]]*3;t1*=t1;n+=t1*t1*(G3[g]*x1+G3[g+1]*y1+G3[g+2]*z1);}
  let t2=0.6-x2*x2-y2*y2-z2*z2;
  if(t2>0){const g=pm[ii+i2+perm[jj+j2+perm[kk+k2]]]*3;t2*=t2;n+=t2*t2*(G3[g]*x2+G3[g+1]*y2+G3[g+2]*z2);}
  let t3=0.6-x3*x3-y3*y3-z3*z3;
  if(t3>0){const g=pm[ii+1+perm[jj+1+perm[kk+1]]]*3;t3*=t3;n+=t3*t3*(G3[g]*x3+G3[g+1]*y3+G3[g+2]*z3);}
  return 32*n;
 }}
```
Check corner 3 offsets: x3 = x0 - 1 + 3G = x0 -1 +0.5 = x0-0.5 ✓. Index for corner3: ii+1+perm[jj+1+perm[kk+1]] ✓.

Seed rnd: LCG s*16807 % 2147483647 needs s nonzero & <2^31; start 1337 fine; first rnd: 1337*16807=22,468,... fine. Values in (0,1]. OK.

Canvas & sim:

```js
const canvas=$('#field'),ctx=canvas.getContext('2d',{alpha:false});
let W=0,H=0,DPR=1;
const sx=new Simplex();
const BUCKETS=[
 {c:'232,226,213',a:.26,w:1.0,n:.24},
 {c:'228,186,108',a:.30,w:1.1,n:.24},
 {c:'178,128,70', a:.27,w:1.0,n:.18},
 {c:'199,112,58', a:.28,w:0.85,n:.11},
 {c:'148,137,116',a:.20,w:0.7,n:.15},
 {c:'244,233,206',a:.5,w:1.6,n:.08},
];
```
n sums to 1.0 ✓ (.24+.24+.18+.11+.15+.08=1.00).

Bucket assignment: cumulative pick.

```js
let parts=[],segs=BUCKETS.map(()=>[]);
function pickBucket(){let r=Math.random(),acc=0;for(let i=0;i<BUCKETS.length;i++){acc+=BUCKETS[i].n;if(r<acc)return i;}return 0;}
const COUNT_BASE = innerWidth<720?750:1600;
const COUNT = RM?Math.round(COUNT_BASE*0.4):COUNT_BASE;
function spawn(p){p=p||{};p.x=Math.random()*W;p.y=Math.random()*H;p.px=p.x;p.py=p.y;p.vx=0;p.vy=0;p.b=pickBucket();p.life=100+Math.random()*300;return p;}
```

Params:
```js
const STOPS=[
 {p:0.00,v:1.00,ns:0.0016,f:0.055,fd:0.075,sw:0.5},
 {p:0.20,v:0.62,ns:0.0027,f:0.040,fd:0.055,sw:0.6},
 {p:0.46,v:1.45,ns:0.0036,f:0.085,fd:0.095,sw:0.8},
 {p:0.70,v:0.22,ns:0.0010,f:0.028,fd:0.026,sw:0.3},
 {p:1.00,v:0.95,ns:0.0021,f:0.060,fd:0.070,sw:0.5},
];
```
Force magnitudes: accel per frame ~0.05 with damping .93 → terminal v ≈ a/(1-damp)= .05/.07≈0.71 px/frame *v. Times v multiplier 1.45 → ~1 px/f. Slowish elegant. Explosion impulses override temporarily. Gather pull up to ~1.6 strong enough vs damping. Fine; will tune constants plausibly.

lerp stops:
```js
function paramsAt(p){let a=STOPS[0],b=STOPS[STOPS.length-1];
 for(let i=0;i<STOPS.length-1;i++){if(p>=STOPS[i].p&&p<=STOPS[i+1].p){a=STOPS[i];b=STOPS[i+1];break;}}
 const span=b.p-a.p||1;let t=(p-a.p)/span;t=Math.max(0,Math.min(1,t));t=t*t*(3-2*t);
 return {v:a.v+(b.v-a.v)*t, ns:a.ns+(b.ns-a.ns)*t, f:a.f+(b.f-a.f)*t, fd:a.fd+(b.fd-a.fd)*t, sw:a.sw+(b.sw-a.sw)*t};}
```

State:
```js
let cur={v:1,ns:0.0016,f:0.055,fd:0.075,sw:0.5};
let scrollP=0, tz=Math.random()*100;
let mx=W/2,my=H*0.5,mDown=false,gStr=0,charging=0,gx=0,gy=0,held=0,lastTap=0;
let kb=false;
```

Events:
```js
addEventListener('pointermove',e=>{mx=e.clientX;my=e.clientY;if(mDown&&!moved){if(Math.hypot(e.clientX-dx0,e.clientY-dy0)>14)moved=true;}},{passive:true});
```
Hmm gather-cancel-on-move: track start pos sx0,sy0 at pointerdown; if moved>14 → moved=true (cancels pending gather on touch; on mouse irrelevant but harmless — mouse users holding & moving lose gather? Bad! Desktop users will move while holding. So cancel-on-move should apply only to touch pointerType. `if(e.pointerType!=='mouse' && dist>14) moved=true;` For pen treat like touch.) Good catch.

```js
addEventListener('pointerdown',e=>{ if(e.button!==undefined&&e.button!==0&&e.pointerType==='mouse')return; mDown=true;moved=false;sx0=e.clientX;sy0=e.clientY;gx=e.clientX;gy=e.clientY;pdT=performance.now();document.body.classList.add('holding');});
addEventListener('pointerup',()=>{ if(mDown){ if(gStr>0.15) explode(); mDown=false;gStr=0;charging=0;held=0;document.body.classList.remove('holding');}});
addEventListener('pointercancel',same as up);
blur → release.
keydown Space: if(!e.repeat&&!kb){kb=true;gx=W/2;gy=H*0.55;pdT=performance.now();} preventDefault to avoid page scroll? Space normally scrolls page — preventing breaks expected behavior; but our page scroll via wheel/touch mostly; Space scrolling is legit though. Compromise: don't preventDefault; space scrolls AND gathers at center — chaotic. Better: preventDefault only when body focused... Simply preventDefault; provide scroll via wheel/touch/rail. Acceptable for an art piece; note in hint? Hint mentions press&hold (pointer). Keyboard users discover little anyway. I'll preventDefault on Space keyup/keydown to make gather clean.
keyup Space: explode if gStr>.15; kb=false.
```

Loop core:

```js
let last=performance.now();
function frame(now){
 requestAnimationFrame(frame);
 let dt=Math.min(now-last,48);last=now;
 if(document.hidden)return;
 const pn=paramsAt(scrollP);
 cur.v+=(pn.v-cur.v)*0.045; cur.ns+=(pn.ns-cur.ns)*0.045; cur.f+=(pn.f-cur.f)*0.045; cur.fd+=(pn.fd-cur.fd)*0.045; cur.sw+=(pn.sw-cur.sw)*0.045;
 const vMul=cur.v*(RM?0.55:1);
 tz+=dt*0.00011*(0.5+vMul*0.5);

 // gather ramp
 const wantG=(mDown&&!moved&&now-pdT>130)||kb;
 gStr+=((wantG?1:0)-gStr)*0.07;
 if(wantG)charging+=dt/1000;
 if(gStr>0.02){gx+= ((kb?W/2:gx)-gx)*0; } // gx fixed at down point; fine.
 // count held
 held=0;

 // fade pass
 ctx.globalCompositeOperation='source-over';
 ctx.fillStyle=`rgba(7,7,7,${(cur.fd*(RM?1.6:1)).toFixed(3)})`;
 ctx.fillRect(0,0,W,H);

 ctx.globalCompositeOperation='lighter';
 ctx.lineCap='round';
 for(const s of segs)s.length=0;

 const ns=cur.ns,f=cur.f,sw=cur.sw;
 const R=Math.min(W,H)*0.22, R2=R*R;
 const damp=0.93;
 const maxSp=2.4*vMul+0.4, maxSp2=maxSp*maxSp;
 const nDt=dt/16.7;

 for(let i=0;i<parts.length;i++){
  const p=parts[i];
  const ang=sx.noise(p.x*ns,p.y*ns,tz)*Math.PI*2.4;
  p.vx+=Math.cos(ang)*f*nDt; p.vy+=Math.sin(ang)*f*nDt;

  let dxm=p.x-mx,dym=p.y-my,d2=dxm*dxm+dym*dym;
  if(pointerLive&&d2<R2){
   const d=Math.sqrt(d2)||1,fall=1-d/R;
   p.vx+=(-dym/d)*fall*sw*0.9*nDt + (dxm/d)*fall*0.12*nDt;
   p.vy+=( dxm/d)*fall*sw*0.9*nDt + (dym/d)*fall*0.12*nDt;
  }

  if(gStr>0.02){
   const dxg=gx-p.x,dyg=gy-p.y,dg=Math.sqrt(dxg*dxg+dyg*dyg)||1;
   const pull=gStr*(0.5+1.5*Math.min(1,dg/280))*0.55;
   p.vx+=(dxg/dg)*pull*nDt+(-dyg/dg)*pull*0.9*nDt;
   p.vy+=(dyg/dg)*pull*nDt+( dxg/dg)*pull*0.9*nDt;
   if(dg<70)held++;
  }

  p.vx*=damp;p.vy*=damp;
  const sp2=p.vx*p.vx+p.vy*p.vy;
  if(sp2>maxSp2){const k=maxSp/Math.sqrt(sp2);p.vx*=k;p.vy*=k;}

  p.x+=p.vx*nDt*vMul; p.y+=p.vy*nDt*vMul;
  p.life-=nDt;
  if(p.life<=0||p.x<-20||p.x>W+20||p.y<-20||p.y>H+20){spawn(p);continue;}

  segs[p.b].push(p.px,p.py,p.x,p.y);
  p.px=p.x;p.py=p.y;
 }

 for(let b=0;b<BUCKETS.length;b++){
  const B=BUCKETS[b],arr=segs[b];
  if(!arr.length)continue;
  ctx.strokeStyle=`rgba(${B.c},${B.a})`;
  ctx.lineWidth=B.w;
  ctx.beginPath();
  for(let i=0;i<arr.length;i+=4){ctx.moveTo(arr[i],arr[i+1]);ctx.lineTo(arr[i+2],arr[i+3]);}
  ctx.stroke();
 }
}
requestAnimationFrame(frame);
```

Note: when respawning we `continue` skipping segment draw — correct (avoid streak).

Explosion:
```js
function explode(){
 const power=1.1+Math.min(charging,2.4)*1.5;
 const R=380+charging*120;
 for(const p of parts){
  const dx=p.x-gx,dy=p.y-gy,d=Math.sqrt(dx*dx+dy*dy)||1;
  if(d<R){const imp=(1-d/R)*power*(1.5+Math.random()*1.5);
   p.vx+=dx/d*imp;p.vy+=dy/d*imp;}
 }
 if(!usedGather){usedGather=true;hideHint();}
}
```

Tap quick burst: on pointerup if !moved && holdDuration<130 && gStr small → mini explode power 0.8 R 220. Implement: in pointerup compute dur=now-pdT; if(dur<130&&!moved) smallBurst at gx,gy. Combine into explode(powerScale).

scrollP update:
```js
function onScroll(){
 const max=document.documentElement.scrollHeight-innerHeight;
 scrollP=max>0?Math.min(1,Math.max(0,scrollY/max)):0;
 // chapter detect & rail marker & readout chapter
}
addEventListener('scroll',onScroll,{passive:true});
```
Marker: railDot.style.top = (scrollP*100)+'%'.

Active chapter: sections array with cached centers; find nearest center to viewport center. Update readout label & tick classes.

Parallax ghosts in same scroll handler (cheap) or rAF: use rAF read of cached tops:
```js
function parallax(){for(const g of ghosts){const rel=scrollY+vh - g.top; g.el.style.transform=`translateY(${(rel-vh/2)*-0.06}px)`;}}
```
Call in frame loop every frame (cheap, 4 elements). Need vh updated on resize, g.top cached via offsetTop of parent section. transform conflicts? Ghost has no other transform. ✓

Reveal IO:
```js
const io=new IntersectionObserver(es=>{for(const e of es){e.target.classList.toggle('in',e.isIntersecting);}},{threshold:[0,0.28]});
$$('.rv-group').forEach(el=>io.observe(el));
```
Apply .in styles to descendants .rv. Toggle false when out → replays. threshold 0.28 might never trigger on tall sections whose content sits high? Content block within tall section; observe the content wrapper instead (smaller). Observe `.stage` (content container) elements. ✓

Clock:
```js
function tick(){const d=new Date();const pad=n=>String(n).padStart(2,'0');
 const off=-d.getTimezoneOffset()/60;const sign=off>=0?'+':'−';
 $('#clock').textContent=`${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())} UTC${sign}${pad(Math.abs(off))}`;}
setInterval(tick,1000);tick();
```
UTC offset formatting with halves (e.g., +05:30)? Keep hours-only; India users see +5 wrong-ish. Format minutes too: `UTC+05:30`: 
```js
const m=Math.abs(off)%1*60; `${sign}${pad(Math.floor(Math.abs(off)))}:${pad(m)}`
```
Nice.

Readout updater every 6th frame:
```js
frameCount%6===0 → readout.textContent = `${chLabel} · TURB ${cur.ns*1000.toFixed?} ...`
```
Format: turb display cur.f*10? Show meaningful: `VEL ${cur.v.toFixed(2)} · FLW ${(cur.f*100).toFixed(0)} · TRB ${(cur.ns*1000).toFixed(1)} · N ${parts.length}` plus held: ` · HELD ${held}` when >0. Prefix chapter: `I·DUST`. Compose: `I — DUST ▸ VEL 1.42 …` avoid glyph weirdness; use plain: `I · DUST — VEL 1.42 / FLD 0.06 / MOTES 1600`.

Rail ticks: build from sections list in JS or hardcode 5 buttons in HTML with data-target ids. Hardcode: ids: hero, dust, flow, still, after. Buttons aria-label "Go to chapter I".

measure(): cache secTops for centers & ghost tops; run after fonts load (layout shift) → also on load event + resize + setTimeout 500. Use ResizeObserver on body? Simple: window resize + load + font ready promise.

Fonts: document.fonts.ready.then(measure).

Init sequence: body.ready added on window load OR after fonts.ready + 100ms, whichever first? Use: Promise.all([fonts.ready]).then(()=>setTimeout(()=>body.classList.add('ready'),80)); Also fallback timeout 1800ms add anyway. Canvas fade-in: canvas opacity transition 2s; add .on class same time.

Edge: initial scrollP if reloaded mid-page — call onScroll() once at init.

Hint hide: also auto-fade after 20s regardless? Keep until used; it's small. Also hide on touch after first gather same way.

Wordmark click & RETURN link: scrollTo({top:0,behavior:RM?'auto':'smooth'}).

Rail click: targets scrollIntoView smooth.

Now HTML structure:

```html
<body>
 <canvas id="field" aria-hidden="true"></canvas>
 <div class="vignette" aria-hidden="true"></div>

 <header class="hud">
  <button class="mark" id="mark" data-hover>AURELIA<span class="dot">·</span><span class="no">Nº 01</span></button>
  <div class="clock" id="clock" aria-hidden="true">00:00:00</div>
 </header>

 <nav class="rail" aria-label="Chapters">
  <span class="rail-track"></span>
  <span class="rail-dot" id="railDot"></span>
  <button data-t="hero" data-hover aria-label="Beginning"></button>
  <button data-t="dust" data-hover aria-label="Chapter I — Dust"></button>
  <button data-t="flow" data-hover aria-label="Chapter II — Flow"></button>
  <button data-t="still" data-hover aria-label="Chapter III — Stillness"></button>
  <button data-t="after" data-hover aria-label="Afterglow"></button>
 </nav>

 <div class="readout" id="readout" aria-hidden="true"></div>
 <div class="hint" id="hint"><span>PRESS&nbsp;&amp;&nbsp;HOLD</span> GATHER THE LIGHT</div>

 <main>
  <section class="hero" id="hero">
   <div class="stage">
    <p class="kicker hr" style="--d:.15s"><span class="rule"></span>Nº 01 — A GENERATIVE NOCTURNE</p>
    <h1 class="title" aria-label="AURELIA">
     <span class="l" style="--d:.30s">A</span>... each letter
    </h1>
    <p class="sub hr" style="--d:1.25s">Sixteen hundred motes of light, adrift in an invisible wind —<br><em>painted live, never twice the same.</em></p>
   </div>
   <div class="cue hr" style="--d:1.9s"><span class="cue-word">SCROLL</span><span class="cue-line"></span></div>
  </section>

  <section class="chapter" id="dust">
   <span class="ghost" aria-hidden="true">I</span>
   <div class="stage rv-group">
    <p class="kicker rv" style="--d:0s"><span class="rule"></span>CHAPTER I — DUST</p>
    <h2 class="head rv" style="--d:.08s">Each mote begins <em>alone.</em></h2>
    <p class="body rv" style="--d:.16s">Scattered at random across the dark, carrying neither memory nor destination. Follow any single one and it appears utterly lost. Follow all of them together and something like intention surfaces — a weather system built from nothing but small obediences to a wind no one can see.</p>
   </div>
  </section>
  ... flow (right-aligned), still ...
  <section class="finale" id="after">
   <span class="ghost ghost-c" aria-hidden="true">IV</span>? 
```
Finale ghost "IV"? Chapters I II III, finale unlabeled — ghost could be "∞"? Italiana may lack ∞. Use "IV"? Finale isn't chapter IV... call finale ghost "✳"? Use "FIN"? Ghost with word "END"? Hmm — ghost "Nº" no. Just omit ghost on finale, or use a large gold asterisk-like star drawn via CSS? Omit — centered finale with rules is ceremonial enough.

Finale stage centered:
```html
<section class="finale" id="after">
 <div class="stage rv-group">
  <p class="kicker rv center"><span class="rule"></span>AFTERGLOW<span class="rule"></span></p>
  <h2 class="head rv">This exact moment <em>will not return.</em></h2>
  <p class="body rv">Not one frame of this page has existed before, and none will come again. When you leave, these small lives dissolve without record.<br>Thank you for watching them burn.</p>
  <div class="colophon rv">
   <span>SET IN ITALIANA &amp; CORMORANT GARAMOND</span>
   <span>FIELD SIMULATED LIVE — NOT A VIDEO, NEVER A RECORDING</span>
   <button class="back" id="back" data-hover>RETURN TO THE FIRST DARK</button>
  </div>
 </div>
</section>
```

Colophon separated by hairlines top/bottom, mono 10px tracked, gap.

Hero letters markup: wrap each in span.l inside h1 with overflow hidden? Mask reveal: h1 has clip via each span wrapped: `<span class="lw"><span class="l">A</span></span>` where .lw overflow:hidden inline-block. Simpler: .l display:inline-block; transform translateY(120%) initially; h1 overflow:hidden — but descenders? Italiana caps only, no descenders in "AURELIA"; overflow hidden on h1 clips rising letters cleanly. line-height 1 padding-bottom small. Works: h1{overflow:hidden} .l{display:inline-block;transform:translateY(115%);transition:transform 1.2s cubic-bezier(.19,1,.22,1);transition-delay:calc(var(--d))} body.ready .l{transform:none}. Letter-spacing applies after each char incl last — minor.

Whitespace between spans: HTML source newlines create gaps — with letter-spacing desired anyway; but inline-block whitespace adds ~0.25em extra. Set h1 font-kerning none & letter-spacing handles rhythm; extra inter-word spaces from source newlines would add unevenly. Solution: put letters on one line without whitespace: `<span ...>A</span><span...>U</span>...` all contiguous. ✓

.hr elements initial opacity 0 translateY(24px); body.ready → visible with delay var(--d). Same mechanism as .rv but keyed to body.ready. Class .hi (hero-in). Use same .rv styles but gate: `.ready .hero .rv{...visible}` — unify: define
```css
.rv{opacity:0;transform:translateY(34px);transition:opacity 1.1s cubic-bezier(.22,1,.36,1) var(--d,0s),transform 1.1s cubic-bezier(.22,1,.36,1) var(--d,0s)}
.in .rv,body.ready .hero .rv,body.ready .cue.rv{opacity:1;transform:none}
```
Give hero children .rv too & cue .rv; body.ready triggers them; other sections via .in on .rv-group ancestor. But .in toggling removes when scrolled away — hero stays because body.ready persists. ✓ And rule span inside kicker: .rule{display:inline-block;width:44px;height:1px;background:var(--gold);margin-right:14px;vertical-align:middle;transform:scaleX(0);transform-origin:left;transition:transform 1.4s ...}. Animate scaleX when parent visible: `.in .rule,body.ready .hero .rule{transform:scaleX(1)}` with delay +0.2s. Finale center kicker: rules both sides — origin center for second? Keep simple: both scaleX from left; visually fine, or give .center .rule origin center. Detail: set .finale .rule{transform-origin:center}.

Cue: absolute bottom center of hero: word mono 10px tracked + vertical line 48px with scaleY loop animation:
```css
.cue-line{width:1px;height:52px;background:linear-gradient(...)}? 
```
Gradient on cue line — avoid; use solid hairline with animated translating dash: pseudo-element moving: .cue-line{position:relative;overflow:hidden;background:rgba(ivory,.15)} .cue-line::after{content:'';position:absolute;left:0;top:-40%;width:100%;height:40%;background:var(--gold);animation:drip 2.2s cubic-bezier(.65,0,.35,1) infinite} @keyframes drip{to{top:110%}}. Elegant.

HUD styling: fixed top; display:flex justify-between; padding:28px 36px; mono 11px letterspaced. Mark button styled text with gold middot. Hover: color shift.

Rail: fixed right:26px top:50% translateY(-50%); height:38vh; width:1px track bg hair; dot 5px gold circle left:-2px transition top .2s? Top set per frame — direct style, add transition top .35s ease for smoothness (updates on scroll events; fine). Buttons: 12px hit area lines: width:14px;height:1px bg hair; position absolute along track at 0/25/50/75/100%: left:-7px; active: bg gold width 22px left:-11px. Buttons need bigger touch target: wrap with ::after inset -8px.

Positions: 5 ticks evenly: top: calc(i*25%). ✓

Readout: fixed left:36px bottom:30px mono 10px tracked color mut; contains chapter span gold. Held indicator maybe gold too.

Hint: fixed bottom:30px right:36px mono 10px; "PRESS & HOLD" in gold box? Style: border:1px solid hair;padding:10px 14px;letter-spacing:.28em; with pulsing opacity animation (subtle 3s). Hidden state translateY(10px) opacity 0 transition.

Z-indexes: canvas 0(fixed), vignette 1, main 2, hud/rail/readout/hint 5, grain 7, cursor 9.

Grain above text slightly textures type — at 4–5% fine, adds filmic unity. mix-blend-mode:overlay? On dark, overlay grain can lighten oddly; plain normal with low opacity white-noise image (has gray tones) — use opacity .06, no blend. Actually feTurbulence rect produces colored noise unless we desaturate: add feColorMatrix type saturate 0. Encode:

`data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="240" height="240"><filter id="n"><feTurbulence type="fractalNoise" baseFrequency="0.8" numOctaves="2" stitchTiles="stitch"/><feColorMatrix type="saturate" values="0"/></filter><rect width="240" height="240" filter="url(%23n)" opacity="0.55"/></svg>` — must URL-encode # and quotes. Use single quotes inside, encode # as %23, spaces %20 or keep spaces (browsers tolerate in quoted url? Safer encode). I'll write encoded compactly.

Animation grain: steps jumping background-position via transform on oversized layer:
```css
.grain{position:fixed;inset:-50%;width:200%;height:200%;background:url(...) repeat;background-size:240px;opacity:.055;pointer-events:none;z-index:7;animation:grain 7s steps(8) infinite}
@keyframes grain{0%{transform:translate(0,0)}12.5%{transform:translate(-2%,1%)}25%{transform:translate(1%,-2%)}...100%{transform:translate(0,0)}}
```
8 keyframe stops.

Vignette: `background:radial-gradient(120% 90% at 50% 45%, transparent 60%, rgba(0,0,0,.42))`. Functional atmosphere.

Also subtle center glow behind hero title? Would be decorative gradient — skip; particles provide life.

Body copy width & sizes done. Headline em style: font-style italic, color gold-bright? Gold text on black at large size = tasteful accent. Yes: .head em{font-style:italic;color:var(--gold-b)}. Sub em likewise.

Kicker color gold; body color rgba ivory .62; head ivory.

Font smoothing antialiased.

Let me also add `lang="en"`.

Meta description tag.

Favicon: inline SVG data URI gold dot on black — nice touch:
`<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'><rect width='32' height='32' fill='%23070707'/><circle cx='16' cy='16' r='5' fill='%23e3b96a'/></svg>">`

Now think about total canvas alpha:false context — with alpha:false, canvas opaque black; fade fill works. Initial fill on resize ✓.

pointerLive flag: set true on first pointermove; also after pointerdown. Initialize mx,my center; before any move, no stir (flag false) — good so hero calm until user moves.

Also on touch, pointermove fires during scroll drags → stirring while scrolling: delightful actually (finger stirs field as you scroll). Keep.

But careful: on touch scroll, pointerdown→moved quickly cancels gather ✓; quick tap (<130ms, no move) triggers smallBurst ✓ playful.

SmallBurst function shared: explode(strengthScale, radiusScale).

Rewrite explode:
```js
function burst(x,y,power,radius){for(const p of parts){const dx=p.x-x,dy=p.y-y,d=Math.hypot(dx,dy)||1;if(d<radius){const imp=(1-d/radius)*power*(1.4+Math.random()*1.6);p.vx+=dx/d*imp;p.vy+=dy/d*imp;}}}
```
Release: burst(gx,gy, 1.2+min(charging,2.5)*1.6, 360+charging*140); tap: burst(gx,gy,1.0,240).

charging caps 3 → power ~5.2, radius 780. Strong satisfying boom. maxSp clamp limits speeds to ~2.8 — explosion visible as wave through clamped velocities + trails. Maybe raise maxSp briefly post-burst: add `boost` variable decaying: maxSp += boost*6; boost*=exp decay. Set boost=1 on burst. Adds drama. Implement: let boost=0; in loop boost*=Math.pow(0.94,nDt)... simpler boost*=0.95 per frame; maxSp=(2.4*vMul+0.4)*(1+boost*2.2).

Held counting only when gStr>0.5 to avoid flicker.

Hint hide on first burst: usedGather flag → hint.classList.add('gone').

Also while holding, readout shows HELD count — implemented via held var.

Space gather: gx,gy=center; wantG includes kb; on keyup burst(center...). Also prevent Space triggering focused button clicks — buttons exist (rail); Space on focused rail button would both click & gather. Minor; acceptable. Actually keydown handler with e.code==='Space': e.preventDefault() prevents button activation too (activation happens on keyup for space? Button activates on keydown? For space, activation on keyup, and preventDefault on keydown prevents scroll; keyup still fires click? If keydown prevented, browsers typically still fire click on keyup for space... inconsistent. Guard: if(document.activeElement&&document.activeElement.tagName==='BUTTON')skip gather. Fine detail, include cheaply.

Resize: rebuild sizes, respawn out-of-bound naturally; also re-measure sections; canvas refilled black (trails cleared — acceptable).

iOS: pointer events supported modern ✓.

Prevent text selection during hold-drag on desktop: holding class → user-select none globally while holding:
```css
body.holding{user-select:none}
```

Cursor JS:
```js
if(!TOUCH){ dot,ring els; tx,ty lerp; on frame: rx+=(mx-rx)*0.16 ... apply transform translate3d. hovering detection: mouseover on [data-hover] via delegation: document.addEventListener('mouseover',e=>{hovering=!!e.target.closest('[data-hover]')}); toggle class on .cursor.
holding class from body.holding sync.
Hide until first move: opacity 0 → 1 on first pointermove.
mouseleave document → hide.
```

Assemble readout chapter names: ['O','I — DUST','II — FLOW','III — STILLNESS','IV — AFTERGLOW']? Hero label: 'Nº 01'. Active detection: nearest section center among 5.

```js
function activeChapter(){const c=scrollY+vh/2;let best=0,bd=1e9;secs.forEach((s,i)=>{const cen=s.top+s.h/2;const d=Math.abs(cen-c);if(d<bd){bd=d;best=i}});return best;}
```
Update tick classes & readout prefix & maybe rail label. Only touch DOM when changed.

secs measured in measure(): secs = ids.map(id=>{el=$('#'+id);return {el,top:el.offsetTop,h:el.offsetHeight}}).

Ghost parallax uses secs entries for chapters with ghost child: store ghostEls with their section index.

Alright — also `overscroll-behavior:none` on html to avoid rubber-band showing white? html bg dark anyway.

Print? skip.

Let me now also double-check "no gradients as primary device": my gradients: vignette radial (atmospheric shading, essentially invisible as "gradient"), that's it. Colors flat elsewhere. Good. No emoji anywhere ✓. Icons: none needed (no icon library necessary — nothing requires icons; rail ticks are CSS lines). Fonts distinctive ✓. Layout editorial asymmetric ✓. All interactive wired ✓. No alerts ✓.

One more consideration — the "signature moment": the gather-and-release with orbiting spiral convergence + HUD counter + explosion is the signature. Also the living readout/clock instrumentation. Good.

Estimate hero title responsiveness: 7 letters Italiana at 13vw each ~0.5em width → total ≈ 7*0.55*13vw ≈ 50vw + spacing .08em*6 ≈ +6vw ≈ 56vw wide. Left-aligned at 9vw margin → ends 65vw. Fine. Mobile 720: clamp floor 64px → 7 chars*~0.55*64 ≈ 250px + spacing ≈ 290px fits 375px? 64px*0.58*7=260 + ls .06em*6*64≈23 → ~283px + margin 7vw(26px) = 309 < 375 ✓. Use clamp(58px,13vw,188px).

Sub width constrain 46ch.

Vertical rhythm hero: stage positioned center-left: hero{min-height:100svh;display:flex;align-items:center;padding:0 9vw} stage margin-top:-4vh optical.

Cue absolute bottom:34px left:50% translateX(-50%).

Chapter vertical: padding:24vh 9vw; min-height:115vh; display flex align center. Right variant: justify-content:flex-end; text-align:left (block right). Ghost positions: odd → right:4vw top:50% translateY(-50%); even → left:4vw. With parallax overriding transform translateY! Conflict: parallax sets transform each frame, killing centering translateY. Solution: position ghost with top:calc(50% - 0.5em)? font-size huge so 0.5em unknown relative to section height... Instead wrap: outer .ghost-wrap absolute centered (top:50%;transform:translateY(-50%)) and inner .ghost receives parallax transform. Clean. Implement wrap div.

Or simpler: parallax writes to CSS var --py and transform:translateY(calc(-50% + var(--py)))? Setting style.setProperty('--py',...) per frame — fine too. I'll do wrapper approach: .ghost-wrap{position:absolute;top:50%;} inner transform translateY(-50%) translate parallax combined in JS string: `translate3d(0, calc(-50% + ${y}px),0)`? calc inside translate3d works. Even simpler: JS sets transform:`translateY(${-gh/2 + y}px)` where gh=ghost.offsetHeight — measurable. Do that: wrap at top:50% only; JS composes -h/2 offset + parallax. Cache gh on measure.

Even simpler: skip perfect centering; place ghosts with top:8vh / bottom anchored per design (numeral bleeding off top-right looks editorial). Fixed top:-4vw right:2vw etc. Then parallax pure translateY. Yes — bleed off edges deliberately:
- ch1 ghost I: top:-6vw; right:2vw
- ch2 ghost II: bottom:-8vw; left:2vw (bottom-anchored: use bottom property; parallax transform independent ✓)
- ch3 ghost III: top:-6vw; left:38vw? vary. 
Set per-section via nth-of-type CSS. Parallax transform translateY only ✓ no conflict.

Ghost font-size: 46vw capped 520px. Opacity stroke .09. For II (two glyphs) size smaller 38vw.

Finale: no ghost.

OK also add slight rotation to ghosts? No.

Now finalize copy wording (grammar):

Ch II body refine: “There is no choreography here. A single mathematical breath — noise folded into current — decides every turn. What reads as grace is arithmetic, repeated sixteen hundred times a frame, patiently, in the dark.” ✓

Ch III add second sentence referencing reader's stillness ✓ drafted.

Hero sub: “Sixteen hundred motes of light adrift in an invisible wind — rendered live, never twice the same.” Split lines with <br>, second line italic gold? em gold: “never twice the same.” Keep em ivory italic; gold reserved for headings em + kickers. Hmm gold em in sub could be pretty: make whole sub ivory .7, em italic gold-bright. Yes.

Colophon back-button style: mono, gold, border-bottom hairline, hover → border-color gold & color bright. Include ↑? Arrow char "↑" is typographic, acceptable (not emoji). "RETURN TO THE FIRST DARK ↑"? Keep without arrow; add "↑" fine. I'll include ↖? Just text.

Double-check no leftover TODOs; wire everything.

Write CSS carefully now (mental compile):

Root vars, resets, body bg #070707 color ivory font Cormorant.

h1,h2 margin 0. p margin 0.

Buttons inherit font.

Canvas: position:fixed;inset:0;width:100%;height:100%;opacity:0;transition:opacity 2.2s ease .2s; body.ready canvas{opacity:1}? Selector: body.ready #field. Also JS-independent fallback if JS fails: page still shows text (canvas empty black) — acceptable; add <noscript> message? Tiny: noscript centered note "This nocturne needs JavaScript." Add politely.

Main z-index above canvas: main{position:relative;z-index:2}.

HUD hidden until ready: .hud,.rail,.readout,.hint{opacity:0;transition:opacity 1.2s ease var(--d)} body.ready → opacity 1 with delays 1.6/1.8/2/2.3s. Hint also has pulsing animation on inner span; gate animation after ready. Simplify: hint pulse via animation on .hint span infinite; container opacity transition.

Careful: .hint.gone{opacity:0!important;pointer-events:none}.

Rail dot transition top .3s linear ok.

Focus-visible outlines gold.

Media ≤720: paddings 24px; rail right:14px height 30vh; readout font 9px bottom 20 left 20; hud padding 20px 22px; hide .no? keep; ghost sizes 60vw; chapter padding 18vh 7vw; head clamp handles; body 17px; cue bottom 22.

Very short screens landscape phones: fine.

Also max-width 1920 center? Full-bleed fine; maybe cap content measure only.

Now JS init order: define everything, measure() after DOM (script at end body) + fonts.ready re-measure. Start rAF immediately (particles visible once canvas fades in). scrollP init via onScroll(). tick() clock. Build nothing dynamically except maybe rail buttons hardcoded in HTML ✓.

Potential bug watch: `paramsAt` when scrollP exactly 1 → loop finds segment [0.70,1.00] since p<=b.p inclusive ✓.

noise input scale: p.x*ns with ns~0.002 → coordinate range W*0.002 ≈ 3.8 across screen — good variation. Time tz grows unbounded — noise fine with large inputs for a while (precision degrades after ~1e6? tz rate 0.0002/frame*60fps=0.012/s → 43/hour. Fine.)

Angle multiplier 2.4π? noise∈[-1,1] → angle∈[-2.4π,2.4π] wraps fine giving richer directional distribution ✓.

Swirl term sign: (-dym,dxm) is CCW around mouse ✓ pleasing.

Gather spiral: pull toward + perpendicular*0.9 → inspiraling orbit ✓. As dg→0 pull→gStr*0.5*0.55≈0.28 mild; particles near center jitter-orbit tightly; held counts d<70 ✓. They'll form glowing knot with trails — beautiful. Some slingshot out due to tangential overshoot then recaptured — dynamic comet swarm. 

Explosion boost & clamp interplay ok.

Trail fade during stillness 0.026 → very long silky trails; with slow v 0.22, motion subtle ✓ meditative.

Hero p=0 params calm ✓. Between hero and dust scrollP small.

Section heights: hero 100svh; chapters 115vh; finale 105vh → total ≈ 450vh; scrollable 350vh. Stop positions map roughly to chapters (0, .2, .46, .70, 1) approx aligned with centers given proportions: cumulative tops: hero 0-100, dust 100-215, flow 215-330, still 330-445, after 445-550 (vh). Centers: 50,157,272,387,497 → /450: .11,.35,.60,.86,1.10?? scrollP max = (550-100)/450=1 at end. Viewport-center method for active chapter independent of STOPS p-values; STOPS are aesthetic interpolation over p — mismatch between chapter positions and STOPS breakpoints means e.g. "stillness" calm hits at p .70 while stillness center at .86. Recompute STOPS to match layout fractions: centers at p≈ .0(hero top? hero center .11), dust .35, flow .60, still .86, end 1.0. Design STOPS keyed: 0:calm, .35 dust(slow big), .60 flow(fast), .86 still(very slow), 1: gentle rise. Adjust:

```js
{p:0.00,v:0.95,ns:0.0017,f:0.055,fd:0.075,sw:0.5},
{p:0.34,v:0.60,ns:0.0028,f:0.040,fd:0.050,sw:0.65},
{p:0.60,v:1.50,ns:0.0037,f:0.088,fd:0.095,sw:0.85},
{p:0.86,v:0.20,ns:0.0010,f:0.026,fd:0.024,sw:0.28},
{p:1.00,v:0.85,ns:0.0020,f:0.058,fd:0.065,sw:0.5},
```
✓.

vh var for JS = innerHeight.

measure() also caches ghost heights & section refs; call on resize & load & fonts.ready & after 300ms safety.

Ghost elements: give each an id-less class; JS: $$('.ghost').map(el=>({el,sec:el.closest('section')})). Parallax: y=(scrollY - (secTop - vh)) * -0.07 → when section enters, ghost slides. Compute rel=(scrollY+vh - top)/(vh+h) ∈0..1 → y=(rel-0.5)*±60px. Direction alternate? Keep uniform -0.5 factor: y=(rel-.5)*-90px → drifts up as you pass. Cache secTop/secH from secs by matching section element. Map via dataset index: assign sections order array SECS=[hero,dust,flow,still,after]; ghosts reference index via closest lookup each measure.

Implement measure():
```js
SECS=$$('.hero,.chapter,.finale') in DOM order → store {el,top,offsetHeight}
GHOSTS=$$('.ghost').map(el=>({el,s:SECS.find(s=>s.el===el.closest('section'))}))
```

Frame-loop parallax each frame using cached tops ✓ cheap.

Active chapter for readout: use SECS centers ✓. Labels array: ['Nº 01 — OVERTURE','I — DUST','II — FLOW','III — STILLNESS','IV — AFTERGLOW']. Finale labeled IV AFTERGLOW (it's the fourth movement — consistent!). Rail ticks 5 ✓ aria labels adjust finale "Movement IV".

So chapters named movements: kicker texts: "MOVEMENT I — DUST" etc. Nice musical nocturne coherence! Update kickers: MOVEMENT I — DUST / MOVEMENT II — FLOW / MOVEMENT III — STILLNESS. Finale kicker: "CODA — AFTERGLOW". Ghost numerals I II III ✓. Readout labels: 'OVERTURE','I · DUST','II · FLOW','III · STILLNESS','CODA'.

Headline for finale references ending ✓.

Hint text: "PRESS & HOLD TO GATHER THE LIGHT" single line mono; on touch same wording works ("press & hold").

I think spec is complete & consistent. Now write the final file meticulously. Length ~600-700 lines. Ensure encoding of grain SVG data URI correct.

Grain URI (encode: <>#" → %3C %3E %23 %22, spaces %20 or keep? In CSS url("data:image/svg+xml,...") spaces allowed inside quoted string generally, but safest encode spaces too? Most browsers accept unencoded spaces within quoted data URI for svg+xml utf8. I'll encode critical chars only (#, <, >) and keep spaces — widely used pattern (e.g., heropatterns) works. Use single quotes in SVG attrs.

Compose: 
url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='240' height='240'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.82' numOctaves='2' stitchTiles='stitch'/%3E%3CfeColorMatrix type='saturate' values='0'/%3E%3C/filter%3E%3Crect width='240' height='240' filter='url(%23n)' opacity='.6'/%3E%3C/svg%3E")

Favicon similar encoded.

Write everything now. Also remember explanation after code, in English (user English). Start response without heading, conversational first line, then code block, then explanation. Keep explanation concise but covering interactions.

One more check on hero title letters with overflow hidden h1: line-height 1 with Italiana caps — ascenders fit; padding-top tiny to avoid clipping? Italiana caps sit within em box; line-height .98 might clip top of letters? Set line-height 1.06 & overflow hidden clips only below baseline area... translateY(115%) start ensures hidden; final position must be fully visible: with line-height 1.06 no vertical clipping of caps. Add padding:0.02em top safe.

Letter-spacing on h1 .07em; last-letter trailing space negligible.

Also add slight per-letter hover? Letters aren't interactive; skip (data-hover on title could scale ring—cute: make title data-hover? It'd imply clickability. Skip.)

Rail dot initial top 0%.

Ensure readout doesn't overlap rail on mobile: readout left, fine.

For performance ensure no layout thrash: parallax uses cached tops ✓; active chapter computed on scroll event using cached ✓.

getComputedStyle none needed.

Write code.

Additional polish idea: page <title> and meta theme-color ✓.

During writing, maintain consistent naming. Let me write the entire HTML now in final form, carefully proofreading JS syntax as I go (no TS). I'll count braces mentally per function.

Also: `ctx.getContext('2d',{alpha:false})` then CSS background not needed but keep body bg.

For pointermove stir we need pointerLive true also on pointerdown (tap without move) — set in down handler ✓.

Edge: multi-touch — ignore secondary pointers (track primary only): if(e.isPrimary===false)return on handlers. Add.

Blur event: window 'blur' → cancel hold (explode softly? just cancel: mDown=false,gStr target 0; if gStr was high, do burst for fun) — do burst if gStr>0.3.

Keydown also ignore when metaKey/ctrl.

Final readout string building each 6 frames — allocate small strings fine.

Numbers formatting helper fmt(n,d).

OK writing deliverable now. Also after code: explanation of features + interaction guide. Keep it tight (~10 bullet-ish lines). And a brief intro line before code stating concept. Total response big but fine.

Let me write out the code.

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="theme-color" content="#070707">
<meta name="description" content="AURELIA — a generative nocturne. Sixteen hundred motes of light, simulated live in your browser.">
<title>AURELIA — a generative nocturne</title>
<link rel="icon" href="data:image/svg+xml,...">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,500;1,400;1,500&family=IBM+Plex+Mono:wght@400;500&family=Italiana&display=swap" rel="stylesheet">
<style> ... </style>
</head>
<body>
...
<script> ... </script>
</body>
</html>
```

CSS full draft:

```css
:root{
 --bg:#070707; --ink:#eae4d6; --ink-60:rgba(234,228,214,.6); --ink-35:rgba(234,228,214,.35);
 --mut:#8f887a; --gold:#c9a15a; --gold-b:#e6bd6e; --hair:rgba(234,228,214,.16);
 --disp:'Italiana',serif; --serif:'Cormorant Garamond',Georgia,serif; --mono:'IBM Plex Mono',ui-monospace,monospace;
 --ease:cubic-bezier(.22,1,.36,1);
}
*{box-sizing:border-box;margin:0;padding:0}
html{background:var(--bg);scroll-behavior:auto;-webkit-text-size-adjust:100%}
body{background:var(--bg);color:var(--ink);font-family:var(--serif);overflow-x:hidden;min-height:100vh;touch-action:pan-y}
body.holding{user-select:none;-webkit-user-select:none}
::selection{background:var(--gold);color:#141008}
:focus-visible{outline:1px solid var(--gold);outline-offset:4px}
::-webkit-scrollbar{width:9px}::-webkit-scrollbar-track{background:#0a0a09}::-webkit-scrollbar-thumb{background:#26231d;border-radius:9px;border:2px solid #0a0a09}

#field{position:fixed;inset:0;width:100%;height:100%;z-index:0;opacity:0;transition:opacity 2.4s ease .15s}
body.ready #field{opacity:1}
.vignette{position:fixed;inset:0;z-index:1;pointer-events:none;background:radial-gradient(130% 95% at 50% 44%,transparent 58%,rgba(0,0,0,.5) 100%)}
main{position:relative;z-index:2}

/* grain */
.grain{position:fixed;inset:-60%;width:220%;height:220%;z-index:7;pointer-events:none;opacity:.05;background:url("data:image/svg+xml,...") repeat;background-size:230px 230px;animation:grain 7s steps(8) infinite}
@keyframes grain{
 0%{transform:translate3d(0,0,0)}
 12.5%{transform:translate3d(-1.5%,1%,0)}
 25%{transform:translate3d(1%,-1.5%,0)}
 37.5%{transform:translate3d(-1%,-1%,0)}
 50%{transform:translate3d(1.5%,1.5%,0)}
 62.5%{transform:translate3d(-1.5%,-.5%,0)}
 75%{transform:translate3d(.5%,1.5%,0)}
 87.5%{transform:translate3d(-.5%,-1.5%,0)}
 100%{transform:translate3d(0,0,0)}
}

/* HUD */
.hud{position:fixed;top:0;left:0;right:0;z-index:5;display:flex;justify-content:space-between;align-items:center;padding:26px 34px;pointer-events:none;font-family:var(--mono);opacity:0;transition:opacity 1.4s ease 1.5s}
body.ready .hud{opacity:1}
.mark{pointer-events:auto;background:none;border:0;color:var(--ink);font-family:var(--mono);font-size:11px;letter-spacing:.34em;display:flex;align-items:center;gap:10px;padding:6px 0}
.mark .dot{color:var(--gold)}
.mark .no{color:var(--mut);font-size:10px;letter-spacing:.22em}
.clock{font-size:10px;letter-spacing:.22em;color:var(--mut)}

/* rail */
.rail{position:fixed;right:30px;top:50%;transform:translateY(-50%);height:36vh;z-index:5;opacity:0;transition:opacity 1.4s ease 1.7s}
body.ready .rail{opacity:1}
.rail-track{position:absolute;left:50%;top:0;bottom:0;width:1px;background:var(--hair)}
.rail-dot{position:absolute;left:50%;top:0;width:5px;height:5px;margin-left:-2.5px;margin-top:-2.5px;border-radius:50%;background:var(--gold-b);transition:top .35s linear}
.rail button{position:absolute;left:50%;width:26px;height:14px;transform:translate(-50%,-50%);background:none;border:0;padding:0}
.rail button::before{content:"";position:absolute;left:50%;top:50%;width:12px;height:1px;background:var(--ink-35);transform:translate(-50%,-50%);transition:all .4s var(--ease)}
.rail button.on::before{width:22px;background:var(--gold)}
.rail button:hover::before{background:var(--gold-b)}

.readout{position:fixed;left:34px;bottom:28px;z-index:5;font-family:var(--mono);font-size:10px;letter-spacing:.18em;color:var(--mut);white-space:nowrap;opacity:0;transition:opacity 1.4s ease 1.9s}
body.ready .readout{opacity:1}
.readout b{color:var(--gold);font-weight:500}
.readout .held{color:var(--gold-b)}

.hint{position:fixed;right:34px;bottom:24px;z-index:5;font-family:var(--mono);font-size:10px;letter-spacing:.3em;color:var(--ink-60);border:1px solid var(--hair);padding:11px 16px 10px 19px;opacity:0;transition:opacity 1.2s ease 2.3s,transform 1.2s var(--ease) 2.3s,color .4s;transform:translateY(8px)}
body.ready .hint{opacity:1;transform:none}
.hint em{font-style:normal;color:var(--gold);animation:pulse 2.6s ease-in-out infinite}
.hint.gone{opacity:0!important;transform:translateY(8px)!important;pointer-events:none}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.35}}
```

Wait hint contains "PRESS & HOLD" emphasized + rest. Markup: `<div class="hint"><em>PRESS &amp; HOLD</em>&nbsp;&nbsp;TO GATHER THE LIGHT</div>`.

Sections CSS:

```css
section{position:relative}
.hero{min-height:100vh;min-height:100svh;display:flex;align-items:center;padding:0 9vw}
.hero .stage{max-width:1100px;margin-top:-3vh}
.kicker{font-family:var(--mono);font-size:11px;letter-spacing:.34em;color:var(--gold);display:flex;align-items:center;gap:16px}
.rule{display:inline-block;width:46px;height:1px;background:var(--gold);transform:scaleX(0);transform-origin:left;transition:transform 1.6s var(--ease) calc(var(--d,0s) + .25s)}
.in .rule,body.ready .hero .rule{transform:scaleX(1)}
.title{font-family:var(--disp);font-weight:400;font-size:clamp(58px,13vw,188px);line-height:1.04;letter-spacing:.07em;margin:26px 0 30px -4px;overflow:hidden;padding-top:.06em;white-space:nowrap}
.title .l{display:inline-block;transform:translateY(118%);transition:transform 1.35s var(--ease);transition-delay:var(--d)}
body.ready .title .l{transform:none}
.sub{font-size:clamp(17px,1.6vw,22px);line-height:1.65;color:var(--ink-60);max-width:52ch;font-weight:400}
.sub em{color:var(--gold-b)}
.cue{position:absolute;left:50%;bottom:34px;transform:translateX(-50%);display:flex;flex-direction:column;align-items:center;gap:12px}
.cue-word{font-family:var(--mono);font-size:9px;letter-spacing:.42em;color:var(--mut)}
.cue-line{width:1px;height:54px;background:var(--hair);position:relative;overflow:hidden}
.cue-line::after{content:"";position:absolute;left:0;top:-45%;width:100%;height:45%;background:var(--gold);animation:drip 2.4s cubic-bezier(.65,0,.35,1) infinite}
@keyframes drip{0%{top:-45%}100%{top:110%}}
```
Cue transform conflicts with .rv translateY! .cue has translateX(-50%) plus reveal translateY. Combine: define .cue reveal differently — put reveal on inner wrapper or use left:50% with margin-left negative? Simplest: cue outer positioned (no transform) using left:0;right:0;margin:auto;width:max-content. Then .rv transform free. ✓ .cue{left:0;right:0;margin:0 auto;width:max-content}.

Chapters:

```css
.chapter{min-height:118vh;display:flex;align-items:center;padding:20vh 9vw}
.chapter.right{justify-content:flex-end}
.stage{max-width:600px;position:relative;z-index:2}
.head{font-weight:500;font-size:clamp(42px,5.4vw,84px);line-height:1.04;letter-spacing:-.005em;margin:30px 0 26px}
.head em{font-style:italic;color:var(--gold-b);font-weight:500}
.body{font-style:italic;font-size:clamp(17px,1.45vw,21px);line-height:1.78;color:var(--ink-60);max-width:46ch}
.ghost{position:absolute;z-index:1;font-family:var(--disp);line-height:.8;color:transparent;-webkit-text-stroke:1px rgba(234,228,214,.09);user-select:none;pointer-events:none;font-size:clamp(240px,44vw,540px)}
#dust .ghost{top:-4vw;right:1vw}
#flow .ghost{bottom:-6vw;left:0;font-size:clamp(200px,36vw,440px)}
#still .ghost{top:-5vw;right:6vw}
```
Right-aligned chapter text-align stays left; fine.

Finale:

```css
.finale{min-height:104vh;display:flex;align-items:center;justify-content:center;text-align:center;padding:18vh 8vw}
.finale .stage{max-width:720px}
.finale .kicker{justify-content:center}
.finale .rule{transform-origin:center}
.finale .body{margin:0 auto}
.colophon{margin-top:64px;padding-top:34px;border-top:1px solid var(--hair);display:flex;flex-direction:column;gap:14px;align-items:center;font-family:var(--mono);font-size:9.5px;letter-spacing:.26em;color:var(--mut)}
.back{background:none;border:0;border-bottom:1px solid var(--hair);padding:2px 2px 8px;color:var(--gold);font-family:var(--mono);font-size:10px;letter-spacing:.3em;transition:color .4s,border-color .4s;margin-top:10px}
.back:hover{color:var(--gold-b);border-color:var(--gold)}
```

Reveal:

```css
.rv{opacity:0;transform:translateY(36px);transition:opacity 1.15s var(--ease) var(--d,0s),transform 1.15s var(--ease) var(--d,0s)}
.in .rv{opacity:1;transform:none}
body.ready .hero .rv{opacity:1;transform:none}
```
Hero children have .rv + inline --d; kicker also contains .rule gated by same selectors ✓ (rule selector listed). Cue is .rv with --d 1.9s ✓ (body.ready .hero .rv covers). But cue also had its own transform translateX removed ✓.

Cursor:

```css
.cursor{display:none}
@media (hover:hover) and (pointer:fine){
 body,a,button{cursor:none}
 .cursor{display:block;position:fixed;inset:0;z-index:9;pointer-events:none;opacity:0;transition:opacity .5s}
 body.moved .cursor{opacity:1}
 .cursor i{position:fixed;top:0;left:0;border-radius:50%;will-change:transform}
 .c-dot{width:4px;height:4px;background:var(--gold-b);margin:-2px 0 0 -2px}
 .c-ring{width:30px;height:30px;border:1px solid var(--ink-35);margin:-15px 0 0 -15px;transition:width .35s var(--ease),height .35s var(--ease),margin .35s var(--ease),border-color .35s}
 body.hovering .c-ring{width:46px;height:46px;margin:-23px 0 0 -23px;border-color:var(--gold)}
 body.holding .c-ring{width:12px;height:12px;margin:-6px 0 0 -6px;border-color:var(--gold-b)}
}
```
Ring/dot positioned via transform translate3d(x,y,0) with margins centering ✓ (i elements top/left 0).

noscript:

```css
noscript{position:fixed;inset:0;display:grid;place-items:center;z-index:20;font-family:var(--mono);font-size:11px;letter-spacing:.3em;color:var(--mut);background:var(--bg)}
```

Reduced motion:

```css
@media (prefers-reduced-motion:reduce){
 .grain{animation:none}
 .cue-line::after{animation:none}
 .hint em{animation:none}
 .rv,.title .l,.rule{transition-duration:.01s!important;transition-delay:0s!important}
}
```

Mobile:

```css
@media (max-width:720px){
 .hud{padding:20px 20px}
 .mark{letter-spacing:.26em;font-size:10px}
 .rail{right:16px;height:30vh}
 .readout{left:20px;bottom:20px;font-size:9px;letter-spacing:.14em}
 .hint{right:16px;bottom:74px;font-size:9px;letter-spacing:.22em;padding:9px 12px 8px 15px}
 .hero{padding:0 7vw}
 .title{font-size:clamp(52px,16.5vw,96px)}
 .chapter{padding:16vh 7vw}
 .ghost{font-size:64vw;opacity:.8}
 #flow .ghost{font-size:52vw}
 .finale{padding:14vh 7vw}
}
```
Hint moved up on mobile to avoid overlapping readout? readout left, hint right — same line ok actually; keep bottom:20 both sides. Set hint bottom:20. But small screens width: readout long string may collide hint. Shorten mobile readout? At 9px, string ~ "III · STILLNESS — VEL 0.20 / MOTES 750" ≈ 38ch*5.4px ≈ 205px; hint ~ "PRESS&HOLD TO GATHER THE LIGHT" 30ch*~6.5 ≈ 195px+borders → total 420 > 375 collision! Fix: on mobile hide readout's tail? Make readout max-width & ellipsis ugly. Alternative: mobile hint bottom:64px (above readout) ✓ as drafted (74). Keep 64. And readout truncated via hiding MOTES on tiny: wrap counts in span.count{display:none @mobile}? Simpler: @media hide .ro-ext span. I'll structure readout: `<b id="roCh"></b><span id="roStats"></span>` and stats includes everything; mobile: font 8.5px & letter-spacing .1em → ~170px, hint at bottom:64 no clash ✓.

JS final assembly — write with care:

```js
(()=>{"use strict";
const $=(s,c=document)=>c.querySelector(s);
const $$=(s,c=document)=>Array.from(c.querySelectorAll(s));
const RM=matchMedia("(prefers-reduced-motion: reduce)").matches;
const FINE=matchMedia("(hover: hover) and (pointer: fine)").matches;
const TAU=Math.PI*2;

/* simplex */
const GRAD=new Float32Array([1,1,0,-1,1,0,1,-1,0,-1,-1,0,1,0,1,-1,0,1,1,0,-1,-1,0,-1,0,1,1,0,-1,1,0,1,-1,0,-1,-1]);
class Simplex{constructor(){const p=new Uint8Array(256);for(let i=0;i<256;i++)p[i]=i;let s=42;const rnd=()=>(s=s*16807%2147483647)/2147483647;for(let i=255;i>0;i--){const j=rnd()*(i+1)|0,t=p[i];p[i]=p[j];p[j]=t;}this.perm=new Uint8Array(512);this.pm=new Uint8Array(512);for(let i=0;i<512;i++){this.perm[i]=p[i&255];this.pm[i]=this.perm[i]%12;}}
 n3(x,y,z){const{perm,pm}=this,F=1/3,G=1/6;const sk=(x+y+z)*F,i=Math.floor(x+sk),j=Math.floor(y+sk),k=Math.floor(z+sk);const t=(i+j+k)*G,x0=x-i+t,y0=y-j+t,z0=z-k+t;let i1,j1,k1,i2,j2,k2;
 if(x0>=y0){if(y0>=z0){i1=1;j1=0;k1=0;i2=1;j2=1;k2=0}else if(x0>=z0){i1=1;j1=0;k1=0;i2=1;j2=0;k2=1}else{i1=0;j1=0;k1=1;i2=1;j2=0;k2=1}}else{if(y0<z0){i1=0;j1=0;k1=1;i2=0;j2=1;k2=1}else if(x0<z0){i1=0;j1=1;k1=0;i2=0;j2=1;k2=1}else{i1=0;j1=1;k1=0;i2=1;j2=1;k2=0}}
 const x1=x0-i1+G,y1=y0-j1+G,z1=z0-k1+G,x2=x0-i2+2*G,y2=y0-j2+2*G,z2=z0-k2+2*G,x3=x0-.5,y3=y0-.5,z3=z0-.5,ii=i&255,jj=j&255,kk=k&255;let n=0;
 let q=.6-x0*x0-y0*y0-z0*z0;if(q>0){const g=pm[ii+perm[jj+perm[kk]]]*3;q*=q;n+=q*q*(GRAD[g]*x0+GRAD[g+1]*y0+GRAD[g+2]*z0)}
 q=.6-x1*x1-y1*y1-z1*z1;if(q>0){const g=pm[ii+i1+perm[jj+j1+perm[kk+k1]]]*3;q*=q;n+=q*q*(GRAD[g]*x1+GRAD[g+1]*y1+GRAD[g+2]*z1)}
 q=.6-x2*x2-y2*y2-z2*z2;if(q>0){const g=pm[ii+i2+perm[jj+j2+perm[kk+k2]]]*3;q*=q;n+=q*q*(GRAD[g]*x2+GRAD[g+1]*y2+GRAD[g+2]*z2)}
 q=.6-x3*x3-y3*y3-z3*z3;if(q>0){const g=pm[ii+1+perm[jj+1+perm[kk+1]]]*3;q*=q;n+=q*q*(GRAD[g]*x3+GRAD[g+1]*y3+GRAD[g+2]*z3)}
 return 32*n}}
```
Note x0 = x - (i - t) = x-i+t ✓ I wrote x-i+t ✓.

Rest:

```js
const cv=$("#field"),cx=cv.getContext("2d",{alpha:false});
const noise=new Simplex();
let W=innerWidth,H=innerHeight,DPR=1,VH=H;

const BUCKETS=[
 {c:"233,227,214",a:.26,w:1.0,n:.24},
 {c:"229,187,109",a:.30,w:1.1,n:.24},
 {c:"179,129,71",a:.27,w:1.0,n:.18},
 {c:"201,113,59",a:.28,w:.85,n:.11},
 {c:"149,138,117",a:.20,w:.7,n:.15},
 {c:"246,235,208",a:.5,w:1.6,n:.08}];
const segs=BUCKETS.map(()=>[]);
function pickB(){let r=Math.random();for(let i=0;i<BUCKETS.length;i++){r-=BUCKETS[i].n;if(r<0)return i}return 0}
const BASE=innerWidth<720?760:1600,COUNT=RM?BASE*.35|0:BASE;
const parts=[];function spawn(p){p=p||{};p.x=Math.random()*W;p.y=Math.random()*H;p.px=p.x;p.py=p.y;p.vx=0;p.vy=0;p.b=pickB();p.life=120+Math.random()*320;return p}
for(let i=0;i<COUNT;i++)parts.push(spawn());

const STOPS=[
 {p:0,v:.95,ns:.0017,f:.055,fd:.075,sw:.5},
 {p:.34,v:.6,ns:.0028,f:.04,fd:.05,sw:.65},
 {p:.6,v:1.5,ns:.0037,f:.088,fd:.095,sw:.85},
 {p:.86,v:.2,ns:.001,f:.026,fd:.024,sw:.28},
 {p:1,v:.85,ns:.002,f:.058,fd:.065,sw:.5}];
function paramsAt(p){let a=STOPS[0],b=STOPS[STOPS.length-1];for(let i=0;i<STOPS.length-1;i++){if(p>=STOPS[i].p&&p<=STOPS[i+1].p){a=STOPS[i];b=STOPS[i+1];break}}let t=(p-a.p)/((b.p-a.p)||1);t=t<0?0:t>1?1:t;t=t*t*(3-2*t);return{v:a.v+(b.v-a.v)*t,ns:a.ns+(b.ns-a.ns)*t,f:a.f+(b.f-a.f)*t,fd:a.fd+(b.fd-a.fd)*t,sw:a.sw+(b.sw-a.sw)*t}}

const cur={v:.95,ns:.0017,f:.055,fd:.075,sw:.5};
let scrollP=0,tz=Math.random()*97,boost=0,held=0,fc=0;
let mx=W/2,my=H*.46,live=false;
let down=false,moved=false,sx0=0,sy0=0,gx=W/2,gy=H*.46,pdT=0,gStr=0,chg=0,kb=false,used=false;
```

resize:

```js
function resize(){W=innerWidth;H=innerHeight;VH=H;DPR=Math.min(devicePixelRatio||1,1.75);cv.width=Math.round(W*DPR);cv.height=Math.round(H*DPR);cx.setTransform(DPR,0,0,DPR,0,0);cx.fillStyle="#070707";cx.fillRect(0,0,W,H);measure()}
addEventListener("resize",resize);
```

sections measure:

```js
const SEC_IDS=["hero","dust","flow","still","after"];
const LABELS=["OVERTURE","I · DUST","II · FLOW","III · STILLNESS","CODA"];
let SECS=[],GHOSTS=[];
function measure(){SECS=SEC_IDS.map(id=>{const el=document.getElementById(id);return{el,top:el.offsetTop,h:el.offsetHeight}});GHOSTS=$$(".ghost").map(el=>({el,s:SECS.find(s=>s.el===el.closest("section"))}))}
```
offsetTop of section relative to body ✓ (no positioned ancestors between? main is position:relative → offsetParent chain: section offsetParent = main? offsetTop then relative to main; main top = 0 anyway since main starts at doc top (no header in flow). main has no top offset ✓ safe.)

active chapter:

```js
let actCh=-1;
function chapterAt(){const c=scrollY+VH/2;let best=0,bd=1e18;for(let i=0;i<SECS.length;i++){const s=SECS[i],d=Math.abs(s.top+s.h/2-c);if(d<bd){bd=d;best=i}}return best}
const ticks=$$(".rail button");
function onScroll(){const max=document.documentElement.scrollHeight-VH;scrollP=max>0?Math.min(1,scrollY/max):0;$("#railDot").style.top=(scrollP*100)+"%";
 const ci=chapterAt();if(ci!==actCh){actCh=ci;ticks.forEach((t,i)=>t.classList.toggle("on",i===ci));$("#roCh").textContent=LABELS[ci];}}
addEventListener("scroll",onScroll,{passive:true});
```

burst:

```js
function burst(x,y,pw,rad){boost=Math.min(boost+.9,1.6);for(let i=0;i<parts.length;i++){const p=parts[i],dx=p.x-x,dy=p.y-y,d=Math.sqrt(dx*dx+dy*dy)||1;if(d<rad){const im=(1-d/rad)*pw*(1.4+Math.random()*1.6);p.vx+=dx/d*im;p.vy+=dy/d*im}}if(!used){used=true;$("#hint").classList.add("gone")}}
```

pointer:

```js
addEventListener("pointermove",e=>{if(e.isPrimary===false)return;mx=e.clientX;my=e.clientY;live=true;document.body.classList.add("moved");
 if(down&&!moved&&e.pointerType!=="mouse"){const dx=e.clientX-sx0,dy=e.clientY-sy0;if(dx*dx+dy*dy>196)moved=true}},{passive:true});
addEventListener("pointerdown",e=>{if(e.isPrimary===false)return;if(e.pointerType==="mouse"&&e.button!==0)return;down=true;moved=false;sx0=e.clientX;sy0=e.clientY;gx=e.clientX;gy=e.clientY;pdT=performance.now();live=true;document.body.classList.add("holding");document.body.classList.add("moved")});
function release(){if(!down&&!kb)return;const dur=performance.now()-pdT;
 if(gStr>.12)burst(gx,gy,1.15+Math.min(chg,2.5)*1.6,340+chg*150);
 else if(down&&!moved&&dur<140)burst(gx,gy,1.05,230);
 down=false;kb=false;gStr=0;chg=0;held=0;document.body.classList.remove("holding")}
addEventListener("pointerup",release);addEventListener("pointercancel",release);
addEventListener("blur",()=>{if(gStr>.3)burst(gx,gy,1.2,300);down=false;kb=false;gStr=0;chg=0;document.body.classList.remove("holding")});
addEventListener("keydown",e=>{if(e.code!=="Space"||e.repeat)return;const ae=document.activeElement;if(ae&&ae.tagName==="BUTTON")return;e.preventDefault();kb=true;gx=W/2;gy=VH*.52;pdT=performance.now();document.body.classList.add("holding")});
addEventListener("keyup",e=>{if(e.code!=="Space")return;e.preventDefault();release()});
```
Note release() checks kb too ✓ (condition `!down&&!kb` return).

Wait release when kb true but down false: dur uses pdT set at keydown ✓.

frame:

```js
let last=performance.now();
function frame(now){requestAnimationFrame(frame);const dt=Math.min(now-last,48);last=now;if(document.hidden)return;fc++;
 const tg=paramsAt(scrollP),k=.05;
 cur.v+=(tg.v-cur.v)*k;cur.ns+=(tg.ns-cur.ns)*k;cur.f+=(tg.f-cur.f)*k;cur.fd+=(tg.fd-cur.fd)*k;cur.sw+=(tg.sw-cur.sw)*k;
 const vm=cur.v*(RM?.55:1);
 tz+=dt*11e-5*(.45+vm*.55);
 const want=(down&&!moved&&now-pdT>130)||kb;
 gStr+=((want?1:0)-gStr)*.075;if(want)chg+=dt/1000;
 boost*=.955;held=0;

 cx.globalCompositeOperation="source-over";
 cx.fillStyle="rgba(7,7,7,"+(cur.fd*(RM?1.7:1)).toFixed(3)+")";
 cx.fillRect(0,0,W,H);
 cx.globalCompositeOperation="lighter";cx.lineCap="round";
 for(let i=0;i<segs.length;i++)segs[i].length=0;

 const ns=cur.ns,F=cur.f,sw=cur.sw,R=Math.min(W,H)*.22,R2=R*R,md=.93;
 const ms=(2.4*vm+.4)*(1+boost*2.4),ms2=ms*ms,nd=dt/16.7;

 for(let i=0;i<parts.length;i++){const p=parts[i];
  const a=noise.n3(p.x*ns,p.y*ns,tz)*7.5;
  p.vx+=Math.cos(a)*F*nd;p.vy+=Math.sin(a)*F*nd;
  if(live){const dx=p.x-mx,dy=p.y-my,d2=dx*dx+dy*dy;
   if(d2<R2){const d=Math.sqrt(d2)||1,fl=1-d/R;
    p.vx+=(-dy/d*sw*.9+dx/d*.12)*fl*nd;p.vy+=(dx/d*sw*.9+dy/d*.12)*fl*nd}}
  if(gStr>.02){const dx=gx-p.x,dy=gy-p.y,d=Math.sqrt(dx*dx+dy*dy)||1;
   const pl=gStr*(.28+1.05*Math.min(1,d/300));
   p.vx+=(dx/d*pl-dy/d*pl*.9)*nd;p.vy+=(dy/d*pl+dx/d*pl*.9)*nd;
   if(d<70&&gStr>.5)held++}
  p.vx*=md;p.vy*=md;const s2=p.vx*p.vx+p.vy*p.vy;
  if(s2>ms2){const kk=ms/Math.sqrt(s2);p.vx*=kk;p.vy*=kk}
  p.x+=p.vx*nd*vm;p.y+=p.vy*nd*vm;p.life-=nd;
  if(p.life<=0||p.x<-24||p.x>W+24||p.y<-24||p.y>H+24){spawn(p);continue}
  segs[p.b].push(p.px,p.py,p.x,p.y);p.px=p.x;p.py=p.py? ...}
```
typo watch: p.py=p.y ✓.

```js
 for(let b=0;b<BUCKETS.length;b++){const arr=segs[b];if(!arr.length)continue;const B=BUCKETS[b];
  cx.strokeStyle="rgba("+B.c+","+B.a+")";cx.lineWidth=B.w;cx.beginPath();
  for(let i=0;i<arr.length;i+=4){cx.moveTo(arr[i],arr[i+1]);cx.lineTo(arr[i+2],arr[i+3])}
  cx.stroke()}

 /* ghosts parallax */
 for(let i=0;i<GHOSTS.length;i++){const g=GHOSTS[i];if(!g.s)continue;
  const rel=(scrollY+VH-g.s.top)/(VH+g.s.h);const y=(rel-.5)*-110;
  g.el.style.transform="translate3d(0,"+y.toFixed(1)+"px,0)"}

 /* readout */
 if(fc%6===0){let s="VEL "+cur.v.toFixed(2)+" · FLD "+(cur.f*100).toFixed(0)+" · TRB "+(cur.ns*1e3).toFixed(1)+" · "+parts.length+" MOTES";
  if(held>0)s+=" · <span class='held'>HELD "+held+"</span>";
  $("#roStats").innerHTML=s}
}
```
noise angle: *7.5 rad range ±7.5 ✓.

Readout innerHTML with span — fine (static strings).

Ghost transform overrides nothing ✓.

Cursor:

```js
if(FINE){const dotEl=document.createElement("i"),ringEl=document.createElement("i");dotEl.className="c-dot";ringEl.className="c-ring";const cw=document.createElement("div");cw.className="cursor";cw.append(dotEl,ringEl);document.body.appendChild(cw);
 let rx=mx,ry=my;
 (function cl(){rx+=(mx-rx)*.16;ry+=(my-ry)*.16;dotEl.style.transform="translate3d("+mx+"px,"+my+"px,0)";ringEl.style.transform="translate3d("+rx.toFixed(1)+"px,"+ry.toFixed(1)+"px,0)";requestAnimationFrame(cl)})();
 document.addEventListener("mouseover",e=>{document.body.classList.toggle("hovering",!!(e.target.closest&&e.target.closest("[data-hover]")))});
 document.documentElement.addEventListener("mouseleave",()=>document.body.classList.remove("moved"));
}
```
body.moved controls cursor opacity & also used for pointer... moved flag separate variable name clash! I used `moved` for gather-cancel AND body class "moved" for cursor visibility. Rename cursor class to "ptr". body.ptr .cursor{opacity:1}. And mouseleave removes ptr. ✓ rename.

Also .cursor appended via JS — CSS .cursor defined ✓.

Clock:

```js
const clockEl=$("#clock");
function tick(){const d=new Date(),z=n=>String(n).padStart(2,"0"),off=-d.getTimezoneOffset(),sg=off<0?"−":"+",ao=Math.abs(off);clockEl.textContent=z(d.getHours())+":"+z(d.getMinutes())+":"+z(d.getSeconds())+" UTC"+sg+z(ao/60|0)+(ao%60?":"+z(ao%60):"")}
tick();setInterval(tick,1000);
```
ao%60 number → padStart on String needed: z(ao%60) z handles ✓. ao/60|0 precedence: ao/60|0 = (ao/60)|0 ✓.

Nav:

```js
ticks.forEach((t,i)=>t.addEventListener("click",()=>SECS[i].el.scrollIntoView({behavior:RM?"auto":"smooth"})));
$("#mark").addEventListener("click",()=>scrollTo({top:0,behavior:RM?"auto":"smooth"}));
$("#back").addEventListener("click",()=>scrollTo({top:0,behavior:RM?"auto":"smooth"}));
```
ticks correspond SECS order ✓ (5 buttons).

Reveal IO:

```js
const io=new IntersectionObserver(es=>{for(const e of es)e.target.classList.toggle("in",e.isIntersecting)},{threshold:.25});
$$(".rv-group").forEach(el=>io.observe(el));
```
Threshold .25 of stage block ✓.

Ready:

```js
function go(){document.body.classList.add("ready")}
if(document.fonts&&document.fonts.ready){document.fonts.ready.then(()=>setTimeout(go,60))}
setTimeout(go,1900);
setTimeout(measure,400);measure();onScroll();resize();
requestAnimationFrame(frame);
```
resize() calls measure ✓ duplicates fine.

Order: define functions before calls. Script at end of body; DOM ready.

HTML body content — finalize with all ids/classes & inline --d values:

Hero letters delays: base .35 step .05: A .30 U .36 R .42 E .48 L .54 I .60 A .66.

Everything cohesive. Also add aria-hidden to ghosts/vignette/grain/canvas/readout/clock/hint? hint informative-ish; keep accessible (aria-live none). fine.

Noscript text: "THIS NOCTURNE REQUIRES JAVASCRIPT — THE LIGHT CANNOT KINDLE WITHOUT IT". Nice.

Also `<html lang="en">`.

Check hint em pulse gated until ready: animation runs while opacity 0 — harmless.

One more: body.ptr class CSS rename:

```css
body.ptr .cursor{opacity:1}
```

And in pointermove add classList.add("ptr").

mouseleave on documentElement → remove ptr ✓.

Also when hovering rail buttons etc, [data-hover] present on: mark, rail buttons, back. Add data-hover attrs in HTML ✓.

Double-check .rv-group on stages: hero stage NOT rv-group (uses body.ready) ✓; chapter stages & finale stage have class "stage rv-group".

Rule inside kicker: transition-delay calc(var(--d) + .25s) — --d inherited from kicker's inline style ✓ (custom props inherit).

Title letters: h1 overflow hidden — but .rv? Title itself not .rv (letters animate). ✓.

Sub uses .rv with --d 1.15s. Kicker .rv --d .1s.

Cue .rv --d 2s. Cue inside hero (absolute) — body.ready .hero .rv covers ✓.

Chapter .rv delays 0/.08/.16 inline.

Finale delays 0/.08/.16/.24.

Ghost z-index 1 vs stage z 2 ✓; ghost inside section (position relative) ✓ absolute within.

Chapter right variant: `<section class="chapter right" id="flow">`.

Ghost placements CSS per id ✓ defined.

Potential overflow: ghost huge at right:1vw with font 44vw — width of "I" glyph narrow ✓; "III" at right:6vw width ~3 glyphs*~0.3em*44vw ≈ 40vw ok; "II" 36vw fine.

overflow-x hidden on body guards bleed ✓; also ghosts inside sections could extend past right edge causing scrollbar? body overflow-x hidden handles ✓. html too: add overflow-x:hidden? body enough usually; add to html for safety? html{overflow-x:hidden} can break position sticky none used ✓ safe. Add.

Vertical: ghost top:-4vw extends above section into previous — visible overlap intended, fine (z-index under text).

Finally verify no forbidden vibes: dark bg with ivory text — contrast strong ✓. No blue/purple ✓. Gradients: only vignette radial (functional shading) ✓. Emoji none ✓. Arrows: none except maybe none. "·" middots fine. "—" em dashes fine. "Nº" masculine ordinal — fine typographically.

Explanation section afterward: describe concept, interactions (move/stir, press-hold gather w/ counter, release burst, spacebar, scroll morphing chapters, rail nav, live readout/clock), tech notes (simplex noise flow field, additive canvas, batched strokes, DPR cap, reduced-motion, mobile). Keep succinct.

Let me also sanity-check the fade+lighter combo brightness equilibrium: each frame adds strokes alpha ~.3 per particle passing; fade removes 7.5%/frame. Steady-state glow moderate. Spark bucket .5 alpha w/ 1.6 width gives occasional bright strands ✓.

Line width <1 with DPR scaling: ctx transform scales, effective hairlines crisp ✓.

One risk: 'lighter' + many overlapping segments in gather knot → blows to white blob momentarily. Alpha .3 accumulates ~ tens of overlaps → saturates to white core with gold fringe — actually looks like a hot star; desirable!

Trail color persistence: fade uses bg rgba fill — since canvas opaque, fine ✓.

iOS Safari: 'lighter' supported ✓. Pointer Events iOS 13+ ✓.

devicePixelRatio cap 1.75 ok perf.

Now, finally write the complete response. Intro sentence: "Here's my take: AURELIA — a generative nocturne..." then code, then explanation.

Writing HTML title letters block contiguously:
`<span class="l" style="--d:.30s">A</span><span class="l" style="--d:.36s">U</span><span class="l" style="--d:.42s">R</span><span class="l" style="--d:.48s">E</span><span class="l" style="--d:.54s">L</span><span class="l" style="--d:.60s">I</span><span class="l" style="--d:.66s">A</span>`

Rail buttons markup with style top: i*25%:
```html
<button style="top:0%" data-t="0" data-hover aria-label="Overture"></button>
<button style="top:25%" ... aria-label="Movement I — Dust"></button>
... 50,75,100
```
JS uses index order ✓ (query order matches).

Readout: `<div class="readout"><b id="roCh">OVERTURE</b><span id="roStats"></span></div>` with gap styling: .readout b{margin-right:14px}.

Initial roStats blank until first frame ✓.

Also add `will-change: transform` sparingly (cursor, ghosts).

I believe design is solid. Compose final answer. Code length ~ acceptable. Ensure I escape & in HTML text (&amp;) where needed: "PRESS &amp; HOLD", "ITALIANA &amp; CORMORANT".

In JS strings with "·" fine unicode.

Also the − minus sign in UTC offset uses U+2212 fine.

Write it.