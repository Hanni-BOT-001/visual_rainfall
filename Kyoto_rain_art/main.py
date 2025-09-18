import os
import textwrap
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import pandas as pd


def main():
    """Run the ripple rainfall animation. Reads 'kyotov03.csv' if available."""
    # parameters
    N_RIPPLES = 12
    MAX_RADIUS = 100
    FADE_RATE = 0.03

    KYOTO_LAT = 35.0116
    KYOTO_LON = 135.7681

    # load data with fallback
    def synthetic(frames=300):
        rng = np.random.default_rng(12345)
        return dict(
            frames=frames,
            rainfall=np.abs(rng.normal(5, 10, frames)),
            wind_dir=rng.uniform(0, 360, frames),
            humidity=np.clip(rng.normal(70, 10, frames), 0, 100),
            temperature=rng.normal(15, 5, frames),
        )

    def load(csv_path='kyotov03.csv'):
        if os.path.isfile(csv_path):
            try:
                df = pd.read_csv(csv_path, skiprows=11)
            except Exception:
                return synthetic()
            # try to find expected cols
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
                return dict(frames=len(df), rainfall=rainfall, wind_dir=wind_dir,
                            humidity=humidity, temperature=temperature)
        return synthetic()

    data = load('kyotov03.csv')
    frames = data['frames']
    rainfall = data['rainfall']
    wind_dir = data['wind_dir']
    humidity = data['humidity']
    temperature = data['temperature']

    # figure
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.set_xlim(0, 200)
    ax.set_ylim(0, 200)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_facecolor('midnightblue')

    rng = np.random.default_rng(1)
    for _ in range(30):
        cx = rng.uniform(20, 180)
        cy = rng.uniform(20, 180)
        cr = rng.uniform(10, 30)
        cloud = plt.Circle((cx, cy), cr, color='white', alpha=rng.uniform(0.10, 0.30), lw=0, fill=True)
        ax.add_patch(cloud)

    info_text = ax.text(1.0, 0.02, '', color='white', fontsize=12,
                        ha='right', va='bottom', transform=ax.transAxes,
                        bbox=dict(facecolor='black', boxstyle='round,pad=0.5', alpha=0.5))

    ripples = []
    ripple_artists = []

    def spawn_ripple(frame_idx):
        rain = float(rainfall[frame_idx % frames])
        wind_angle = np.deg2rad(float(wind_dir[frame_idx % frames]))
        base_x, base_y = 100, 100
        offset = np.random.uniform(10, 60)
        x = base_x + offset * np.cos(wind_angle)
        y = base_y + offset * np.sin(wind_angle)
        color_val = min(1.0, rain / 30.0)
        color = plt.cm.rainbow(color_val)
        new_ripple = {'x': x, 'y': y, 'radius': 0.0, 'alpha': 1.0, 'color': color, 'angle': wind_angle}
        artist = plt.Circle((x, y), 0.0, edgecolor=color, facecolor='none', alpha=1.0, lw=2)
        ripples.append(new_ripple)
        ripple_artists.append(artist)
        ax.add_patch(artist)

    def animate(frame_idx):
        info_text.set_text(textwrap.dedent(f"""
            Kyoto ({KYOTO_LAT:.4f}, {KYOTO_LON:.4f})
            Rainfall: {rainfall[frame_idx % frames]:.1f} mm
            Humidity: {humidity[frame_idx % frames]:.1f}%
            Temp: {temperature[frame_idx % frames]:.1f}°C
        """))

        if len(ripples) < N_RIPPLES:
            spawn_ripple(frame_idx)

        for i, r in list(enumerate(ripples)):
            r['radius'] += 2.0 + float(rainfall[frame_idx % frames]) * 0.08
            r['alpha'] -= FADE_RATE
            move_dist = r['radius'] * 0.02
            r['x'] += move_dist * np.cos(r['angle'])
            r['y'] += move_dist * np.sin(r['angle'])

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

        return ripple_artists + [info_text]

    ani = FuncAnimation(fig, animate, frames=frames, interval=50, blit=True)
    plt.show()


if __name__ == '__main__':
    main()
