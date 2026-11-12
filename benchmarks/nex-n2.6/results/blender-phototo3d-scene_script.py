import bpy
import bmesh
import math
import os
import glob
import random
from mathutils import Vector

random.seed(7)

# ----------------------------------------------------------------------
# 0. Output directory (next to this script) + clean default scene
# ----------------------------------------------------------------------
try:
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
except NameError:
    SCRIPT_DIR = os.getcwd()
OUT_DIR = os.path.join(SCRIPT_DIR, "output")
RENDER_DIR = os.path.join(OUT_DIR, "render")
os.makedirs(RENDER_DIR, exist_ok=True)

scene = bpy.context.scene

for ob in list(bpy.data.objects):
    bpy.data.objects.remove(ob, do_unlink=True)

# ----------------------------------------------------------------------
# 1. Helpers
# ----------------------------------------------------------------------
def set_in(node, name, value):
    """Safely set a socket value (socket names differ slightly across 4.x)."""
    try:
        node.inputs[name].default_value = value
    except Exception:
        pass

def make_pbr(name):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    return m, m.node_tree.nodes.get("Principled BSDF")

def loft(name, rings, segments=96, close_bottom=True, close_top=True, mat=None):
    """Loft superellipse rings [(z, radius, exponent_n), ...] bottom->top.
    n=2 -> circle, n=6 -> square with rounded corners."""
    bm = bmesh.new()
    ring_vs = []
    for (z, r, n) in rings:
        e = 2.0 / n
        vs = []
        for i in range(segments):
            t = 2.0 * math.pi * i / segments
            c, s = math.cos(t), math.sin(t)
            x = r * math.copysign(abs(c) ** e, c)
            y = r * math.copysign(abs(s) ** e, s)
            vs.append(bm.verts.new((x, y, z)))
        ring_vs.append(vs)
    for j in range(len(ring_vs) - 1):
        a, b = ring_vs[j], ring_vs[j + 1]
        for i in range(segments):
            i2 = (i + 1) % segments
            bm.faces.new((a[i], a[i2], b[i2], b[i]))
    if close_bottom:
        bm.faces.new(list(reversed(ring_vs[0])))
    if close_top:
        bm.faces.new(ring_vs[-1])
    bm.normal_update()
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    scene.collection.objects.link(ob)
    if mat is not None:
        me.materials.append(mat)
    return ob

def smooth_all(ob):
    for p in ob.data.polygons:
        p.use_smooth = True

def smooth_sides_only(ob):
    for p in ob.data.polygons:
        p.use_smooth = abs(p.normal.z) < 0.5

def add_bevel(ob, width, segments=3):
    bev = ob.modifiers.new("Bevel", 'BEVEL')
    bev.width = width
    bev.segments = segments
    bev.limit_method = 'ANGLE'
    bev.angle_limit = math.radians(30)

def add_area(name, loc, target, energy, size):
    ld = bpy.data.lights.new(name, 'AREA')
    ld.energy = energy
    ld.size = size
    lo = bpy.data.objects.new(name, ld)
    scene.collection.objects.link(lo)
    lo.location = loc
    d = Vector(target) - Vector(loc)
    lo.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    return lo

# ----------------------------------------------------------------------
# 2. Materials
# ----------------------------------------------------------------------
glass_m, glass_b = make_pbr("BottleGlass")
set_in(glass_b, 'Base Color', (0.94, 0.97, 0.96, 1.0))
set_in(glass_b, 'Roughness', 0.02)
set_in(glass_b, 'Transmission Weight', 1.0)
set_in(glass_b, 'IOR', 1.45)

liquid_m, liquid_b = make_pbr("AmberLiquid")
set_in(liquid_b, 'Base Color', (1.0, 0.55, 0.15, 1.0))
set_in(liquid_b, 'Roughness', 0.03)
set_in(liquid_b, 'Transmission Weight', 1.0)
set_in(liquid_b, 'IOR', 1.33)

