import bpy, bmesh, math, random, os
import numpy as np
from mathutils import Vector

random.seed(7); np.random.seed(7)

# ------------------------------------------------------------------ settings
FPS, FRAMES, RES, SAMPLES = 30, 720, (1920, 1080), 96
HAZE = True
OUT = os.path.join(os.path.expanduser("~"), "portofino")
os.makedirs(OUT, exist_ok=True)

SUN_EL = math.radians(16)          # golden hour elevation
SUN_AZ = math.radians(38)          # degrees north of due west
S = Vector((-math.cos(SUN_EL) * math.cos(SUN_AZ),
            math.cos(SUN_EL) * math.sin(SUN_AZ),
            math.sin(SUN_EL)))     # direction TOWARD the sun
_hl = math.hypot(S.x, S.y); UX, UY = S.x / _hl, S.y / _hl

for o in list(bpy.data.objects):
    bpy.data.objects.remove(o, do_unlink=True)
scene = bpy.context.scene
COL = scene.collection

# ------------------------------------------------------------------ landform
# +X = east (harbour mouth), +Y = north. Harbour = capsule along X, radius 75 m.
def coast_d(x, y):
    """signed distance to the coast: >0 inland, <0 in water"""
    x = np.asarray(x, float); y = np.asarray(y, float)
    px = np.clip(x, -45, 230)
    d1 = np.hypot(x - px, y) - 75                 # harbour
    d2 = -(0.55 * (x - 230) + 0.835 * y)          # Gulf of Tigullio (NE)
    d3 = (y + 235) + 12 * np.sin(x * 0.013)       # open sea south of promontory
    return np.minimum(np.minimum(d1, d2), d3)

def inland_t(x, y):
    d = coast_d(x, y)
    x = np.asarray(x, float); y = np.asarray(y, float)
    piazza = 34 * np.exp(-(y / 55) ** 2) * np.clip((-60 - x) / 40, 0, 1)
    return d, np.maximum(d - 26 - piazza, 0)

def height(x, y):
    d, t = inland_t(x, y)
    x = np.asarray(x, float); y = np.asarray(y, float)
    along = x * UX + y * UY; q = x * UY - y * UX   # valley toward the sun
    w = np.exp(-(q / 150) ** 2) * np.clip((along - 60) / 140, 0, 1)
    hill = 200 * (1 - np.exp(-t / 170)) * (1 - 0.72 * w)
    n = (np.sin(x * 0.021 + 1.3) * np.cos(y * 0.017)
         + 0.5 * np.sin(x * 0.05 + y * 0.043) + 0.25 * np.sin(x * 0.11 - y * 0.09))
    hill = np.maximum(hill + n * 14 * t / (t + 50), 0)
    sea = np.maximum(-1.2 + d * 0.22, -32)
    return np.where(d > 0, 1.5 + hill, sea)

def H(x, y):
    return float(height(x, y))

