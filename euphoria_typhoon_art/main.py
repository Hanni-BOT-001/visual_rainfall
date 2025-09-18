import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Euphoria-inspired color palette
PURPLE = '#8f5fd7'
BLUE = '#3a8dde'
DARK = '#1a1a2e'

fig, ax = plt.subplots(figsize=(10, 10))
fig.patch.set_facecolor(DARK)
ax.set_facecolor(DARK)
ax.set_xticks([])
ax.set_yticks([])
ax.set_xlim(-180, 180)
ax.set_ylim(-90, 90)

# Generate imaginary typhoon tracks
num_typhoons = 5
frames = 200
tracks = []
for i in range(num_typhoons):
    # Random start/end points, spiral path
    lon0, lat0 = np.random.uniform(-150, 150), np.random.uniform(-60, 60)
    angle = np.linspace(0, 2 * np.pi, frames)
    r = np.linspace(10, 40, frames) + np.random.uniform(-5, 5)
    lon = lon0 + r * np.cos(angle + i)
    lat = lat0 + r * np.sin(angle + i)
    tracks.append((lon, lat))

# Draw glowing background
for i in range(12):
    ax.scatter(np.random.uniform(-180, 180, 100), np.random.uniform(-90, 90, 100),
               color=PURPLE if i % 2 == 0 else BLUE, alpha=0.04, s=400)

lines = [ax.plot([], [], lw=4, alpha=0.8)[0] for _ in range(num_typhoons)]
points = [ax.scatter([], [], s=180, alpha=0.9) for _ in range(num_typhoons)]

def animate(frame):
    for i, (line, point) in enumerate(zip(lines, points)):
        lon, lat = tracks[i]
        color = PURPLE if i % 2 == 0 else BLUE
        line.set_data(lon[:frame], lat[:frame])
        line.set_color(color)
        line.set_alpha(0.7 + 0.3 * np.sin(frame * 0.05 + i))
        point.set_offsets(np.c_[lon[frame], lat[frame]])
        point.set_color(color)
    return lines + points

ani = FuncAnimation(fig, animate, frames=frames, interval=40, blit=True)
plt.show()
