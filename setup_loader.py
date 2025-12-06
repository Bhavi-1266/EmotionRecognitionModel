#!/usr/bin/env python3
"""
setup_loader.py
Shows a fullscreen loading UI while installing ONLY:
  - python3-pygame
  - python3-pil

On success: exits with code 0.
On failure: shows ERROR screen and waits for a keypress (then exits nonzero).
Run from a terminal (so sudo can prompt).
"""
import os
import sys
import time
import subprocess
from pathlib import Path

# Try import pygame for UI; if missing and user can't install, we fallback to textual output.
try:
    import pygame
except Exception:
    pygame = None

REQUIRED_APT_PKGS = ["python3-pygame", "python3-pil"]
BG = (10,10,10)
WHITE = (240,240,240)
RED = (220,80,80)
YELLOW = (240,200,60)

def run_cmd(cmd):
    try:
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, check=False)
        return proc.returncode, proc.stdout
    except Exception as e:
        return 1, str(e)

def apt_install(pkgs):
    """Install apt packages; uses sudo if not root."""
    if os.geteuid() != 0:
        rc, out = run_cmd(["sudo", "apt", "update", "-y"])
        if rc != 0:
            return False, f"apt update failed: {out.splitlines()[-1][:200]}"
        rc, out = run_cmd(["sudo", "apt", "install", "-y"] + pkgs)
        if rc != 0:
            return False, f"apt install failed: {out.splitlines()[-1][:200]}"
        return True, "installed"
    else:
        rc, out = run_cmd(["apt", "update", "-y"])
        if rc != 0:
            return False, f"apt update failed: {out.splitlines()[-1][:200]}"
        rc, out = run_cmd(["apt", "install", "-y"] + pkgs)
        if rc != 0:
            return False, f"apt install failed: {out.splitlines()[-1][:200]}"
        return True, "installed"

def show_text(screen, lines, font, color=WHITE):
    screen.fill(BG)
    w,h = screen.get_size()
    total = sum(font.size(line)[1] + 8 for line in lines)
    y = (h - total) // 2
    for line in lines:
        surf = font.render(line, True, color)
        screen.blit(surf, ((w - surf.get_width())//2, y))
        y += surf.get_height() + 8
    pygame.display.flip()

def run_ui_install():
    """Runs apt install with a pygame UI. Returns (ok, message)."""
    if pygame is None:
        # No pygame available — run apt headless (user will see terminal output)
        return apt_install(REQUIRED_APT_PKGS)

    pygame.init()
    pygame.display.init()
    info = pygame.display.Info()
    screen = pygame.display.set_mode((info.current_w, info.current_h), pygame.FULLSCREEN)
    pygame.mouse.set_visible(False)
    font = pygame.font.SysFont("Arial", 44)
    small = pygame.font.SysFont("Arial", 28)

    show_text(screen, ["Preparing setup...", "", "Installing system packages..."], font, color=YELLOW)
    pygame.event.pump()
    time.sleep(0.4)

    ok, msg = apt_install(REQUIRED_APT_PKGS)
    if not ok:
        show_text(screen, ["ERROR LOADING", "", msg[:200]], font, color=RED)
        # keep the error screen until user presses a key
        waiting = True
        while waiting:
            for ev in pygame.event.get():
                if ev.type == pygame.KEYDOWN or ev.type == pygame.QUIT:
                    waiting = False
            time.sleep(0.1)
        pygame.quit()
        return False, msg
    else:
        show_text(screen, ["Setup complete.", "", "You may now run the launcher."], font, color=WHITE)
        time.sleep(1.0)
        pygame.quit()
        return True, "installed"

def main():
    ok, msg = run_ui_install()
    if not ok:
        print("Setup failed:", msg)
        return 2
    print("Setup succeeded:", msg)
    return 0

if __name__ == "__main__":
    sys.exit(main())