# ------------------------------------------------------------------ materials
def principled(nt):
    return next(n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED')

def set_in(node, names, val):
    for nm in names:
        if nm in node.inputs:
            node.inputs[nm].default_value = val; return

def drive(sock, expr):
    sock.driver_add("default_value").driver.expression = expr

def mat(name, col, rough=0.6, metal=0.0, var=0.0, scale=0.5, bump=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; b = principled(nt)
    b.inputs["Base Color"].default_value = (*col, 1)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    if var or bump:
        tc = nt.nodes.new("ShaderNodeTexCoord"); nz = nt.nodes.new("ShaderNodeTexNoise")
        nz.inputs["Scale"].default_value = scale; nz.inputs["Detail"].default_value = 6
        nt.links.new(tc.outputs["Object"], nz.inputs["Vector"])
        if var:
            ma = nt.nodes.new("ShaderNodeMath"); ma.operation = 'MULTIPLY_ADD'
            ma.inputs[1].default_value = 2 * var; ma.inputs[2].default_value = 1 - var
            nt.links.new(nz.outputs[0], ma.inputs[0])
            hs = nt.nodes.new("ShaderNodeHueSaturation")
            hs.inputs["Color"].default_value = (*col, 1)
            nt.links.new(ma.outputs[0], hs.inputs["Value"])
            nt.links.new(hs.outputs["Color"], b.inputs["Base Color"])
        if bump:
            bp = nt.nodes.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = bump
            nt.links.new(nz.outputs[0], bp.inputs["Height"])
            nt.links.new(bp.outputs["Normal"], b.inputs["Normal"])
    return m

def mix(nt, fac, a, b):
    n = nt.nodes.new("ShaderNodeMix"); n.data_type = 'RGBA'
    for sock, val in ((n.inputs[0], fac), (n.inputs[6], a), (n.inputs[7], b)):
        if isinstance(val, bpy.types.NodeSocket): nt.links.new(val, sock)
        elif isinstance(val, (int, float)): sock.default_value = val
        else: sock.default_value = (*val, 1)
    return n.outputs[2]

def terrain_material():
    m = bpy.data.materials.new("Terrain"); m.use_nodes = True
    nt = m.node_tree; L = nt.links; b = principled(nt)
    b.inputs["Roughness"].default_value = 0.85
    geo = nt.nodes.new("ShaderNodeNewGeometry")
    sp = nt.nodes.new("ShaderNodeSeparateXYZ"); L.new(geo.outputs["Position"], sp.inputs[0])
    sn = nt.nodes.new("ShaderNodeSeparateXYZ"); L.new(geo.outputs["Normal"], sn.inputs[0])
    def mr(sock, a, c, tomax=1.0):
        n = nt.nodes.new("ShaderNodeMapRange")
        n.inputs[1].default_value = a; n.inputs[2].default_value = c
        n.inputs[4].default_value = tomax
        L.new(sock, n.inputs[0]); return n.outputs[0]
    n1 = nt.nodes.new("ShaderNodeTexNoise"); n1.inputs["Scale"].default_value = 0.03
    n1.inputs["Detail"].default_value = 8; L.new(geo.outputs["Position"], n1.inputs["Vector"])
    n2 = nt.nodes.new("ShaderNodeTexNoise"); n2.inputs["Scale"].default_value = 0.5
    n2.inputs["Detail"].default_value = 8; L.new(geo.outputs["Position"], n2.inputs["Vector"])
    veg = mix(nt, n1.outputs[0], (0.025, 0.07, 0.02), (0.09, 0.13, 0.04))
    c2 = mix(nt, mr(sn.outputs[2], 0.5, 0.3), veg, (0.33, 0.29, 0.24))
    c3 = mix(nt, mr(sp.outputs[2], 2.2, 5.0), (0.48, 0.45, 0.40), c2)
    vor = nt.nodes.new("ShaderNodeTexVoronoi")           # fake animated caustics
    try:
        vor.voronoi_dimensions = '4D'; vor.feature = 'DISTANCE_TO_EDGE'
        drive(vor.inputs["W"], "frame/45")
    except Exception:
        pass
    vor.inputs["Scale"].default_value = 0.35
    L.new(geo.outputs["Position"], vor.inputs["Vector"])
    sand = mix(nt, mr(vor.outputs["Distance"], 0.12, 0.0, 0.6),
               (0.55, 0.52, 0.42), (1.0, 0.98, 0.85))
    c4 = mix(nt, mr(sp.outputs[2], -0.3, 0.8), sand, c3)
    L.new(c4, b.inputs["Base Color"])
    bp = nt.nodes.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.3
    L.new(n2.outputs[0], bp.inputs["Height"]); L.new(bp.outputs["Normal"], b.inputs["Normal"])
    return m

def water_material():
    m = bpy.data.materials.new("Water"); m.use_nodes = True
    nt = m.node_tree; L = nt.links; b = principled(nt)
    out = next(n for n in nt.nodes if n.type == 'OUTPUT_MATERIAL')
    b.inputs["Base Color"].default_value = (0.85, 0.97, 0.97, 1)
    b.inputs["Roughness"].default_value = 0.03
    b.inputs["IOR"].default_value = 1.33
    set_in(b, ("Transmission Weight", "Transmission"), 1.0)
    tc = nt.nodes.new("ShaderNodeTexCoord")
    heights = []
    for sc, amp, speed in ((0.09, 1.0, 90), (0.45, 0.45, 40), (1.6, 0.15, 25)):
        nz = nt.nodes.new("ShaderNodeTexNoise"); nz.noise_dimensions = '4D'
        nz.inputs["Scale"].default_value = sc; nz.inputs["Detail"].default_value = 3
        L.new(tc.outputs["Object"], nz.inputs["Vector"])
        drive(nz.inputs["W"], "frame/%d" % speed)
        mu = nt.nodes.new("ShaderNodeMath"); mu.operation = 'MULTIPLY'
        mu.inputs[1].default_value = amp; L.new(nz.outputs[0], mu.inputs[0])
        heights.append(mu.outputs[0])
    a1 = nt.nodes.new("ShaderNodeMath"); L.new(heights[0], a1.inputs[0]); L.new(heights[1], a1.inputs[1])
    a2 = nt.nodes.new("ShaderNodeMath"); L.new(a1.outputs[0], a2.inputs[0]); L.new(heights[2], a2.inputs[1])
    bp = nt.nodes.new("ShaderNodeBump")
    bp.inputs["Strength"].default_value = 0.35; bp.inputs["Distance"].default_value = 0.4
    L.new(a2.outputs[0], bp.inputs["Height"]); L.new(bp.outputs["Normal"], b.inputs["Normal"])
    # let sunlight reach the seabed (shadow rays pass through the surface)
    lp = nt.nodes.new("ShaderNodeLightPath"); tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    tr.inputs["Color"].default_value = (0.75, 0.93, 0.9, 1)
    ms = nt.nodes.new("ShaderNodeMixShader")
    L.new(lp.outputs["Is Shadow Ray"], ms.inputs[0])
    L.new(b.outputs[0], ms.inputs[1]); L.new(tr.outputs[0], ms.inputs[2])
    L.new(ms.outputs[0], out.inputs["Surface"])
    # depth colour: turquoise over shallow sand -> deep blue
    va = nt.nodes.new("ShaderNodeVolumeAbsorption")
    va.inputs["Color"].default_value = (0.2, 0.72, 0.8, 1)
    va.inputs["Density"].default_value = 0.1
    L.new(va.outputs[0], out.inputs["Volume"])
    return m

M = dict(
    roof=mat("Roof", (0.55, 0.25, 0.15), 0.8, var=0.25, scale=1.5, bump=0.4),
    trim=mat("Trim", (0.88, 0.85, 0.78), 0.6),
    glass=mat("Glass", (0.02, 0.03, 0.04), 0.08),
    shutter=mat("Shutter", (0.05, 0.22, 0.10), 0.5),
    dark=mat("Dark", (0.03, 0.025, 0.02), 0.7),
    stone=mat("Stone", (0.42, 0.38, 0.32), 0.9, var=0.3, scale=0.8, bump=0.8),
    quay=mat("Quay", (0.50, 0.47, 0.42), 0.85, var=0.15, scale=1.0, bump=0.4),
    terracotta=mat("Terracotta", (0.6, 0.3, 0.18), 0.8),
    trunk=mat("Trunk", (0.12, 0.08, 0.05), 0.9),
    pine=mat("Pine", (0.03, 0.10, 0.03), 0.8, var=0.35, scale=0.6, bump=1.0),
    cypress=mat("Cypress", (0.02, 0.07, 0.03), 0.8, var=0.3, scale=0.8, bump=1.0),
    olive=mat("Olive", (0.16, 0.20, 0.12), 0.8, var=0.3, scale=0.6, bump=1.0),
    white=mat("HullWhite", (0.9, 0.9, 0.9), 0.15),
    navy=mat("HullNavy", (0.02, 0.04, 0.12), 0.15),
    teak=mat("Teak", (0.45, 0.28, 0.14), 0.6),
    metal=mat("Metal", (0.8, 0.8, 0.8), 0.25, metal=1.0),
    church=mat("Church", (0.92, 0.75, 0.35), 0.7, var=0.1, scale=0.3),
    abyss=mat("Abyss", (0.005, 0.02, 0.05), 1.0),
)
WALLS = [mat("Wall%d" % i, c, 0.75, var=0.12, scale=0.25, bump=0.15) for i, c in enumerate([
    (0.80, 0.55, 0.18), (0.85, 0.42, 0.33), (0.55, 0.62, 0.42), (0.60, 0.20, 0.14),
    (0.90, 0.82, 0.62), (0.88, 0.50, 0.22), (0.88, 0.62, 0.55), (0.90, 0.72, 0.30)])]
FLOWERS = [mat("Flower%d" % i, c, 0.6) for i, c in enumerate(
    [(0.8, 0.05, 0.08), (0.9, 0.3, 0.5), (0.7, 0.1, 0.6)])]
FABRIC = [mat("Fabric%d" % i, c, 0.8) for i, c in enumerate(
    [(0.9, 0.86, 0.75), (0.75, 0.2, 0.12), (0.15, 0.35, 0.2), (0.95, 0.95, 0.95), (0.85, 0.6, 0.2)])]
BOATCOL = [M['white'], M['white'], mat("BoatBlue", (0.05, 0.2, 0.5), 0.3),
           mat("BoatRed", (0.6, 0.06, 0.05), 0.3), M['teak'], mat("BoatGreen", (0.05, 0.3, 0.2), 0.3)]

# ------------------------------------------------------------------ mesh builder
def frame(p, ang, z=0.0):
    c, s = math.cos(ang), math.sin(ang)
    return lambda x, y, zz: (p[0] + x * c - y * s, p[1] + x * s + y * c, z + zz)

class MB:
    def __init__(s): s.v = []; s.f = []; s.mi = []; s.mats = []
    def add(s, verts, faces, m):
        if m not in s.mats: s.mats.append(m)
        k = s.mats.index(m); o = len(s.v); s.v += verts
        for f in faces: s.f.append(tuple(i + o for i in f)); s.mi.append(k)
    def box(s, fr, x0, x1, y0, y1, z0, z1, m):
        vs = [fr(x, y, z) for z in (z0, z1) for y in (y0, y1) for x in (x0, x1)]
        s.add(vs, [(0, 2, 3, 1), (4, 5, 7, 6), (0, 1, 5, 4), (2, 6, 7, 3), (0, 4, 6, 2), (1, 3, 7, 5)], m)
    def cyl(s, fr, cx, cy, z0, z1, r0, r1, m, seg=12):
        vs = []
        for z, r in ((z0, r0), (z1, r1)):
            for j in range(seg):
                a = 2 * math.pi * j / seg
                vs.append(fr(cx + r * math.cos(a), cy + r * math.sin(a), z))
        fs = [(j, (j + 1) % seg, seg + (j + 1) % seg, seg + j) for j in range(seg)]
        fs += [tuple(range(seg)), tuple(range(seg, 2 * seg))]
        s.add(vs, fs, m)
    def blob(s, fr, cx, cy, cz, rx, ry, rz, m, seg=10, rings=6, jit=0.0):
        vs = [fr(cx, cy, cz - rz)]
        for i in range(1, rings):
            ph = math.pi * i / rings
            for j in range(seg):
                th = 2 * math.pi * j / seg; k = 1 + random.uniform(-jit, jit)
                vs.append(fr(cx + rx * k * math.sin(ph) * math.cos(th),
                             cy + ry * k * math.sin(ph) * math.sin(th), cz - rz * math.cos(ph)))
        vs.append(fr(cx, cy, cz + rz)); top = len(vs) - 1; fs = []
        for j in range(seg):
            a = 1 + j; b = 1 + (j + 1) % seg
            fs.append((0, b, a))
            for i in range(rings - 2):
                fs.append((a + i * seg, b + i * seg, b + (i + 1) * seg, a + (i + 1) * seg))
            fs.append((a + (rings - 2) * seg, b + (rings - 2) * seg, top))
        s.add(vs, fs, m)
    def build(s, name, smooth=False):
        me = bpy.data.meshes.new(name); me.from_pydata(s.v, [], s.f)
        for m in s.mats: me.materials.append(m)
        me.polygons.foreach_set("material_index", s.mi)
        bm = bmesh.new(); bm.from_mesh(me)
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:]); bm.to_mesh(me); bm.free()
        if smooth: me.polygons.foreach_set("use_smooth", [True] * len(me.polygons))
        me.update()
        ob = bpy.data.objects.new(name, me); COL.objects.link(ob); return ob

