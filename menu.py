#!/usr/bin/env python3
import pygame
import os

def run_menu():
    # ---------------- CONFIG ----------------
    BG_COLOR = (18, 18, 18)
    TOPBAR_COLOR = (28, 28, 28)

    BUTTON_COLOR = (50, 90, 160)
    BUTTON_HOVER = (70, 120, 200)

    ITEM_BG = (35, 35, 35)
    HOVER_COLOR = (60, 60, 60)

    TEXT_COLOR = (230, 230, 230)

    IMAGE_DIR = "eposter_cache"

    IMAGE_MAX_WIDTH = 1100
    IMAGE_MAX_HEIGHT = 650

    TOPBAR_HEIGHT = 70
    BUTTON_WIDTH = 220
    BUTTON_HEIGHT = 45

    ITEM_PADDING = 25
    TEXT_HEIGHT = 30
    SCROLL_SPEED = 50
    # ----------------------------------------

    pygame.init()
    pygame.mouse.set_visible(True)

    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    clock = pygame.time.Clock()

    font = pygame.font.SysFont("arial", 22)
    button_font = pygame.font.SysFont("arial", 24, bold=True)

    WIDTH, HEIGHT = screen.get_size()

    # -------- Timed Poster Button --------
    button_rect = pygame.Rect(
        30,
        TOPBAR_HEIGHT // 2 - BUTTON_HEIGHT // 2,
        BUTTON_WIDTH,
        BUTTON_HEIGHT
    )

    # -------- Load Images --------
    items = []

    def scale_image(img, max_w, max_h):
        w, h = img.get_size()
        scale = min(max_w / w, max_h / h)
        return pygame.transform.smoothscale(img, (int(w * scale), int(h * scale)))

    if not os.path.isdir(IMAGE_DIR):
        pygame.quit()
        return ("EXIT", None)

    for name in sorted(os.listdir(IMAGE_DIR)):
        if name.lower().endswith((".png", ".jpg", ".jpeg")):
            path = os.path.abspath(os.path.join(IMAGE_DIR, name))
            img = pygame.image.load(path).convert_alpha()
            img = scale_image(img, IMAGE_MAX_WIDTH, IMAGE_MAX_HEIGHT)

            height = img.get_height() + TEXT_HEIGHT + ITEM_PADDING * 2

            items.append({
                "image": img,
                "path": path,
                "height": height
            })

    scroll_y = 0

    # ---------------- MAIN LOOP ----------------
    hover_index = None
    while True:
        clock.tick(60)
        screen.fill(BG_COLOR)

        mx, my = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return ("EXIT", None)

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.quit()
                return ("EXIT", None)

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Timed Poster button
                if button_rect.collidepoint(mx, my):
                    return ("TIMED_POSTER", None)

                # Image click
                if hover_index is not None:
                    return ("IMAGE_SELECTED", items[hover_index]["path"])

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4 and my > TOPBAR_HEIGHT:
                    scroll_y += SCROLL_SPEED
                elif event.button == 5 and my > TOPBAR_HEIGHT:
                    scroll_y -= SCROLL_SPEED

        # Clamp scrolling
        total_height = sum(i["height"] for i in items)
        max_scroll = max(0, total_height - (HEIGHT - TOPBAR_HEIGHT))
        scroll_y = max(-max_scroll, min(0, scroll_y))

        # -------- Top Bar --------
        pygame.draw.rect(screen, TOPBAR_COLOR, (0, 0, WIDTH, TOPBAR_HEIGHT))

        btn_color = BUTTON_HOVER if button_rect.collidepoint(mx, my) else BUTTON_COLOR
        pygame.draw.rect(screen, btn_color, button_rect, border_radius=8)

        text = button_font.render("Timed Poster", True, TEXT_COLOR)
        screen.blit(
            text,
            (button_rect.centerx - text.get_width() // 2,
             button_rect.centery - text.get_height() // 2)
        )

        # -------- Posters --------
        y = scroll_y + TOPBAR_HEIGHT + 20

        for i, item in enumerate(items):
            rect = pygame.Rect(40, y, WIDTH - 80, item["height"])

            if rect.collidepoint(mx, my):
                hover_index = i
                bg = HOVER_COLOR
            else:
                bg = ITEM_BG

            pygame.draw.rect(screen, bg, rect, border_radius=12)

            img = item["image"]
            screen.blit(
                img,
                (WIDTH // 2 - img.get_width() // 2, y + ITEM_PADDING)
            )

            y += item["height"] + 25

        pygame.display.flip()


    # ---------------- END MAIN LOOP ----------------
