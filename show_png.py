#!/usr/bin/env python3
"""
show_eposters.py
Fully dynamic:
- Uses POSTER_TOKEN from bash
- Uses CACHE_REFRESH from bash (API refresh interval)
- Uses DISPLAY_TIME from bash (seconds per image)
- Uses HOME path dynamically
"""

import os
import time
from pathlib import Path
import requests
from PIL import Image
import pygame

API_BASE = "https://posterbridge.incandescentsolution.com/api/v1/eposter-list"
REQUEST_TIMEOUT = 10

# -------------------------------
# Read variables from environment
# -------------------------------
TOKEN = os.environ.get("POSTER_TOKEN")
CACHE_REFRESH = int(os.environ.get("CACHE_REFRESH", "60"))   # default 60 seconds
DISPLAY_SECONDS = int(os.environ.get("DISPLAY_TIME", "5"))  # default 5 seconds

HOME = Path(os.environ.get("HOME", "/home/pi"))
CACHE_DIR = HOME / "eposter_cache"


# -------------------------------
# Utility Functions
# -------------------------------
def ensure_cache():
    CACHE_DIR.mkdir(parents=True, exist_ok=True)


def get_posters_list(token):
    try:
        r = requests.get(API_BASE, params={"key": token}, timeout=REQUEST_TIMEOUT)
        if r.status_code != 200:
            return []
        data = r.json()
        posters = data.get("data", [])
        return posters
    except Exception:
        return []


def download_poster(url):
    ensure_cache()
    fname = url.split("/")[-1]
    dest = CACHE_DIR / fname
    if dest.exists():
        return dest

    try:
        r = requests.get(url, stream=True, timeout=REQUEST_TIMEOUT)
        r.raise_for_status()
        with open(dest, "wb") as f:
            for chunk in r.iter_content(8192):
                if chunk:
                    f.write(chunk)
        return dest
    except Exception:
        return None


def make_portrait_and_fit(img, target_w, target_h):
    iw, ih = img.size
    if iw > ih:
        img = img.rotate(90, expand=True)
        iw, ih = img.size

    scale = min(target_w / iw, target_h / ih)
    nw = int(iw * scale)
    nh = int(ih * scale)

    resized = img.resize((nw, nh), Image.LANCZOS)

    canvas = Image.new("RGBA", (target_w, target_h), (0, 0, 0, 255))
    x = (target_w - nw) // 2
    y = (target_h - nh) // 2
    canvas.paste(resized, (x, y))
    return canvas


def pil_to_surface(pil_img):
    return pygame.image.fromstring(
        pil_img.tobytes(), pil_img.size, pil_img.mode
    )


# -------------------------------
# Main Program
# -------------------------------
def main():
    if not TOKEN:
        print("ERROR: POSTER_TOKEN not set in environment!")
        return

    ensure_cache()

    # Initial fetch
    posters = get_posters_list(TOKEN)
    last_refresh = time.time()

    image_paths = []
    for p in posters:
        url = p.get("eposter_file")
        if not url:
            continue
        img_path = download_poster(url)
        if img_path:
            image_paths.append(img_path)

    pygame.init()
    pygame.display.init()

    info = pygame.display.Info()
    scr_w, scr_h = info.current_w, info.current_h

    screen = pygame.display.set_mode((scr_w, scr_h), pygame.FULLSCREEN)
    pygame.mouse.set_visible(False)
    clock = pygame.time.Clock()

    idx = 0
    running = True

    while running:
        # Refresh posters at interval
        if time.time() - last_refresh >= CACHE_REFRESH:
            posters = get_posters_list(TOKEN)
            image_paths.clear()
            for p in posters:
                url = p.get("eposter_file")
                if not url:
                    continue
                img_path = download_poster(url)
                if img_path:
                    image_paths.append(img_path)
            last_refresh = time.time()

        if not image_paths:
            continue

        path = image_paths[idx % len(image_paths)]

        try:
            pil = Image.open(path).convert("RGBA")
        except Exception:
            idx += 1
            continue

        canvas = make_portrait_and_fit(pil, scr_w, scr_h)
        surf = pil_to_surface(canvas)

        screen.blit(surf, (0, 0))
        pygame.display.flip()

        start = time.time()
        while time.time() - start < DISPLAY_SECONDS:
            for ev in pygame.event.get():
                if ev.type == pygame.KEYDOWN and ev.key in (pygame.K_ESCAPE, pygame.K_q):
                    running = False
                if ev.type == pygame.QUIT:
                    running = False
            clock.tick(30)

        idx += 1

    pygame.quit()


if __name__ == "__main__":
    main()