ID = frame((0, 0), 0, 0)

# ------------------------------------------------------------------ terrain + sea
xs = np.arange(-1200, 901, 5.0); ys = np.arange(-700, 1101, 5.0)
X, Y = np.meshgrid(xs, ys); Z = height(X, Y)
nx, ny = len(xs), len(ys)
idx = np.arange(nx * ny).reshape(ny, nx)
faces = np.column_stack((idx[:-1, :-1].ravel(), idx[:-1, 1:].ravel(),
                         idx[1:, 1:].ravel(), idx[1:, :-1].ravel()))
me = bpy.data.meshes.new("Terrain")
me.from_pydata(np.column_stack((X.ravel(), Y.ravel(), Z.ravel())).tolist(), [], faces.tolist())
me.polygons.foreach_set("use_smooth", [True] * len(me.polygons))
me.materials.append(terrain_material()); me.update()
COL.objects.link(bpy.data.objects.new("Terrain", me))

mb = MB(); mb.box(ID, -30000, 30000, -30000, 30000, -60, 0, water_material()); mb.build("Sea")
mb = MB(); mb.box(ID, -30000, 30000, -30000, 30000, -52, -50, M['abyss']); mb.build("Abyss")

# ------------------------------------------------------------------ village
def shore(s, off, push=True):
    """walk the harbour edge (north quay -> Piazzetta arc -> south quay)"""
    R = 75 + off
    if s < 145: return (100 - s, R), (0, -1)
    s -= 145
    if s < math.pi * R:
        a = math.pi / 2 + s / R
        r = R + (26 if push and abs(a - math.pi) < 0.40 else 0)   # Piazzetta recess
        return (-45 + r * math.cos(a), r * math.sin(a)), (-math.cos(a), -math.sin(a))
    s -= math.pi * R
    return (-45 + s, -R), (0, 1)

