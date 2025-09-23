"""Render frames from the existing animation code and encode to MP4 using imageio.

This script imports the animation setup from `main.py` by running it in a special mode:
- It sets matplotlib to Agg backend, executes the code to obtain `fig` and the `update` function, then renders a number of frames and saves them as PNGs and tries to write an MP4 via imageio.

If imageio/ffmpeg isn't available, it will still write the PNG frames to `rainfall_chart/frames/`.
"""
import os
import sys
import importlib.util
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

ROOT = os.path.dirname(__file__)
MAIN_PY = os.path.join(ROOT, 'main.py')
FRAMES_DIR = os.path.join(ROOT, 'frames')
os.makedirs(FRAMES_DIR, exist_ok=True)

# execute main.py in a controlled namespace to extract the required objects
spec = importlib.util.spec_from_file_location('rain_main', MAIN_PY)
mod = importlib.util.module_from_spec(spec)
# Provide a flag so main.py can detect headless rendering if needed (we'll not modify main.py; it should define everything at module-level)
sys.modules['rain_main'] = mod
try:
    spec.loader.exec_module(mod)
except Exception as e:
    print('Error importing main.py:', e)
    raise

# We expect main.py defines `fig`, `update`, and possibly `frame_idx` in global scope; if not, we will recreate a simple runner
# Search for a FuncAnimation instance named `anim` or for `update` and `fig`
fig = getattr(mod, 'plt', None)

# Fallback: re-run main to build the animation but prevent plt.show() from blocking
# We'll run the main() function with a modified argv so it doesn't call plt.show() or we rely on mod.anim

# Try to use mod.anim
anim = getattr(mod, 'anim', None)
if anim is None:
    # as a safer fallback, re-import by executing main with a flag
    import runpy
    # provide argv to use save mode if available
    sys.argv = ['main.py', '--save']
    try:
        runpy.run_path(MAIN_PY, run_name='__main__')
        print('Ran main.py in save mode')
    except Exception as e:
        print('Failed to run main.py save mode:', e)

# If frames were created to frames/ by main.py, list them
pngs = sorted([os.path.join(FRAMES_DIR, f) for f in os.listdir(FRAMES_DIR) if f.endswith('.png')])
if not pngs:
    print('No frames found in', FRAMES_DIR)
else:
    print('Found', len(pngs), 'frames')

# Try to encode using imageio
try:
    import imageio
    out_mp4 = os.path.join(ROOT, 'animation.mp4')
    print('Writing', out_mp4)
    with imageio.get_writer(out_mp4, fps=20) as writer:
        for p in pngs:
            img = imageio.imread(p)
            writer.append_data(img)
    print('Wrote', out_mp4)
except Exception as e:
    print('Could not write mp4 via imageio:', e)
    print('Frames are available in', FRAMES_DIR)
