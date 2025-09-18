import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import matplotlib.colors as mcolors
import os

# Load weather data
csv_path = 'Kyotorain.csv'
if not os.path.isfile(csv_path):
    print(f"Error: Data file '{csv_path}' not found in the current directory.")
    print("Please make sure the file exists and try again.")
    exit(1)
try:
    # Find the line number where the main weather data starts
    with open(csv_path, encoding='utf-8') as f:
        lines = f.readlines()
    for i, line in enumerate(lines):
        if line.strip().startswith('time,temperature_2m'):
            data_start = i
            break
    df = pd.read_csv(csv_path, skiprows=data_start)
except Exception as e:
    print(f"Error loading CSV file: {e}")
    exit(1)


# Clean and parse data
# Use all columns from the weather data block
expected_cols = ['time','temperature_2m (°C)','dew_point_2m (°C)','relative_humidity_2m (%)','rain (mm)','wind_speed_10m (km/h)','wind_direction_10m (°)','surface_pressure (hPa)','cloud_cover_low (%)']
df = df[expected_cols].dropna()
df['time'] = pd.to_datetime(df['time'])



# Normalize for generative art
rain = df['rain (mm)'].astype(float).values
frames = len(df)

fig, ax = plt.subplots(figsize=(10, 10))
ax.set_facecolor('#1a1a2e')
ax.set_xticks([])
ax.set_yticks([])
ax.set_xlim(-1, 1)
ax.set_ylim(-1, 1)

# Prepare raindrop scatter
raindrops = ax.scatter([], [], s=[], c=[], alpha=0.7)
rain_cmap = plt.get_cmap('Blues')


def animate(frame):
    # Number of drops and their properties depend on rain intensity
    n_drops = int(10 + rain[frame]*8)
    # Raindrop positions: random x, falling y
    x = np.random.uniform(-0.95, 0.95, n_drops)
    y = np.linspace(1, -1, n_drops) + np.random.normal(0, 0.05, n_drops)
    sizes = 30 + rain[frame]*20 * np.random.uniform(0.7, 1.3, n_drops)
    colors = rain_cmap(np.clip(rain[frame]/10, 0, 1))
    alphas = np.clip(0.3 + rain[frame]/10, 0.3, 0.9)
    raindrops.set_offsets(np.c_[x, y])
    raindrops.set_sizes(sizes)
    raindrops.set_color(colors)
    raindrops.set_alpha(alphas)
    ax.set_title(f"Rainfall: {rain[frame]:.2f} mm", fontsize=18, color='#3a8dde')

    # Display Kyoto info and real-time weather in lower right
    kyoto_lon = float(135.7681)
    kyoto_lat = float(35.0116)
    print(f"DEBUG: kyoto_lon={kyoto_lon} type={type(kyoto_lon)}, kyoto_lat={kyoto_lat} type={type(kyoto_lat)}")
    dewpoint = df['dew_point_2m (°C)'].iloc[frame]
    humidity = df['relative_humidity_2m (%)'].iloc[frame]
    temp = df['temperature_2m (°C)'].iloc[frame]
    try:
        info_text = (f"Kyoto\nLon: {kyoto_lon:.4f}\nLat: {kyoto_lat:.4f}\n"
                     f"Temp: {temp:.1f}°C\nDewpoint: {dewpoint:.1f}°C\nRH: {humidity:.0f}%")
    except ValueError:
        info_text = (f"Kyoto\nLon: {str(kyoto_lon)}\nLat: {str(kyoto_lat)}\n"
                     f"Temp: {str(temp)}°C\nDewpoint: {str(dewpoint)}°C\nRH: {str(humidity)}%")
    # Remove previous text box if exists
    if hasattr(ax, 'weather_box'):
        ax.weather_box.remove()
    ax.weather_box = ax.text(0.98, 0.02, info_text, transform=ax.transAxes,
        fontsize=14, color='white', ha='right', va='bottom',
        bbox=dict(facecolor='#1a1a2e', edgecolor='#3a8dde', boxstyle='round,pad=0.5', alpha=0.7))

    return [raindrops, ax.weather_box]

ani = FuncAnimation(fig, animate, frames=frames, interval=120, blit=True)
plt.show()
