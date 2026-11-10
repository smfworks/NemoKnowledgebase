# render_runner.py — fixed-budget headless render of a model-written Blender scene script.
# Usage: blender -b -P render_runner.py -- <scene_script.py> <out_dir> [seconds] [width] [height]
# The scene script is EXPECTED to: build a scene, create a camera with animation, set render settings.
# This runner OVERRIDES only resolution/fps/samples/frame range (first N seconds) and output path,
# so both models get the identical render budget. Everything else the model wrote is preserved.
import bpy, sys, os, time

argv = sys.argv[sys.argv.index("--")+1:]
scene_script, out_dir = argv[0], argv[1]
SECONDS = int(argv[2]) if len(argv) > 2 else 12
W = int(argv[3]) if len(argv) > 3 else 1280
H = int(argv[4]) if len(argv) > 4 else 720
FPS = 24
os.makedirs(out_dir, exist_ok=True)
log = []

t0 = time.time()
# Execute the model's scene-builder. It runs with blender API available.
exec(open(scene_script).read(), {'__name__': '__main__', 'bpy': bpy})
log.append(f"scene script executed in {time.time()-t0:.1f}s")

scene = bpy.context.scene
# Fixed budget overrides (identical for both models)
scene.render.engine = 'CYCLES'
scene.cycles.device = 'CPU'
scene.cycles.samples = 64
scene.cycles.use_denoising = True
scene.render.resolution_x = W
scene.render.resolution_y = H
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'FFMPEG'
scene.render.ffmpeg.format = 'MPEG4'
scene.render.ffmpeg.codec = 'H264'
scene.render.fps = FPS
scene.frame_start = 1
scene.frame_end = SECONDS * FPS
scene.render.filepath = os.path.join(out_dir, 'render.mp4')
# Save the .blend as the deliverable the prompt asks for
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(out_dir, 'scene.blend'))
log.append(f"rendering frames 1..{scene.frame_end} at {W}x{H} {FPS}fps Cycles CPU 64 samples")

t1 = time.time()
bpy.ops.render.render(animation=True)
log.append(f"render wall: {time.time()-t1:.0f}s")
with open(os.path.join(out_dir, 'render_log.txt'), 'w') as f:
    f.write('\n'.join(log))
print("RENDER_RUNNER_DONE")
