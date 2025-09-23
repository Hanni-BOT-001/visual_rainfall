"""Encode PNG frames in frames/ to an MP4 using imageio[ffmpeg]."""
import os
import imageio

FRAMES_DIR = os.path.join(os.path.dirname(__file__), 'frames')
OUT_MP4 = os.path.join(os.path.dirname(__file__), 'rainfall_animation.mp4')

pngs = sorted([os.path.join(FRAMES_DIR, f) for f in os.listdir(FRAMES_DIR) if f.endswith('.png')])
if not pngs:
    print('No PNG frames found in', FRAMES_DIR)
    raise SystemExit(1)

print('Writing', OUT_MP4, 'from', len(pngs), 'frames')
with imageio.get_writer(OUT_MP4, fps=20, codec='libx264') as writer:
    for p in pngs:
        img = imageio.imread(p)
        writer.append_data(img)

print('Wrote', OUT_MP4)
