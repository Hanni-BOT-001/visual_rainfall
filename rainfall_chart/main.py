import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from mpl_toolkits.basemap import Basemap

# Placeholder: Generate synthetic rainfall data for 100 years (1200 months)
# Each entry: (longitude, latitude, rainfall_mm)
np.random.seed(42)
months = 1200
num_points = 200
lons = np.random.uniform(-180, 180, num_points)
lats = np.random.uniform(-90, 90, num_points)
rainfall = np.random.uniform(0, 300, (months, num_points))

fig, ax = plt.subplots(figsize=(10, 6))
m = Basemap(projection='cyl', resolution='l', ax=ax)
m.drawcoastlines()
m.drawcountries()

scat = m.scatter(lons, lats, c=rainfall[0], cmap='Blues', s=50, edgecolor='k', zorder=5)
plt.title('Monthly Average Rainfall (Animated)')
cbar = plt.colorbar(scat, ax=ax, orientation='vertical', label='Rainfall (mm)')

# Animation function
def update(frame):
    scat.set_array(rainfall[frame])
    plt.title(f'Monthly Average Rainfall - Month {frame+1} ({1900 + frame//12})')
    return scat,

ani = animation.FuncAnimation(fig, update, frames=months, interval=100, blit=True)
plt.show()
