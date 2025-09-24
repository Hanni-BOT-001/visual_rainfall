"""Render the ripple animation to PNG frames (headless).

This recreates the logic from Kyoto_rain_art/main.py and writes frames to
rainfall_chart/frames/frame_####.png which you can assemble into a video.
"""
import os
import math
import textwrap
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd


OUT_DIR = os.path.join(os.path.dirname(__file__), 'frames')
os.makedirs(OUT_DIR, exist_ok=True)


def load_data(csv_path=None):
    if csv_path and os.path.isfile(csv_path):
        try:
            df = pd.read_csv(csv_path, skiprows=11)
        except Exception:
            df = None
        if df is not None:
            def find(cols):
                for c in cols:
                    if c in df.columns:
                        return c
                return None
            rcol = find(['rain (mm)', 'rain_mm', 'rain'])
            wcol = find(['wind_direction_10m (°)', 'wind_direction_10m', 'wind_direction', 'wind_dir'])
            rhcol = find(['relative_humidity_2m (%)', 'relative_humidity_2m', 'humidity'])
            tcol = find(['temperature_2m (°C)', 'temperature_2m', 'temperature', 'temp'])
            if rcol and wcol:
                rainfall = df[rcol].fillna(0).astype(float).values
                wind_dir = df[wcol].fillna(0).astype(float).values
                humidity = df[rhcol].fillna(0).astype(float).values if rhcol else np.zeros(len(df))
                temperature = df[tcol].fillna(0).astype(float).values if tcol else np.zeros(len(df))
                return dict(frames=len(df), rainfall=rainfall, wind_dir=wind_dir, humidity=humidity, temperature=temperature)
    # fallback synthetic
    rng = np.random.default_rng(12345)
    frames = 300
    return dict(frames=frames,
                rainfall=np.abs(rng.normal(5, 10, frames)),
                wind_dir=rng.uniform(0, 360, frames),
                humidity=np.clip(rng.normal(70, 10, frames), 0, 100),
                temperature=rng.normal(15, 5, frames))


def render_frames(csv_path=None, max_frames=None):
    data = load_data(csv_path)
    frames = data['frames']
    rainfall = data['rainfall']
    wind_dir = data['wind_dir']
    humidity = data['humidity']
    temperature = data['temperature']

    if max_frames is None:
        max_frames = frames
    max_frames = min(max_frames, frames)

    # animation params
    N_RIPPLES = 24
    MAX_RADIUS = 100
    FADE_RATE = 0.03

    KYOTO_LAT = 35.0116
    KYOTO_LON = 135.7681

    fig, ax = plt.subplots(figsize=(8, 8))
    ax.set_xlim(0, 200)
    ax.set_ylim(0, 200)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_facecolor('black')

    # optional background map if available
    kyoto_img = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Kyoto_rain_art', 'Kyoto_map.jpg'))
    if os.path.exists(kyoto_img):
        img = plt.imread(kyoto_img)
        ax.imshow(img, extent=(0, 200, 0, 200), aspect='auto', zorder=0, alpha=0.75)

    rng = np.random.default_rng(1)
    for _ in range(30):
        cx = rng.uniform(20, 180)
        cy = rng.uniform(20, 180)
        cr = rng.uniform(10, 30)
        cloud = plt.Circle((cx, cy), cr, color='white', alpha=rng.uniform(0.10, 0.30), lw=0, fill=True, zorder=0.5)
        ax.add_patch(cloud)

    info_text = ax.text(1.0, 0.02, '', color='white', fontsize=12,
                        ha='right', va='bottom', transform=ax.transAxes,
                        bbox=dict(facecolor='black', boxstyle='round,pad=0.5', alpha=0.5), zorder=3)

    # create a grid of spawn positions across the 0..200 coordinate space
    GRID_ROWS = 6
    GRID_COLS = 8
    MARGIN = 12
    xs = np.linspace(MARGIN, 200 - MARGIN, GRID_COLS)
    ys = np.linspace(MARGIN, 200 - MARGIN, GRID_ROWS)
    grid_positions = [(x, y) for y in ys for x in xs]
    spawn_counter = {'c': 0}

    ripples = []
    ripple_artists = []

    def spawn_ripple(frame_idx):
        rain = float(rainfall[frame_idx % frames])
        wind_angle = np.deg2rad(float(wind_dir[frame_idx % frames]))

        pos = grid_positions[spawn_counter['c'] % len(grid_positions)]
        spawn_counter['c'] += 1

        # small jitter + wind nudge
        jitter = 6.0
        x = pos[0] + (rng.uniform() - 0.5) * jitter
        y = pos[1] + (rng.uniform() - 0.5) * jitter
        nudge = 6.0
        x += nudge * math.cos(wind_angle)
        y += nudge * math.sin(wind_angle)

        color_val = min(1.0, rain / 30.0)
        color = plt.cm.rainbow(color_val)
        new_ripple = {'x': x, 'y': y, 'radius': 0.0, 'alpha': 1.0, 'color': color, 'angle': wind_angle}
        artist = plt.Circle((x, y), 0.0, edgecolor=color, facecolor='none', alpha=1.0, lw=2, zorder=2)
        ripples.append(new_ripple)
        ripple_artists.append(artist)
        ax.add_patch(artist)

    for frame_idx in range(max_frames):
        # spawn
        if len(ripples) < N_RIPPLES:
            spawn_ripple(frame_idx)

        # update
        for i, r in list(enumerate(ripples)):
            r['radius'] += 2.0 + float(rainfall[frame_idx % frames]) * 0.08
            r['alpha'] -= FADE_RATE
            move_dist = r['radius'] * 0.02
            r['x'] += move_dist * math.cos(r['angle'])
            r['y'] += move_dist * math.sin(r['angle'])

            if i < len(ripple_artists):
                art = ripple_artists[i]
                art.center = (r['x'], r['y'])
                art.set_radius(r['radius'])
                art.set_alpha(max(0.0, min(1.0, r['alpha'])))
                color_val = min(1.0, float(rainfall[frame_idx % frames]) / 30.0)
                art.set_edgecolor(plt.cm.rainbow(color_val))

        remove_indices = [i for i, r in enumerate(ripples) if r['alpha'] <= 0.0 or r['radius'] > MAX_RADIUS]
        for idx in sorted(remove_indices, reverse=True):
            if idx < len(ripple_artists):
                ripple_artists[idx].remove()
            ripples.pop(idx)
            ripple_artists.pop(idx)

        info_text.set_text(textwrap.dedent(f"""
            Kyoto (35.0116, 135.7681)
            Rainfall: {rainfall[frame_idx % frames]:.1f} mm
            Humidity: {humidity[frame_idx % frames]:.1f}%
            Temp: {temperature[frame_idx % frames]:.1f}°C
        """))

        # render to file
        out_path = os.path.join(OUT_DIR, f'frame_{frame_idx:04d}.png')
        fig.savefig(out_path, dpi=150)
        print('Saved', out_path)

    plt.close(fig)


if __name__ == '__main__':
    render_frames(csv_path=None, max_frames=200)
