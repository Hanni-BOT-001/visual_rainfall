import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
import numpy as np

# reuse helpers from main.py in the same directory
import main as m

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'frames')


def save_frames(n_frames=200, fps=20, dpi=150):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    data = m.load_data(m.CSV_CANDIDATE)
    n = len(data['rain'])

    fig, ax = plt.subplots(figsize=(10, 7))
    # use same background logic as main
    try:
        kyoto_img_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Kyoto_rain_art', 'Kyoto_map.jpg'))
        if os.path.exists(kyoto_img_path):
            img = plt.imread(kyoto_img_path)
            ax.imshow(img, extent=(0,1,0,1), aspect='auto', interpolation='bilinear', zorder=0, alpha=0.75)
        else:
            ax.set_facecolor('#000000')
    except Exception:
        ax.set_facecolor('#000000')

    ax.set_xlim(0,1); ax.set_ylim(0,1)
    ax.set_xticks([]); ax.set_yticks([])

    # grid spawn positions (match main.py)
    MARGIN = 0.06
    span = 1.0 - 2 * MARGIN
    max_area_frac = 1.0 / 20.0
    max_r = float(np.sqrt(max_area_frac / np.pi))
    min_spacing = 2.0 * max_r
    max_cols = max(1, int(np.floor(span / min_spacing)) + 1)
    max_rows = max(1, int(np.floor(span / min_spacing)) + 1)
    GRID_COLS = min(8, max_cols)
    GRID_ROWS = min(6, max_rows)
    xs = np.linspace(MARGIN, 1 - MARGIN, GRID_COLS)
    ys = np.linspace(MARGIN, 1 - MARGIN, GRID_ROWS)
    grid_positions = [(x, y) for y in ys for x in xs]
    spawn_i = 0

    ripples = []
    artists = []

    def spawn(idx):
        nonlocal spawn_i
        rain = float(data['rain'][idx % n])
        wind = float(data['wind_dir'][idx % n])
        ang = np.deg2rad(wind)
        pos = grid_positions[spawn_i % len(grid_positions)]
        spawn_i += 1
        jitter = 0.03
        x = pos[0] + (np.random.rand() - 0.5) * jitter
        y = pos[1] + (np.random.rand() - 0.5) * jitter
        offx = 0.02 * np.cos(ang)
        offy = 0.02 * np.sin(ang)
        x += offx; y += offy
        x = float(np.clip(x, 0.02, 0.98))
        y = float(np.clip(y, 0.02, 0.98))
        col = m.color_from_rain(rain)
        r = m.Ripple(x, y, col, r0=0.02, max_r=max_r)
        from matplotlib.colors import to_rgba
        rgba = to_rgba(r.color, r.alpha)
        c = Circle((r.x, r.y), r.r, fill=False, edgecolor=rgba, linewidth=2.5, zorder=2)
        ax.add_patch(c)
        ripples.append(r); artists.append(c)

    frame_idx = 0
    for frame in range(n_frames):
        if frame % 5 == 0:
            for _ in range(6):
                spawn(frame_idx)
                frame_idx += 1

        # step and update artists
        to_remove = []
        for rp, art in zip(ripples[:], artists[:]):
            alive = rp.step()
            art.set_radius(rp.r)
            from matplotlib.colors import to_rgba
            art.set_edgecolor(to_rgba(rp.color, max(0.0, rp.alpha)))
            if not alive:
                to_remove.append((rp, art))

        for rp, art in to_remove:
            try:
                ripples.remove(rp); artists.remove(art); art.remove()
            except ValueError:
                pass

        out_path = os.path.join(OUTPUT_DIR, f'frame_{frame:04d}.png')
        fig.savefig(out_path, dpi=dpi)
    plt.close(fig)
    print(f'Wrote {n_frames} frames to {OUTPUT_DIR}')


if __name__ == '__main__':
    save_frames()
