import pygame
import sys
import math
import random
import pandas as pd
import numpy as np
from collections import deque

# --- CONFIG ---
WIDTH, HEIGHT = 1000, 700
BG_COLOR = (18, 20, 26)
FPS = 60
DATA_FILE_CANDIDATES = [
    '../kyotov9.24.csv',
    '../kyotov03.csv',
    'kyotov9.24.csv',
    'kyotov03.csv'
]

# Kyoto coordinates
KYOTO_LAT, KYOTO_LON = 35.0116, 135.7681

# Visual parameters
N_RIPPLES = 12
MAX_RADIUS = min(WIDTH, HEIGHT) // 2
FADE_RATE = 0.015
RIPPLE_LINEWIDTH = 2


def find_data_file(candidates):
    import os
    for p in candidates:
        if os.path.exists(p):
            return p
    return None


def load_weather_data(path):
    # If no path provided, return deterministic synthetic fallback immediately
    if path is None:
        rng = np.random.RandomState(1234)
        n = 1000
        return {
            'rain': rng.uniform(0, 20, n),
            'wind_dir': rng.uniform(0, 360, n),
            'rh': rng.uniform(30, 100, n),
            'temp': rng.uniform(0, 30, n)
        }

    # Attempts to find sensible columns; returns a dict of arrays or fallbacks
    try:
        df = pd.read_csv(path)
        # possible column names
        col_names = {c.lower(): c for c in df.columns}
        def find(cols):
            for c in cols:
                for k, orig in col_names.items():
                    if c in k:
                        return df[orig].values
            return None

        rain = find(['rain', 'precip', 'precipitation'])
        wind_dir = find(['wind_direction', 'winddir', 'wind_dir'])
        rh = find(['relative_humidity', 'humidity', 'rh'])
        temp = find(['temperature', 'temp', 'air_temperature'])

        # fallback to synthetic columns if missing
        n = len(df)
        if rain is None:
            rain = np.zeros(n)
        if wind_dir is None:
            wind_dir = np.zeros(n)
        if rh is None:
            rh = np.zeros(n)
        if temp is None:
            temp = np.zeros(n)

        return {'rain': rain, 'wind_dir': wind_dir, 'rh': rh, 'temp': temp}
    except Exception as e:
        print(f'Error loading data: {e}')
        # deterministic synthetic fallback
        rng = np.random.RandomState(1234)
        n = 1000
        return {
            'rain': rng.uniform(0, 20, n),
            'wind_dir': rng.uniform(0, 360, n),
            'rh': rng.uniform(30, 100, n),
            'temp': rng.uniform(0, 30, n)
        }


class Ripple:
    def __init__(self, x, y, color, wind_angle=0):
        self.x = x
        self.y = y
        self.r = 2.0
        self.color = color
        self.alpha = 0.95
        self.wind_angle = wind_angle

    def step(self):
        self.r += 1.6
        self.alpha -= FADE_RATE
        # small wind drift
        self.x += math.cos(self.wind_angle) * 0.4
        self.y += math.sin(self.wind_angle) * 0.4

    def is_dead(self):
        return self.alpha <= 0 or self.r > MAX_RADIUS


def color_from_rain(r):
    # map 0..30 mm to blue -> cyan -> yellow
    v = max(0.0, min(1.0, r / 30.0))
    # simple gradient
    if v < 0.5:
        t = v / 0.5
        rcol = int(40 + t * (40))
        gcol = int(80 + t * (150))
        bcol = int(200 + t * (55))
    else:
        t = (v - 0.5) / 0.5
        rcol = int(80 + t * (175))
        gcol = int(230 - t * (120))
        bcol = int(255 - t * (200))
    return (max(0, min(255, rcol)), max(0, min(255, gcol)), max(0, min(255, bcol)))