def house(mb, p, n, w, dep, floors, base, wall, simple=False):
    fr = frame(p, math.atan2(n[1], n[0]) - math.pi / 2, base)
    fh, g = 3.3, 3.8; h = g + floors * fh
    mb.box(fr, -w / 2, w / 2, -dep, 0, -5, h, wall)
    e = 0.35; zr = h + 0.25
    mb.box(fr, -w / 2 - e, w / 2 + e, -dep - e, e, h, zr, M['roof'])
    vs = [fr(-w / 2 - e, -dep - e, zr), fr(w / 2 + e, -dep - e, zr), fr(w / 2 + e, e, zr),
          fr(-w / 2 - e, e, zr), fr(-w / 2, -dep / 2, zr + 1.6), fr(w / 2, -dep / 2, zr + 1.6)]
    mb.add(vs, [(0, 1, 2, 3), (3, 2, 5, 4), (1, 0, 4, 5), (0, 3, 4), (2, 1, 5)], M['roof'])
    ncol = max(2, int(w / 2.4))
    for fl in range(floors):
        z = g + fl * fh + 0.9
        mb.box(fr, -w / 2, w / 2, 0, 0.06, z - 1.02, z - 0.86, M['trim'])
        for c in range(ncol):
            x = -w / 2 + (c + 0.5) * w / ncol
            mb.box(fr, x - 0.62, x + 0.62, 0, 0.04, z - 0.15, z + 1.85, M['trim'])
            mb.box(fr, x - 0.45, x + 0.45, 0, 0.07, z, z + 1.7, M['glass'])
            if random.random() < 0.75:
                mb.box(fr, x - 0.92, x - 0.47, 0, 0.10, z, z + 1.7, M['shutter'])
                mb.box(fr, x + 0.47, x + 0.92, 0, 0.10, z, z + 1.7, M['shutter'])
            else:
                mb.box(fr, x - 0.45, x + 0.45, 0, 0.11, z, z + 1.7, M['shutter'])
            if random.random() < 0.3:
                mb.box(fr, x - 0.5, x + 0.5, 0.05, 0.35, z - 0.3, z - 0.05, M['terracotta'])
                mb.box(fr, x - 0.48, x + 0.48, 0.07, 0.33, z - 0.05, z + 0.2, random.choice(FLOWERS))
    if not simple:
        for c in range(ncol):
            x = -w / 2 + (c + 0.5) * w / ncol
            mb.box(fr, x - 0.8, x + 0.8, 0, 0.06, 0, 2.8, M['dark'])
        if random.random() < 0.65:
            vs = [fr(-w / 2 + .3, 0.05, 3.3), fr(w / 2 - .3, 0.05, 3.3),
                  fr(w / 2 - .3, 2.4, 2.6), fr(-w / 2 + .3, 2.4, 2.6)]
            mb.add(vs, [(0, 1, 2, 3)], random.choice(FABRIC))