gold_m, gold_b = make_pbr("BrushedGold")
set_in(gold_b, 'Base Color', (1.0, 0.72, 0.32, 1.0))
set_in(gold_b, 'Metallic', 1.0)
set_in(gold_b, 'Roughness', 0.32)

tube_m, tube_b = make_pbr("DipTube")
set_in(tube_b, 'Base Color', (0.90, 0.93, 0.95, 1.0))
set_in(tube_b, 'Roughness', 0.08)
set_in(tube_b, 'Transmission Weight', 1.0)
set_in(tube_b, 'IOR', 1.46)

wall_m, wall_b = make_pbr("Backdrop")
set_in(wall_b, 'Base Color', (0.83, 0.83, 0.85, 1.0))
set_in(wall_b, 'Roughness', 0.95)

marble_m, marble_b = make_pbr("BlackMarble")
nt = marble_m.node_tree
tc = nt.nodes.new("ShaderNodeTexCoord")
mp = nt.nodes.new("ShaderNodeMapping")
no = nt.nodes.new("ShaderNodeTexNoise")
rp = nt.nodes.new("ShaderNodeValToRGB")
mp.inputs['Scale'].default_value = (0.35, 2.5, 1.0)
no.inputs['Scale'].default_value = 5.0
set_in(no, 'Detail', 8.0)
set_in(no, 'Roughness', 0.55)
rp.color_ramp.elements[0].position = 0.35
rp.color_ramp.elements[0].color = (0.012, 0.012, 0.014, 1.0)
rp.color_ramp.elements[1].position = 0.72
rp.color_ramp.elements[1].color = (0.060, 0.060, 0.066, 1.0)
nt.links.new(tc.outputs['Object'], mp.inputs['Vector'])
nt.links.new(mp.outputs['Vector'], no.inputs['Vector'])
nt.links.new(no.outputs['Fac'], rp.inputs['Fac'])
nt.links.new(rp.outputs['Color'], marble_b.inputs['Base Color'])
set_in(marble_b, 'Roughness', 0.16)
set_in(marble_b, 'Coat Weight', 0.6)
set_in(marble_b, 'Coat Roughness', 0.08)
set_in(marble_b, 'Specular IOR Level', 0.6)

# ----------------------------------------------------------------------
# 3. Studio set: dark marble floor + open-topped light cyclorama
# ----------------------------------------------------------------------
bpy.ops.mesh.primitive_plane_add(size=4.0, location=(0, 0, 0))
floor = bpy.context.active_object
floor.name = "Floor"
floor.data.materials.append(marble_m)

bpy.ops.mesh.primitive_cylinder_add(radius=1.7, depth=3.0, vertices=128,
                                    location=(0, 0, 1.2))
wall = bpy.context.active_object
wall.name = "Cyclorama"
wall.data.materials.append(wall_m)
# remove top/bottom caps so world light leaks in from above
import bmesh as _bm
_bm_ = _bm.new()
_bm_.from_mesh(wall.data)
_bmf = [f for f in _bm_.faces if abs(f.normal.z) > 0.9]
_bm.ops.delete(_bm_, geom=_bmf, context='FACES')
_bm_.to_mesh(wall.data)
_bm_.free()
wall.data.update()
smooth_all(wall)

# ----------------------------------------------------------------------
# 4. The bottle (dimensions in meters, base of bottle at z=0)
#    body width ~5.3 cm, glass+neck ~8.6 cm, gold cap ~3.6 cm
# ----------------------------------------------------------------------
body_r = 0.0265
rings = [
    (0.000, body_r, 6.0),   # bottom edge
    (0.006, body_r, 6.0),   # straight square body
    (0.058, body_r, 6.0),
]
for k in range(1, 7):       # smooth shoulder: square -> round neck
    u = k / 6.0
    s = u * u * (3 - 2 * u)
    rings.append((0.058 + (0.0745 - 0.058) * u,
                  body_r + (0.0085 - body_r) * s,
                  6.0 - 4.0 * s))