def make_clouds(surface, num=18):
    clouds = []
    for _ in range(num):
        cx = random.randint(0, WIDTH)
        cy = random.randint(0, HEIGHT)
        r = random.randint(120, 280)
        alpha = random.uniform(0.06, 0.18)
        clouds.append((cx, cy, r, alpha))
    return clouds


def draw_clouds(surface, clouds):
    for (cx, cy, r, alpha) in clouds:
        s = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
        g = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
        pygame.draw.circle(g, (30, 35, 50, int(alpha * 255)), (r, r), r)
        g = pygame.transform.smoothscale(g, (int(r * 2), int(r * 2)))
        s.blit(g, (0, 0))
        surface.blit(s, (cx - r, cy - r), special_flags=pygame.BLEND_RGBA_ADD)


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption('Kyoto Rain — Ripples')
    clock = pygame.time.Clock()

    data_path = find_data_file(DATA_FILE_CANDIDATES)
    if data_path:
        print('Loading data from', data_path)
        data = load_weather_data(data_path)
    else:
        print('No CSV found; using synthetic data')
        data = load_weather_data(None)

    n = len(data['rain'])
    idx = 0

    ripples = []
    clouds = make_clouds(screen, num=20)

    font = pygame.font.SysFont('Arial', 16)

    running = True
    frame = 0
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill(BG_COLOR)

        # draw clouds in background (subtle)
        draw_clouds(screen, clouds)

        # spawn a set of ripples every few frames
        if frame % 6 == 0:
            # spawn up to N_RIPPLES distributed around center with wind offset
            center_x = WIDTH // 2
            center_y = HEIGHT // 2
            for r_i in range(N_RIPPLES):
                # sample data
                rain_val = float(data['rain'][idx % n])
                wind_deg = float(data['wind_dir'][idx % n]) if n > 0 else 0.0
                wind_rad = math.radians(wind_deg)
                # spawn position slightly offset by wind
                off = 30 + r_i * 6
                sx = center_x + int(math.cos(wind_rad + r_i) * off)
                sy = center_y + int(math.sin(wind_rad + r_i) * off)
                color = color_from_rain(rain_val)
                ripples.append(Ripple(sx, sy, color, wind_angle=wind_rad))
                idx = (idx + 1) % n

        # step & draw ripples
        for rp in ripples[:]:
            rp.step()
            if rp.alpha > 0:
                col = rp.color + (int(max(0, min(255, rp.alpha * 255))),)
                surf = pygame.Surface((int(rp.r * 2) + 4, int(rp.r * 2) + 4), pygame.SRCALPHA)
                pygame.draw.circle(surf, col, (surf.get_width() // 2, surf.get_height() // 2), int(rp.r), RIPPLE_LINEWIDTH)
                screen.blit(surf, (rp.x - rp.r - 2, rp.y - rp.r - 2), special_flags=pygame.BLEND_RGBA_ADD)
            if rp.is_dead():
                try:
                    ripples.remove(rp)
                except ValueError:
                    pass

        # info overlay
        info_lines = [f'Kyoto: {KYOTO_LAT:.4f}, {KYOTO_LON:.4f}',
                      f'Frame: {frame}',
                      f'Rain sample: {float(data["rain"][idx % n]):.2f} mm',
                      f'RH: {float(data["rh"][idx % n]):.1f}%',
                      f'Temp: {float(data["temp"][idx % n]):.1f}°C']
        # draw semi-opaque box
        box_w = 240
        box_h = 22 * len(info_lines) + 12
        box_surf = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
        box_surf.fill((8, 10, 12, 180))
        # small blur-like border by drawing translucent rects (cheap)
        screen.blit(box_surf, (WIDTH - box_w - 18, HEIGHT - box_h - 18))
        for i, line in enumerate(info_lines):
            txt = font.render(line, True, (230, 230, 230))
            screen.blit(txt, (WIDTH - box_w - 12, HEIGHT - box_h - 6 + i * 22))

        pygame.display.flip()
        clock.tick(FPS)
        frame += 1

    pygame.quit()


if __name__ == '__main__':
    main()