vil = MB()
for off, second in ((11, False), (30, True)):
    dep = 10 if second else 12
    total = 145 + math.pi * (75 + off) + 260; s = 2.0
    while s < total - 6:
        w = random.uniform(5.5, 9.5)
        p, n = shore(s + w / 2, off)
        s += w
        back = (p[0] - n[0] * dep, p[1] - n[1] * dep)
        if float(coast_d(*back)) < 14: continue
        if second and random.random() < 0.2: continue
        base = H(*p) - 0.5 if second else 1.5
        house(vil, p, n, w + 0.05, dep, random.randint(2, 4) if second else random.randint(4, 6),
              base, random.choice(WALLS), simple=second)

# quay wall
R0 = 74; s = 0.0
while s < 145 + math.pi * R0 + 290:
    p, n = shore(s, -1, push=False); s += 4.0
    if float(coast_d(p[0] - n[0] * 9, p[1] - n[1] * 9)) < 2: continue
    fr = frame(p, math.atan2(n[1], n[0]) - math.pi / 2, 0)
    vil.box(fr, -2.7, 2.7, -10, 0, -3, 1.62, M['quay'])

# Piazzetta cafe umbrellas
for ux in np.arange(-150, -130, 5.5):
    for uy in np.arange(-26, 27, 5.5):
        if random.random() < 0.2: continue
        fr = frame((ux + random.uniform(-1, 1), uy + random.uniform(-1, 1)), random.uniform(0, 6.28), 1.5)
        vil.cyl(fr, 0, 0, 0, 2.9, 0.04, 0.04, M['metal'], 6)
        vil.cyl(fr, 0, 0, 2.25, 3.0, 1.7, 0.05, random.choice(FABRIC[:2] + FABRIC[3:4]), 8)
        vil.cyl(fr, 0, 0, 0.70, 0.75, 0.5, 0.5, M['trim'], 8)

# scattered hillside villas
count = 0
while count < 45:
    x, y = random.uniform(-600, 450), random.uniform(-230, 500)
    d, t = inland_t(x, y)
    if not (35 < float(t) < 260) or math.hypot(x - 150, y + 155) < 40 or math.hypot(x + 5, y + 150) < 30:
        continue
    nn = Vector((-30 - x, -y)).normalized()
    house(vil, (x, y), (nn.x, nn.y), random.uniform(9, 14), 9, random.randint(2, 3),
          H(x, y) - 1.0, random.choice(WALLS[:2] + WALLS[4:]), simple=True)
    count += 1