rings += [
    (0.0790, 0.0085, 2.0),  # neck
    (0.0850, 0.0085, 2.0),
    (0.0862, 0.0098, 2.0),  # small lip under the cap
]
glass = loft("BottleGlass", rings, mat=glass_m)
sol = glass.modifiers.new("Solidify", 'SOLIDIFY')   # real glass thickness
sol.thickness = 0.003
sol.offset = -1.0

# solid thick glass base slab (the bright clear band at the bottom)
loft("GlassBase", [(0.002, 0.0230, 6.0), (0.0118, 0.0230, 6.0)], mat=glass_m)

# amber liquid with a small air gap at the shoulders
loft("AmberLiquid", [(0.012, 0.0228, 6.0), (0.054, 0.0228, 6.0),
                     (0.058, 0.0212, 6.0)], mat=liquid_m)

# dip tube visible through the liquid
bpy.ops.mesh.primitive_cylinder_add(radius=0.0008, depth=0.058, vertices=24,
                                    location=(0, 0, 0.049))
tube = bpy.context.active_object
tube.name = "DipTube"
tube.data.materials.append(tube_m)
smooth_all(tube)

# two air bubbles at the liquid surface (+ a tiny one)
for i, (bx, by, bz, br) in enumerate([(0.005, 0.002, 0.0590, 0.0017),
                                      (-0.004, 0.003, 0.0600, 0.0012),
                                      (0.000, -0.005, 0.0586, 0.0009)]):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=br, segments=20, ring_count=12,
                                         location=(bx, by, bz))
    bub = bpy.context.active_object
    bub.name = "Bubble.%d" % (i + 1)
    bub.data.materials.append(glass_m)
    smooth_all(bub)

# brushed-gold two-tier cap
bpy.ops.mesh.primitive_cylinder_add(radius=0.0105, depth=0.027, vertices=96,
                                    location=(0, 0, 0.0895))
cap_lo = bpy.context.active_object
cap_lo.name = "CapBody"
cap_lo.data.materials.append(gold_m)
add_bevel(cap_lo, 0.0006, 2)
smooth_sides_only(cap_lo)

bpy.ops.mesh.primitive_cylinder_add(radius=0.0118, depth=0.0085, vertices=96,
                                    location=(0, 0, 0.10725))
cap_top = bpy.context.active_object
cap_top.name = "CapTop"
cap_top.data.materials.append(gold_m)
add_bevel(cap_top, 0.0012, 3)
smooth_sides_only(cap_top)

# ----------------------------------------------------------------------
# 5. Three-point studio lighting + soft world ambient
# ----------------------------------------------------------------------
add_area("KeyLight",  (0.55,  0.65, 0.62), (0, 0, 0.06), 300, 0.7)
add_area("FillLight", (-0.75, 0.35, 0.30), (0, 0, 0.06), 90, 0.9)
add_area("RimLight",  (-0.45, -0.70, 0.60), (0, 0, 0.06), 200, 0.5)

world = scene.world or bpy.data.worlds.new("World")
scene.world = world
world.use_nodes = True
bg = world.node_tree.nodes.get("Background")
bg.inputs[0].default_value = (0.72, 0.75, 0.80, 1.0)
bg.inputs[1].default_value = 0.7

# ----------------------------------------------------------------------
# 6. Camera rig: turntable orbit (360 deg) + gentle crane rise
# ----------------------------------------------------------------------
rig = bpy.data.objects.new("Turntable", None)
scene.collection.objects.link(rig)
rig.location = (0, 0, 0)

aim = bpy.data.objects.new("Aim", None)
scene.collection.objects.link(aim)
aim.location = (0, 0, 0.055)

cam_data = bpy.data.cameras.new("ShowcaseCamera")
cam_data.lens = 50.0
cam_data.clip_start = 0.02
cam_data.clip_end = 50.0
cam_data.dof.use_dof = True
cam_data.dof.focus_distance = 0.46
cam_data.dof.aperture_fstop = 5.6
cam_data.dof.aperture_blades = 8
cam = bpy.data.objects.new("Camera", cam_data)
scene.collection.objects.link(cam)
cam.parent = rig
cam.location = (0.44, 0, 0.105)
cam.rotation_euler = (math.radians(85), 0, math.radians(90))
con = cam.constraints.new('TRACK_TO')
con.target = aim
con.track_axis = 'TRACK_NEGATIVE_Z'
con.up_axis = 'UP_Y'
scene.camera = cam

