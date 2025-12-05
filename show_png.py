#!/usr/bin/env python3
"""
show_folder_scroll.py

Slideshow for all images in a folder with a smooth vertical scrolling animation.

Usage:
    python3 show_folder_scroll.py images_folder [seconds_per_image]

Defaults to 5 seconds per image if not provided.
Press ESC or 'q' to quit.
"""
import sys
import time
from pathlib import Path
from PIL import Image
import pygame
import math

def scale_letterbox_allow_zoom(img, target_w, target_h, min_zoom=1.0):
    """
    Scale image to at least fit one dimension and letterbox.
    Returns a PIL RGBA image. If the image exactly fits, caller may request a slight zoom
    by setting min_zoom > 1.0 to create room for scrolling.
    """
    iw, ih = img.size
    # scale so image covers the width or height (we want to fill the screen along the smaller axis)
    scale = max(target_w / iw, target_h / ih)  # this ensures we cover the full screen (no empty bars)
    scale = max(scale, min_zoom)
    nw, nh = max(1, int(iw * scale)), max(1, int(ih * scale))
    resized = img.resize((nw, nh), Image.LANCZOS)

    # If the resized image is smaller than target in either dimension (shouldn't be), letterbox on black
    canvas = Image.new("RGBA", (max(target_w, nw), max(target_h, nh)), (0, 0, 0, 255))
    x = (canvas.width - nw) // 2
    y = (canvas.height - nh) // 2
    canvas.paste(resized, (x, y), resized)
    # center-crop to exact target size (important when we used max scale)
    left = (canvas.width - target_w) // 2
    top = (canvas.height - target_h) // 2
    cropped = canvas.crop((left, top, left + target_w, top + target_h))
    return cropped

def pil_to_surface(pil_img):
    mode = pil_img.mode
    size = pil_img.size
    data = pil_img.tobytes()
    return pygame.image.fromstring(data, size, mode)

def ease_in_out(t):
    """Smooth cosine easing from 0->1 for t in [0,1]."""
    return 0.5 - 0.5 * math.cos(math.pi * t)

def show_image_with_scroll(screen, pil_img, scr_w, scr_h, seconds=5, fps=30):
    """
    Display the given PIL image (RGBA) on the pygame screen with a vertical scroll animation.
    """
    # Prepare canvas: try to cover the screen (we use slight zoom to allow motion if needed)
    # If the image after cover-scaling is still exactly the screen, we apply a tiny zoom to create some scroll room.
    # The scale_letterbox_allow_zoom function returns a canvas sized exactly scr_w x scr_h.
    # To compute scrolling, we will generate a slightly taller "frame" by resizing with a small extra zoom if needed.
    # First try scale that covers screen without extra zoom:
    canvas = scale_letterbox_allow_zoom(pil_img, scr_w, scr_h, min_zoom=1.0)

    # We want some scroll range. If the original scaled image (before cropping) had more height than scr_h,
    # we can derive scroll. To simplify, re-scale a version with a *slightly larger* min_zoom when necessary.
    # Compute a small zoom factor: if no extra vertical room, set min_zoom = 1.05 (5% zoom).
    # Recreate a "taller canvas" to allow vertical movement.
    # We'll measure if there's available scroll by temporarily scaling with min_zoom=1.0 and checking.
    # To be robust, always create a source image that is >= scr_h in height and then we'll pan its crop.
    # Create a source image with a small extra zoom if needed:
    temp = scale_letterbox_allow_zoom(pil_img, scr_w, scr_h, min_zoom=1.0)
    # If temp is exactly screen, try small zoom
    if temp.size[1] == scr_h and temp.size[0] == scr_w:
        # small zoom to create subtle motion
        source = scale_letterbox_allow_zoom(pil_img, scr_w, scr_h, min_zoom=1.05)
    else:
        source = temp

    # Now source is >= scr_w x scr_h; to create scrolling, we'll slide a scr_w x scr_h window vertically over source.
    src_w, src_h = source.size
    max_scroll = max(0, src_h - scr_h)

    # Convert source to pygame surface once; we'll blit different portions by creating subsurfaces via Surface.copy
    source_surf = pil_to_surface(source)

    # Animation loop: scroll top -> bottom over 'seconds' with easing
    total_frames = max(1, int(seconds * fps))
    clock = pygame.time.Clock()

    for frame in range(total_frames):
        t = frame / (total_frames - 1) if total_frames > 1 else 1.0
        eased = ease_in_out(t)
        offset_y = int(eased * max_scroll)

        # We need to blit the portion of source_surf starting at y=offset_y, height=scr_h.
        # pygame doesn't support cropping a Surface by parameters directly, so we use subsurface if possible.
        try:
            view_rect = pygame.Rect(0, offset_y, scr_w, scr_h)
            portion = source_surf.subsurface(view_rect)
            screen.blit(portion, (0, 0))
        except Exception:
            # fallback: convert full source surface to string and create a new surface for the crop
            tmp = pygame.Surface((scr_w, scr_h), pygame.SRCALPHA)
            tmp.blit(source_surf, (0, -offset_y))
            screen.blit(tmp, (0, 0))

        pygame.display.flip()

        # handle events so ESC/q can quit
        for ev in pygame.event.get():
            if ev.type == pygame.KEYDOWN and ev.key in (pygame.K_ESCAPE, pygame.K_q):
                raise KeyboardInterrupt
            if ev.type == pygame.QUIT:
                raise KeyboardInterrupt

        clock.tick(fps)

def collect_image_files(folder: Path):
    exts = ("*.png", "*.jpg", "*.jpeg", "*.webp", "*.bmp")
    files = []
    for e in exts:
        files.extend(sorted(folder.glob(e)))
    return files

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 show_folder_scroll.py images_folder [seconds_each]")
        sys.exit(1)

    folder = Path(sys.argv[1])
    if not folder.exists() or not folder.is_dir():
        print("Folder not found:", folder)
        sys.exit(1)

    seconds = 5.0
    if len(sys.argv) >= 3:
        try:
            seconds = float(sys.argv[2])
        except Exception:
            pass

    files = collect_image_files(folder)
    if not files:
        print("No images found in folder:", folder)
        sys.exit(1)

    print(f"Found {len(files)} images. Press ESC or 'q' to exit.")

    pygame.init()
    pygame.display.init()
    info = pygame.display.Info()
    scr_w, scr_h = info.current_w, info.current_h
    screen = pygame.display.set_mode((scr_w, scr_h), pygame.FULLSCREEN)
    pygame.mouse.set_visible(False)

    try:
        idx = 0
        while True:
            path = files[idx % len(files)]
            try:
                pil = Image.open(path).convert("RGBA")
            except Exception as e:
                print("Failed to open", path, e)
                idx += 1
                continue
            try:
                show_image_with_scroll(screen, pil, scr_w, scr_h, seconds=seconds, fps=30)
            except KeyboardInterrupt:
                raise
            except Exception as e:
                # If animation fails for some image, print and continue
                print("Error while displaying", path, e)
            idx += 1
    except KeyboardInterrupt:
        pass
    finally:
        pygame.quit()

if __name__ == "__main__":
    main()