# Church of San Giorgio (on the saddle of the promontory)
cp = (-5, -150); cn = Vector((-0.5, 0.87)).normalized()
fr = frame(cp, math.atan2(cn.y, cn.x) - math.pi / 2, H(*cp) - 1.5)
vil.box(fr, -6.5, 6.5, -22, 0, -6, 11, M['church'])
vs = [fr(-6.9, -22.4, 11), fr(6.9, -22.4, 11), fr(6.9, 0.4, 11), fr(-6.9, 0.4, 11),
      fr(0, -22.4, 14.5), fr(0, 0.4, 14.5)]
vil.add(vs, [(0, 1, 2, 3), (0, 4, 5, 3), (1, 2, 5, 4), (0, 1, 4), (3, 5, 2)], M['roof'])
vil.box(fr, -1.3, 1.3, 0, 0.1, 0, 4.2, M['dark'])
vil.cyl(fr, 0, 0.0, 7.2, 7.2, 1.2, 1.2, M['glass'], 12)
for px in (-6.2, -3, 3, 6.2):
    vil.box(fr, px - 0.3, px + 0.3, 0, 0.15, 0, 11, M['trim'])
vil.box(fr, 6.5, 11, -22, -17.5, -6, 21, M['church'])
vil.box(fr, 7.3, 10.2, -17.5, -17.4, 16, 19.5, M['dark'])
vil.cyl(fr, 8.75, -19.75, 21, 25, 3.3, 0.1, M['roof'], 8)
vil.build("Village")

# Castello Brown + twin pines
cas = MB(); kp = (150, -155); kb = H(*kp) - 2
fr = frame(kp, 0, kb)
cas.box(fr, -20, 20, -14, 14, -10, 3, M['stone'])              # terrace / ramparts
cas.box(fr, -11, 9, -9, 7, 3, 14, M['stone'])                  # main keep
cas.box(fr, -12, -6, -10, -4, 3, 19, M['stone'])               # square tower
cas.cyl(fr, 12, 8, -8, 18, 4, 4, M['stone'], 20)               # round tower
cas.cyl(fr, 12, 8, 18, 19.2, 4.5, 4.5, M['stone'], 20)
for i in range(-11, 9, 2):                                     # crenellations
    for yy in (-9, 6):
        cas.box(fr, i, i + 1, yy, yy + 1, 14, 15, M['stone'])
for j in range(-9, 7, 2):
    for xx in (-11, 8):
        cas.box(fr, xx, xx + 1, j, j + 1, 14, 15, M['stone'])
for i in range(-20, 20, 2):
    for yy in (-14, 13.4):
        cas.box(fr, i, i + 1, yy, yy + 0.6, 3, 4, M['stone'])
for wx in (-7, -2, 3):
    for wz in (6, 10):
        cas.box(fr, wx, wx + 1, 7, 7.08, wz, wz + 1.8, M['dark'])
for px, py, ph in ((-16, 9, 14), (-11.5, 11, 15.5)):           # the twin pines
    cas.cyl(fr, px, py, 3, 3 + ph, 0.35, 0.22, M['trunk'], 8)
    cas.blob(fr, px, py, 3 + ph + 1.2, 4.6, 4.6, 2.2, M['pine'], 12, 6, 0.18)
cas.build("CastelloBrown")

# ------------------------------------------------------------------ boats
def hull(mb, fr, L, B, Hh, m):
    st = [(0, .8), (.3, 1), (.6, .95), (.85, .6), (1, .03)]
    vs = []; dv = []
    for t, wf in st:
        x = -L / 2 + t * L; w = B / 2 * wf; z = Hh * (1 + .35 * t * t)
        vs += [fr(x, -w, z), fr(x, -w * .8, -.1 * Hh), fr(x, 0, -.5 * Hh), fr(x, w * .8, -.1 * Hh), fr(x, w, z)]
        dv += [fr(x, -w * .97, z - .06), fr(x, w * .97, z - .06)]
    fs = [(0, 1, 2, 3, 4)]
    for i in range(len(st) - 1):
        a = i * 5; b = a + 5
        fs += [(a + j, a + j + 1, b + j + 1, b + j) for j in range(4)]
    mb.add(vs, fs, m)
    mb.add(dv, [(2 * i, 2 * i + 1, 2 * i + 3, 2 * i + 2) for i in range(len(st) - 1)], M['teak'])

def yacht(mb, p, ang, L, dark=False):
    fr = frame(p, ang, 0); B = L * .21; Hh = L * .085
    hull(mb, fr, L, B, Hh, M['navy'] if dark else M['white'])
    mb.box(fr, -.32 * L, .12 * L, -.36 * B, .36 * B, Hh, Hh + .075 * L, M['white'])
    mb.box(fr, -.30 * L, .125 * L, -.365 * B, .365 * B, Hh + .03 * L, Hh + .055 * L, M['glass'])
    mb.box(fr, -.25 * L, .0, -.28 * B, .28 * B, Hh + .075 * L, Hh + .135 * L, M['white'])
    mb.box(fr, -.24 * L, .005 * L, -.285 * B, .285 * B, Hh + .095 * L, Hh + .12 * L, M['glass'])
    mb.cyl(fr, -.12 * L, 0, Hh + .135 * L, Hh + .21 * L, .1, .05, M['white'], 6)