# one full revolution, frames 1..240 (10 s @ 24 fps)
rig.rotation_euler = (0, 0, 0)
rig.keyframe_insert("rotation_euler", frame=1)
rig.rotation_euler = (0, 0, math.radians(360))
rig.keyframe_insert("rotation_euler", frame=240)

# gentle rise during the first ~4.5 s, then hold
cam.location = (0.44, 0, 0.105)
cam.keyframe_insert("location", frame=1)
cam.location = (0.44, 0, 0.160)
cam.keyframe_insert("location", frame=110)
cam.location = (0.44, 0, 0.160)
cam.keyframe_insert("location", frame=240)

# constant angular speed on the turntable
try:
    for fc in rig.animation_data.action.fcurves:
        for kp in fc.keyframe_points:
            kp.interpolation = 'LINEAR'
except Exception:
    pass

# ----------------------------------------------------------------------
# 7. Render settings: Cycles / CPU / 1280x720 / 24 fps / H.264 MP4
# ----------------------------------------------------------------------
scene.render.engine = 'CYCLES'
scene.cycles.device = 'CPU'
scene.cycles.feature_set = 'SUPPORTED'
scene.cycles.samples = 96
scene.cycles.use_adaptive_sampling = True
scene.cycles.adaptive_threshold = 0.03
try:
    scene.cycles.use_denoising = True
    scene.cycles.denoiser = 'OPENIMAGEDENOISE'
except Exception:
    pass
scene.cycles.caustics_reflective = False
scene.cycles.caustics_refractive = False
scene.render.use_persistent_data = True

scene.render.resolution_x = 1280
scene.render.resolution_y = 720
scene.render.resolution_percentage = 100
scene.render.pixel_aspect_x = 1.0
scene.render.pixel_aspect_y = 1.0
scene.render.fps = 24
scene.render.fps_base = 1.0
scene.frame_start = 1
scene.frame_end = 240
scene.frame_set(1)

try:
    scene.view_settings.view_transform = 'AgX'
    scene.view_settings.exposure = 0.4
except Exception:
    pass

scene.render.image_settings.file_format = 'FFMPEG'
scene.render.ffmpeg.format = 'MPEG4'
scene.render.ffmpeg.codec = 'H264'
scene.render.ffmpeg.constant_rate_factor = 'HIGH'
scene.render.ffmpeg.audio_codec = 'NONE'
scene.render.filepath = os.path.join(RENDER_DIR, "showcase")

# ----------------------------------------------------------------------
# 8. Save .blend, render the animation, report
# ----------------------------------------------------------------------
blend_path = os.path.join(OUT_DIR, "product.blend")
bpy.ops.wm.save_as_mainfile(filepath=blend_path)

bpy.ops.render.render(animation=True)

mp4 = os.path.join(RENDER_DIR, "showcase.mp4")
if not os.path.exists(mp4):
    cand = (glob.glob(os.path.join(RENDER_DIR, "showcase*.mp4"))
            or glob.glob(os.path.join(RENDER_DIR, "*.mp4")))
    mp4 = cand[0] if cand else "(movie not found)"

print("=" * 60)
print("PRODUCT : square glass cologne bottle, amber liquid, gold cap")
print("OBJECTS :", ", ".join(sorted(o.name for o in scene.objects)))
print("MATERIALS:", ", ".join(sorted(m.name for m in bpy.data.materials)))
print("CAMERA  : 360 deg turntable orbit, radius 0.44 m, constant speed,")
print("          frames 1-240 @ 24 fps, gentle rise z 0.105 -> 0.160 m")
print("          over the first 110 frames, tracking (0,0,0.055), 50 mm, f/5.6")
print("BLEND   :", blend_path)
print("MOVIE   :", mp4)
print("=" * 60)
