import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Parameters
N_RIPPLES = 12
MAX_RADIUS = 100
FADE_RATE = 0.03

# Kyoto coordinates
KYOTO_LAT = 35.0116
KYOTO_LON = 135.7681

# Synthetic weather data
frames = 300
rainfall = np.abs(np.random.normal(5, 10, frames))
humidity = np.clip(np.random.normal(70, 10, frames), 0, 100)
temperature = np.random.normal(15, 5, frames)

fig, ax = plt.subplots(figsize=(8, 8))
ax.set_xlim(0, 200)
ax.set_ylim(0, 200)
ax.set_xticks([])
ax.set_yticks([])
ax.set_facecolor('midnightblue')

info_text = ax.text(1.0, 0.02,
    '', color='white', fontsize=12,
    ha='right', va='bottom', transform=ax.transAxes,
    bbox=dict(facecolor='black', boxstyle='round,pad=0.5', alpha=0.5))

ripples = []
ripple_artists = []

def spawn_ripple(frame):
    x = np.random.uniform(40, 160)
    y = np.random.uniform(40, 160)
    color_val = (frame % N_RIPPLES) / N_RIPPLES
    color = plt.cm.rainbow(color_val)
    new_ripple = {'x': x, 'y': y, 'radius': 0, 'alpha': 1.0, 'color': color, 'frame': frame}
    artist = plt.Circle((x, y), 0, color=color, alpha=1.0, lw=2, fill=False)
    ripples.append(new_ripple)
    ripple_artists.append(artist)
    ax.add_patch(artist)

def animate(frame):
    info_text.set_text(
        f"Kyoto ({KYOTO_LAT:.4f}, {KYOTO_LON:.4f})\n"
        f"Rainfall: {rainfall[frame]:.1f} mm\n"
        f"Humidity: {humidity[frame]:.1f}%\n"
        f"Temp: {temperature[frame]:.1f}°C"
    )

    if len(ripples) < N_RIPPLES:
        spawn_ripple(frame)

    for i, r in enumerate(ripples):
        color_val = min(1, r['radius'] / MAX_RADIUS)
        color = plt.cm.rainbow(color_val)
    r['radius'] += 2 + rainfall[frame] * 0.1
    r['alpha'] -= FADE_RATE
    ripple_artists[i].set_radius(r['radius'])
    ripple_artists[i].set_alpha(max(0, min(1, r['alpha'])))
    ripple_artists[i].set_edgecolor(color)
    r['color'] = color

    remove_indices = [i for i, r in enumerate(ripples) if r['alpha'] <= 0 or r['radius'] > MAX_RADIUS]
    for idx in sorted(remove_indices, reverse=True):
        ripple_artists[idx].remove()
        ripples.pop(idx)
        ripple_artists.pop(idx)

    return ripple_artists + [info_text]

ani = FuncAnimation(fig, animate, frames=frames, interval=50, blit=True)
plt.show()