def sailboat(mb, p, ang, L):
    fr = frame(p, ang, 0); B = L * .28; Hh = L * .09
    hull(mb, fr, L, B, Hh, random.choice((M['white'], M['navy'])))
    mb.box(fr, -.2 * L, .15 * L, -.25 * B, .25 * B, Hh, Hh + .5, M['white'])
    mb.cyl(fr, .1 * L, 0, Hh, Hh + 1.25 * L, .09, .06, M['metal'], 6)
    mb.box(fr, -.3 * L, .1 * L, -.06, .06, Hh + 1.4, Hh + 1.55, M['metal'])

def dinghy(mb, p, ang):
    L = random.uniform(4.5, 7); fr = frame(p, ang, 0)
    hull(mb, fr, L, L * .36, L * .1, random.choice(BOATCOL))
    mb.box(fr, -.1 * L, 0, -.14 * L, .14 * L, L * .06, L * .1 + .05, M['teak'])

bo = MB()
x = -5.0
while x < 205:                                   # superyachts stern-to on the south quay
    L = random.uniform(18, 32)
    yacht(bo, (x, -72 + L / 2), math.pi / 2 + random.uniform(-.04, .04), L, random.random() < 0.25)
    x += L * .21 + random.uniform(4, 7)
for x in np.arange(-40, 95, 4.2):                # small boats on the north quay
    if random.random() < 0.85:
        dinghy(bo, (x, 69 - random.uniform(0, 1)), -math.pi / 2 + random.uniform(-.1, .1))
for x in np.arange(-108, 10, 7.5):               # moorings in the inner harbour
    for y in np.arange(-44, 50, 8):
        if float(coast_d(x, y)) < -9 and random.random() < 0.6:
            dinghy(bo, (x + random.uniform(-1.5, 1.5), y + random.uniform(-1.5, 1.5)),
                   random.uniform(-.3, .3))
yacht(bo, (250, -8), 2.7, 36); yacht(bo, (372, 5), 0.5, 30, True); yacht(bo, (430, 215), 1.1, 42)
sailboat(bo, (170, -22), 0.3, 12); sailboat(bo, (310, 22), 2.9, 14); sailboat(bo, (400, 160), 0.8, 13)
bo.build("Boats")

# ------------------------------------------------------------------ vegetation
t1 = MB(); t1.cyl(ID, 0, 0, -1, 7, .3, .2, M['trunk'], 6)
t1.blob(ID, 0, 0, 8.3, 4.6, 4.6, 2.3, M['pine'], 10, 6, 0.2); pine = t1.build("PineProto", True)
t2 = MB(); t2.cyl(ID, 0, 0, -1, 1, .2, .2, M['trunk'], 6)
t2.blob(ID, 0, 0, 7, 1.2, 1.2, 6.5, M['cypress'], 8, 6, 0.1); cyp = t2.build("CypressProto", True)
t3 = MB(); t3.blob(ID, 0, 0, 2.4, 3.3, 3.3, 2.8, M['olive'], 9, 5, 0.25); oli = t3.build("OliveProto", True)

N = 220000
tx = np.random.uniform(-1200, 900, N); ty = np.random.uniform(-700, 1100, N)
_, tt = inland_t(tx, ty)
ok = (tt > 20) & (np.hypot(tx - 150, ty + 155) > 27) & (np.hypot(tx + 5, ty + 150) > 19)
tx, ty = tx[ok], ty[ok]
pts = np.column_stack((tx, ty, height(tx, ty) - 0.3))
kind = np.random.rand(len(pts))

def scatter(name, proto, P, smin, smax):
    n = len(P); th = np.random.uniform(0, 2 * np.pi, n); sc = np.random.uniform(smin, smax, n) / 2
    c, s = np.cos(th), np.sin(th); V = []
    for dx, dy in ((1, 1), (-1, 1), (-1, -1), (1, -1)):
        V.append(np.column_stack((P[:, 0] + sc * (dx * c - dy * s), P[:, 1] + sc * (dx * s + dy * c), P[:, 2])))
    me = bpy.data.meshes.new(name)
    me.from_pydata(np.stack(V, axis=1).reshape(-1, 3).tolist(), [], np.arange(4 * n).reshape(n, 4).tolist())
    ob = bpy.data.objects.new(name, me); COL.objects.link(ob)
    ob.instance_type = 'FACES'; ob.use_instance_faces_scale = True
    ob.show_instancer_for_render = False; ob.show_instancer_for_viewport = False
    proto.parent = ob

scatter("Pines", pine, pts[kind < 0.5], 0.7, 1.4)
scatter("Cypresses", cyp, pts[(kind >= 0.5) & (kind < 0.62)], 0.7, 1.5)
scatter("Olives", oli, pts[kind >= 0.62], 0.6, 1.5)

# ------------------------------------------------------------------ light, sky, haze
sd = bpy.data.lights.new("Sun", 'SUN'); sd.energy = 5.0
sd.color = (1.0, 0.78, 0.55); sd.angle = math.radians(2.0)
sun = bpy.data.objects.new("Sun", sd); COL.objects.link(sun)
sun.rotation_euler = S.to_track_quat('Z', 'Y').to_euler()

world = bpy.data.worlds.new("Sky"); scene.world = world; world.use_nodes = True
wnt = world.node_tree
bg = next(n for n in wnt.nodes if n.type == 'BACKGROUND')
sky = wnt.nodes.new("ShaderNodeTexSky")
try: sky.sky_type = 'NISHITA'
except Exception: pass
for attr, val in (("sun_elevation", SUN_EL), ("sun_rotation", math.atan2(S.x, S.y)),
                  ("sun_disc", False), ("air_density", 1.2), ("dust_density", 2.5),
                  ("ozone_density", 1.5)):
    try: setattr(sky, attr, val)
    except Exception: pass
wnt.links.new(sky.outputs[0], bg.inputs["Color"])
bg.inputs["Strength"].default_value = 0.25

if HAZE:
    hm = bpy.data.materials.new("Haze"); hm.use_nodes = True
    hnt = hm.node_tree
    for n in list(hnt.nodes):
        if n.type != 'OUTPUT_MATERIAL': hnt.nodes.remove(n)
    hout = next(n for n in hnt.nodes if n.type == 'OUTPUT_MATERIAL')
    vs_ = hnt.nodes.new("ShaderNodeVolumeScatter")
    vs_.inputs["Color"].default_value = (1.0, 0.95, 0.9, 1)
    vs_.inputs["Density"].default_value = 0.00035
    vs_.inputs["Anisotropy"].default_value = 0.7
    hnt.links.new(vs_.outputs[0], hout.inputs["Volume"])
    hz = MB(); hz.box(ID, -30000, 30000, -30000, 30000, 0.05, 800, hm); hz.build("Haze")

# ------------------------------------------------------------------ camera
cd = bpy.data.cameras.new("Cam"); cd.lens = 26; cd.clip_start = 0.5; cd.clip_end = 1e5
cam = bpy.data.objects.new("Camera", cd); COL.objects.link(cam); scene.camera = cam
tgt = bpy.data.objects.new("CamTarget", None); COL.objects.link(tgt)
con = cam.constraints.new('TRACK_TO'); con.target = tgt
con.track_axis = 'TRACK_NEGATIVE_Z'; con.up_axis = 'UP_Y'
KEYS = [  # frame, camera position, look-at point
    (1,   (480, 112, 2.5),   (-60, 0, 16)),    # low over the open sea
    (230, (290, 62, 7),      (-80, -5, 14)),   # gliding into the harbour mouth
    (410, (70, 38, 17),      (-95, -12, 12)),  # rising in front of the Piazzetta
    (540, (40, -25, 46),     (-75, -5, 8)),    # arc over the yachts, climbing
    (650, (170, -150, 98),   (-45, 5, 4)),     # pulling back up over the castle ridge
    (720, (262, -212, 128),  (-30, 15, 0)),    # high panorama: castle, bay, gulf
]
for f, cpos, tpos in KEYS:
    cam.location = cpos; cam.keyframe_insert("location", frame=f)
    tgt.location = tpos; tgt.keyframe_insert("location", frame=f)

# ------------------------------------------------------------------ render setup
r = scene.render
scene.frame_start, scene.frame_end = 1, FRAMES
r.fps = FPS; r.resolution_x, r.resolution_y = RES; r.resolution_percentage = 100
r.engine = 'CYCLES'
cy = scene.cycles
cy.samples = SAMPLES; cy.use_denoising = True
cy.caustics_reflective = False; cy.caustics_refractive = False
cy.volume_bounces = 0
try: cy.device = 'GPU'
except Exception: pass
r.use_motion_blur = True; r.motion_blur_shutter = 0.35
for vt in ('AgX', 'Filmic'):
    try: scene.view_settings.view_transform = vt; break
    except Exception: pass
for look in ('AgX - Medium High Contrast', 'Medium High Contrast'):
    try: scene.view_settings.look = look; break
    except Exception: pass
r.image_settings.file_format = 'PNG'
r.filepath = os.path.join(OUT, "frames", "")
scene.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "portofino.blend"))
print("Saved", os.path.join(OUT, "portofino.blend"))
