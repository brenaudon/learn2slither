"""
This script handles the rendering of a snake game using Pygame. It includes functions for loading images,
drawing the game board, displaying menus (home, pause, game over, settings, ...), and creating UI elements like sliders and list boxes.

Dependencies:
    - os
    - math
    - time
    - pygame
    - typing (List, Tuple)
"""

import os
import math
import time
import pygame
from typing import List, Tuple


CELL = 48
"""Size of one grid cell (pixels).
@type: int
"""

MARGIN = 4
"""Margin between grid cells (pixels).
@type: int
"""


def load_images(cell_size: int, assets_path="assets"):
    """
    Load and scale game images from the assets directory.

    @param cell_size: Size to scale images to (width and height)
    @param assets_path: Path to the assets directory

    @return: Dictionary of loaded and scaled images
    """
    def _ld(name):
        """
        Load and scale a single image.

        @param name: Filename of the image to load

        @return: Scaled Pygame surface
        """
        surf = pygame.image.load(os.path.join(assets_path, name)).convert_alpha()
        return pygame.transform.smoothscale(surf, (cell_size, cell_size))

    imgs = {
        "green": _ld("green_apple.png"),
        "red": _ld("red_apple.png"),
    }

    return {
        "green": imgs["green"],
        "red": imgs["red"],
    }


def blit_scaled_center(screen, img, cell_x, cell_y, scale = 1.0):
    """
    Scale `img` by `scale` and blit centered in the (cell_x, cell_y) tile.

    @param screen: Pygame display surface
    @param img: Pygame surface to scale and blit
    @param cell_x: X coordinate of the cell
    @param cell_y: Y coordinate of the cell
    @param scale: Scaling factor

    @return: None
    """
    w = h = max(1, int(CELL * scale))
    scaled = pygame.transform.smoothscale(img, (w, h))
    px = cell_x * CELL + (CELL - w) // 2 + MARGIN // 2
    py = cell_y * CELL + (CELL - h) // 2 + MARGIN // 2
    screen.blit(scaled, (px, py))


def draw_cell(screen, x, y, color):
    """
    Draw a single cell at (x, y) with the specified color.

    @param screen: Pygame display surface
    @param x: X coordinate of the cell
    @param y: Y coordinate of the cell
    @param color: Color to fill the cell with

    @return: None
    """
    r = pygame.Rect(x * CELL + MARGIN , y * CELL + MARGIN, CELL - MARGIN, CELL - MARGIN)
    pygame.draw.rect(screen, color, r)


def draw_board(screen, board, grid_size, imgs, percentage=1.0):
    """
    Draw the game board on the screen.

    @param screen: Pygame display surface
    @param board: Dictionary representing the game state
    @param grid_size: Size of the game grid (grid_size x grid_size)
    @param imgs: Dictionary of loaded images
    @param percentage: Animation percentage for scaling effects (0.0 to 1.0)

    @return: None
    """
    bg = (68, 90, 144)
    empty_odd = (45, 60, 96)
    empty_even = (57, 69, 107)
    snake_color = (108, 190, 66)

    amp = 0.10
    scale = 0.7 + amp * math.sin(percentage * 2 * math.pi)

    screen.fill(bg)
    for y in range(grid_size):
        for x in range(grid_size):
            if (x + y) % 2 == 0:
                draw_cell(screen, x, y, empty_even)
            else:
                draw_cell(screen, x, y, empty_odd)
    for (gx, gy) in board["greens"]:
        blit_scaled_center(screen, imgs["green"], gx, gy, scale)
    if board["red"] is not None:
        rx, ry = board["red"]
        blit_scaled_center(screen, imgs["red"], rx, ry, scale)

    snake: List[Tuple[int, int]] = board.get("snake", [])
    if not snake: return

    for i in range(len(snake)):
        x, y = snake[i]
        draw_cell(screen, x, y, snake_color)

    head_x = snake[0][0] * CELL
    head_y = snake[0][1] * CELL
    match board.get("head_dir", "UP"):
        case "UP":
            pygame.draw.rect(screen, (0, 0, 0), (head_x + CELL // 4 + 1, head_y + CELL // 8, CELL // 8, CELL // 4))
            pygame.draw.rect(screen, (0, 0, 0), (head_x + 5 * CELL // 8 + 1, head_y + CELL // 8, CELL // 8, CELL // 4))
        case "DOWN":
            pygame.draw.rect(screen, (0, 0, 0), (head_x + CELL // 4 + 1, head_y + 5 * CELL // 8, CELL // 8, CELL // 4))
            pygame.draw.rect(screen, (0, 0, 0), (head_x + 5 * CELL // 8 + 1, head_y + 5 * CELL // 8, CELL // 8, CELL // 4))
        case "LEFT":
            pygame.draw.rect(screen, (0, 0, 0), (head_x + CELL // 8, head_y + CELL // 4 + 1, CELL // 4, CELL // 8))
            pygame.draw.rect(screen, (0, 0, 0), (head_x + CELL // 8, head_y + 5 * CELL // 8 + 1, CELL // 4, CELL // 8))
        case "RIGHT":
            pygame.draw.rect(screen, (0, 0, 0), (head_x + 5 * CELL // 8, head_y + CELL // 4 + 1, CELL // 4, CELL // 8))
            pygame.draw.rect(screen, (0, 0, 0), (head_x + 5 * CELL // 8, head_y + 5 * CELL // 8 + 1, CELL // 4, CELL // 8))
        case _:
            pass


def _draw_round_rect(surf, rect, color, radius=16, width=0):
    """
    Draw a rectangle with rounded corners.

    @param surf: Pygame surface to draw on
    @param rect: Rectangle area to draw (pygame.Rect)
    @param color: Color of the rectangle
    @param radius: Radius of the rounded corners
    @param width: Width of the rectangle border (0 for filled)

    @return: None
    """
    pygame.draw.rect(surf, color, rect, width=width, border_radius=radius)


def _draw_shadow(surf, rect, radius=16, offset=(0, 8), blur=12, alpha=140):
    """
    Draw a shadow effect for a rounded rectangle.

    @param surf: Pygame surface to draw on
    @param rect: Rectangle area for the shadow (pygame.Rect)
    @param radius: Radius of the rounded corners
    @param offset: Offset of the shadow (x, y)
    @param blur: Number of blur layers
    @param alpha: Maximum alpha value for the shadow

    @return: None
    """
    x, y, w, h = rect
    ox, oy = offset
    for i in range(blur):
        a = int(alpha * (1 - i/(blur+1)))
        s = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.rect(s, (0, 0, 0, a), s.get_rect(), border_radius=radius + i)
        surf.blit(s, (x + ox, y + oy))


def _button(surf, rect, text, font, *, base=(45, 50, 58), hover=(70, 80, 95), text_col=(240, 244, 248)):
    """
    Draw a button and handle hover/click state.

    @param surf: Pygame surface to draw on
    @param rect: Rectangle area for the button (pygame.Rect)
    @param text: Text to display on the button
    @param font: Pygame font to use for the text
    @param base: Base color of the button
    @param hover: Hover color of the button
    @param text_col: Color of the button text

    @return: Tuple (hovered: bool, clicked: bool)
    """
    mouse = pygame.mouse.get_pos()
    pressed = pygame.mouse.get_pressed()[0]
    hl = rect.collidepoint(mouse)
    col = hover if hl else base
    _draw_shadow(surf, rect, radius=14, offset=(0, 4), blur=6, alpha=90)
    _draw_round_rect(surf, rect, col, radius=14)
    label = font.render(text, True, text_col)
    surf.blit(label, label.get_rect(center=rect.center))
    clicked = hl and pressed
    return hl, clicked


def _fast_blur(surface, scale=0.22, passes=2):
    """
    Cheap 'Gaussian-like' blur:
    scale down to a small surface then scale back up; repeat 'passes' times.

    @param surface: Pygame surface to blur
    @param scale: Scaling factor for downscaling
    @param passes: Number of blur passes

    @return: Blurred Pygame surface
    """
    w, h = surface.get_size()
    tmp = surface
    for _ in range(passes):
        small_w = max(1, int(w * scale))
        small_h = max(1, int(h * scale))
        small = pygame.transform.smoothscale(tmp, (small_w, small_h))
        tmp   = pygame.transform.smoothscale(small, (w, h))
    return tmp


def game_over_screen(screen, *, bg_surface, length, bg_dim=160):
    """
    Draws GAme Over screen. Blocks until user picks an option. Returns: 'restart', 'quit', or 'quit_window'.

    @param screen: Pygame display surface
    @param bg_surface: Background surface to blur
    @param length: Length of the snake achieved
    @param bg_dim: Alpha value for dimming the background (0-255)

    @return: User choice as a string
    """
    w, h = screen.get_size()
    clock = pygame.time.Clock()
    title_f = pygame.font.SysFont(None, 64, bold=True)
    big_f   = pygame.font.SysFont(None, 36)
    small_f = pygame.font.SysFont(None, 24)

    # Precompute blur (once)
    blurred = _fast_blur(bg_surface, scale=0.22, passes=2)
    # Dim the blurred bg slightly
    dim = pygame.Surface((w, h), pygame.SRCALPHA)
    dim.fill((0, 0, 0, bg_dim))  # alpha 0..255

    panel = pygame.Rect(w // 2 - 360, h // 2 - 180, 720, 320)
    btn_w, btn_h, gap = 200, 56, 20
    btn_restart = pygame.Rect(w // 2 - btn_w - gap // 2, panel.bottom - btn_h - 24, btn_w, btn_h)
    btn_quit = pygame.Rect(w // 2 + gap // 2, panel.bottom - btn_h - 24, btn_w, btn_h)

    # fade-in
    t0 = time.time()
    fade_ms = 280
    focused = 0  # 0=restart, 1=quit
    buttons = [btn_restart, btn_quit]
    pulser = 0.0

    # allow keyboard repeat after a short delay
    pygame.key.set_repeat(250, 40)

    choice = None
    while choice is None:
        dt = clock.tick(60) / 1000.0
        pulser += dt

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return "quit_window"
            if e.type == pygame.KEYDOWN:
                if e.key in (pygame.K_ESCAPE, pygame.K_q):
                    return "quit"
                if e.key == pygame.K_r:
                    return "restart"
                if e.key in (pygame.K_LEFT, pygame.K_a):
                    focused = (focused - 1) % 2
                if e.key in (pygame.K_RIGHT, pygame.K_d):
                    focused = (focused + 1) % 2
                if e.key == pygame.K_RETURN:
                    choice = ("restart", "quit")[focused]
            if e.type == pygame.MOUSEBUTTONUP and e.button == 1:
                # clicks handled after drawing to respect hover state
                pass

        # background: blurred screenshot + dim
        screen.blit(blurred, (0, 0))
        screen.blit(dim, (0, 0))

        # panel
        _draw_shadow(screen, panel, radius=20, offset=(0, 10), blur=12, alpha=140)
        _draw_round_rect(screen, panel, (28, 32, 38), radius=20)

        # title
        title = title_f.render("Game Over", True, (240, 244, 248))
        screen.blit(title, title.get_rect(midtop=(w // 2, panel.top + 24)))

        # stats
        y_stats = panel.top + 100
        l_txt = big_f.render(f"Length: {length}", True, (220, 225, 232))
        screen.blit(l_txt, l_txt.get_rect(center=(w // 2, y_stats)))
        y_stats += 34

        # hint (pulsing)
        pulse = 0.6 + 0.4 * (0.5 + 0.5 * math.sin(pulser * 4.0))
        hint = small_f.render("Press R to Restart — Q/Esc to Quit", True,
                              (int(200 * pulse), int(210 * pulse), int(220 * pulse)))
        screen.blit(hint, hint.get_rect(midtop=(w // 2, panel.bottom - btn_h - 60)))

        # buttons
        _, clicked_restart = _button(screen, btn_restart, "Restart", big_f)
        _, clicked_quit = _button(screen, btn_quit, "Quit", big_f)

        # keyboard focus ring
        focus_rect = buttons[focused].inflate(8, 8)
        pygame.draw.rect(screen, (86, 156, 255), focus_rect, width=2, border_radius=18)

        if clicked_restart:
            choice = "restart"
        if clicked_quit:
            choice = "quit"

        # fade overlay
        elapsed = (time.time() - t0) * 1000
        if elapsed < fade_ms:
            a = int(255 * (1 - elapsed / fade_ms))
            f = pygame.Surface((w, h))
            f.set_alpha(a)
            f.fill((0, 0, 0))
            screen.blit(f, (0, 0))

        pygame.display.flip()

    return choice


def home_menu(screen, *, bg_color=(18, 20, 24)):
    """
    Draws Home menu. Blocks until user picks an option. Returns: 'play', 'ai', 'settings', or 'quit'.

    @param screen: Pygame display surface
    @param bg_color: Background color of the menu

    @return: User choice as a string
    """
    w, h = screen.get_size()
    clock = pygame.time.Clock()
    title_f = pygame.font.SysFont(None, 64, bold=True)
    sub_f = pygame.font.SysFont(None, 22)
    btn_f = pygame.font.SysFont(None, 32)
    small_f = pygame.font.SysFont(None, 24)

    # responsive layout
    panel_w, panel_h = min(760, int(w * 0.9)), min(420, int(h * 0.75))
    panel = pygame.Rect((w - panel_w) // 2, (h - panel_h) // 2, panel_w, panel_h)

    gap = 16
    bw = min(300, panel_w - 120)
    bh = 56
    cx = w // 2
    y0 = panel.centery - bh - gap

    btn_play = pygame.Rect(cx - bw // 2, y0, bw, bh)
    btn_ai = pygame.Rect(cx - bw // 2, y0 + (bh + gap), bw, bh)
    btn_settings = pygame.Rect(cx - bw // 2, y0 + 2 * (bh + gap), bw, bh)

    fade_ms = 220
    t0 = time.time()
    focused = 0  # 0=Play, 1=AI, 2=Settings (keyboard)
    buttons = [btn_play, btn_ai, btn_settings]
    pulser = 0.0

    while True:
        dt = clock.tick(60) / 1000.0
        pulser += dt

        for e in pygame.event.get([pygame.QUIT, pygame.KEYDOWN]):
            if e.type == pygame.QUIT:
                return "quit"
            if e.type == pygame.KEYDOWN:
                if e.key in (pygame.K_ESCAPE, pygame.K_q):
                    return "quit"
                elif e.key in (pygame.K_DOWN, pygame.K_s):
                    focused = (focused + 1) % 3
                elif e.key in (pygame.K_UP, pygame.K_w):
                    focused = (focused - 1) % 3
                elif e.key == pygame.K_RETURN:
                    return ("play", "ai", "settings")[focused]

        # bg
        screen.fill(bg_color)

        # panel with shadow
        _draw_shadow(screen, panel, radius=22, offset=(0, 10), blur=14, alpha=150)
        _draw_round_rect(screen, panel, (28, 32, 38), radius=22)

        # title + subtitle
        title = title_f.render("Learn2Slither", True, (240, 244, 248))
        screen.blit(title, title.get_rect(midtop=(w // 2, panel.top + 26)))
        subtitle = sub_f.render("Reinforcement-learning snake — choose an option", True, (170, 178, 188))
        screen.blit(subtitle, subtitle.get_rect(midtop=(w // 2, panel.top + 26 + 52)))

        # draw buttons (mouse)
        _, click_play = _button(screen, btn_play, "Play", btn_f)
        _, click_ai = _button(screen, btn_ai, "AI Play", btn_f)
        _, click_set = _button(screen, btn_settings, "Settings", btn_f)

        pulse = 0.6 + 0.4 * (0.5 + 0.5 * math.sin(pulser * 4.0))
        hint = small_f.render("Press Q/Esc to Quit", True,
                              (int(200 * pulse), int(210 * pulse), int(220 * pulse)))
        screen.blit(hint, hint.get_rect(midtop=(w // 2, panel.bottom - 32)))

        # keyboard focus ring
        focus_rect = buttons[focused].inflate(8, 8)
        pygame.draw.rect(screen, (86, 156, 255), focus_rect, width=2, border_radius=18)

        # clicks
        if click_play: return "play"
        if click_ai:   return "ai"
        if click_set:  return "settings"

        # fade-in overlay
        elapsed = (time.time() - t0) * 1000.0
        if elapsed < fade_ms:
            a = int(255 * (1 - elapsed / fade_ms))
            f = pygame.Surface((w, h))
            f.set_alpha(a)
            f.fill((0, 0, 0))
            screen.blit(f, (0, 0))

        pygame.display.flip()


def pause_menu(screen, *, bg_surface=None, bg_dim=140):
    """
    Draws Pause menu.
    Blocks until user chooses an action.
    Returns: 'resume', 'home', or 'quit'.
    Keys: Space/Enter -> resume, H -> home, Esc/Q -> quit.

    @param screen: Pygame display surface
    @param bg_surface: Background surface to blur (if None, uses current screen)
    @param bg_dim: Alpha value for dimming the background (0-255)

    @return: User choice as a string
    """
    w, h = screen.get_size()
    clock = pygame.time.Clock()
    title_f = pygame.font.SysFont(None, 56, bold=True)
    sub_f = pygame.font.SysFont(None, 22)
    btn_f = pygame.font.SysFont(None, 32)

    # backdrop: blurred screenshot if provided
    if bg_surface is None:
        bg_surface = screen.copy()
    blurred = _fast_blur(bg_surface, scale=0.22, passes=2)
    dim = pygame.Surface((w, h), pygame.SRCALPHA)
    dim.fill((0, 0, 0, bg_dim))

    # panel + buttons
    panel_w, panel_h = min(760, int(w * 0.9)), min(300, int(h * 0.7))
    panel = pygame.Rect((w - panel_w) // 2, (h - panel_h) // 2, panel_w, panel_h)

    bw, bh, gap = 220, 56, 18
    btn_resume = pygame.Rect(w // 2 - bw - gap // 2, panel.centery + 20, bw, bh)
    btn_home = pygame.Rect(w // 2 + gap // 2, panel.centery + 20, bw, bh)

    focused = 0  # 0=resume, 1=home (keyboard)
    buttons = [btn_resume, btn_home]

    fade_ms = 160
    t0 = time.time()
    pulser = 0.0

    while True:
        dt = clock.tick(60) / 1000.0
        pulser += dt

        for e in pygame.event.get([pygame.QUIT, pygame.KEYDOWN]):
            if e.type == pygame.QUIT:
                return "quit"
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    return "quit"
                elif e.key == pygame.K_RETURN:
                    return ("resume", "home")[focused]
                elif e.key == pygame.K_SPACE:
                    return "resume"
                elif e.key in (pygame.K_LEFT, pygame.K_a):
                    focused = (focused - 1) % 2
                elif e.key in (pygame.K_RIGHT, pygame.K_d):
                    focused = (focused + 1) % 2
                elif e.key == pygame.K_h:
                    return "home"

        # background
        screen.blit(blurred, (0, 0))
        screen.blit(dim, (0, 0))

        # panel
        _draw_shadow(screen, panel, radius=20, offset=(0, 8), blur=12, alpha=140)
        _draw_round_rect(screen, panel, (28, 32, 38), radius=20)

        # title + hint
        title = title_f.render("Paused", True, (240, 244, 248))
        screen.blit(title, title.get_rect(midtop=(w // 2, panel.top + 22)))
        pulse = 0.6 + 0.4 * (0.5 + 0.5 * math.sin(pulser * 4.0))
        hint = sub_f.render("Space: Resume - H: Home - Esc: Quit", True,
                              (int(200 * pulse), int(210 * pulse), int(220 * pulse)))
        screen.blit(hint, hint.get_rect(midtop=(w // 2, panel.top + 22 + 46)))

        # buttons
        _, clicked_resume = _button(screen, btn_resume, "Resume", btn_f)
        _, clicked_home = _button(screen, btn_home, "Home", btn_f)

        # keyboard focus ring
        focus_rect = buttons[focused].inflate(8, 8)
        pygame.draw.rect(screen, (86, 156, 255), focus_rect, width=2, border_radius=18)

        if clicked_resume:
            return "resume"
        if clicked_home:
            return "home"

        # fade-in
        elapsed = (time.time() - t0) * 1000.0
        if elapsed < fade_ms:
            a = int(255 * (1 - elapsed / fade_ms))
            f = pygame.Surface((w, h))
            f.set_alpha(a)
            f.fill((0, 0, 0))
            screen.blit(f, (0, 0))

        pygame.display.flip()


class Slider:
    """
    A horizontal slider widget.
    """
    def __init__(self, rect, vmin, vmax, value, *, integer=True):
        """
        Initialize the slider.

        @param rect: Rectangle area for the slider (x, y, w, h)
        @param vmin: Minimum value of the slider
        @param vmax: Maximum value of the slider
        @param value: Initial value of the slider
        @param integer: Whether the slider value should be an integer
        """
        self.rect = pygame.Rect(rect)
        self.vmin = vmin
        self.vmax = vmax
        self.value = max(vmin, min(vmax, value))
        self.integer = integer
        self.dragging = False

    def _pos_to_value(self, x):
        """
        Convert a position x to a slider value.

        @param x: X coordinate to convert

        @return: Corresponding slider value
        """
        t = (x - self.rect.x) / max(1, self.rect.w)
        t = max(0.0, min(1.0, t))
        v = self.vmin + t * (self.vmax - self.vmin)
        if self.integer:
            v = round(v)
        return v

    def handle_event(self, e):
        """
        Handle Pygame events for the slider.

        @param e: Pygame event to handle

        @return: None
        """
        if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1 and self.rect.collidepoint(e.pos):
            self.dragging = True
            self.value = self._pos_to_value(e.pos[0])
        elif e.type == pygame.MOUSEBUTTONUP and e.button == 1:
            self.dragging = False
        elif e.type == pygame.MOUSEMOTION and self.dragging:
            self.value = self._pos_to_value(e.pos[0])

    def nudge(self, delta):
        """
        Nudge the slider value by delta.

        @param delta: Amount to nudge the slider value by

        @return: None
        """
        v = self.value + delta
        v = max(self.vmin, min(self.vmax, v))
        if self.integer:
            v = int(v)
        self.value = v

    def draw(self, surf, font, label, *, accent=(86, 156, 255), track=(55, 60, 68), fill=(86, 156, 255), text=(235, 239, 245)):
        """
        Draw the slider on the given surface.

        @param surf: Pygame surface to draw on
        @param font: Pygame font to use for text
        @param label: Label text for the slider
        @param accent: Color for the slider handle
        @param track: Color for the slider track
        @param fill: Color for the filled portion of the slider
        @param text: Color for the text

        @return: None
        """

        # label
        lab = font.render(f"{label}: {self.value}", True, text)
        surf.blit(lab, (self.rect.x, self.rect.y - 28))

        # track
        _draw_round_rect(surf, self.rect, track, radius=8)
        # fill
        if self.vmax > self.vmin:
            t = (self.value - self.vmin) / (self.vmax - self.vmin)
        else:
            t = 0.0
        fill_rect = pygame.Rect(self.rect.x, self.rect.y, int(self.rect.w * t), self.rect.h)
        _draw_round_rect(surf, fill_rect, fill, radius=8)

        # handle
        handle_x = self.rect.x + int(self.rect.w * t)
        handle = pygame.Rect(handle_x - 8, self.rect.y - 6, 16, self.rect.h + 12)
        _draw_shadow(surf, handle, radius=10, offset=(0,3), blur=6, alpha=80)
        _draw_round_rect(surf, handle, accent, radius=10)

# ---------- listbox widget ----------
class ListBox:
    """
    A scrollable list box widget.
    """
    def __init__(self, rect, items, selected=None):
        """
        Initialize the list box.

        @param rect: Rectangle area for the list box (x, y, w, h)
        @param items: List of string items to display
        @param selected: Initially selected item (string)
        """
        self.rect = pygame.Rect(rect)
        self.items = items[:]  # list of strings
        self.selected = 0 if items else -1
        if selected in items:
            self.selected = items.index(selected)
        self.scroll = 0  # index of first visible item
        self.item_h = 36
        self.pad = 6

    def set_items(self, items, keep_selection_name=None):
        """
        Update the list of items in the list box.

        @param items: New list of string items
        @param keep_selection_name: Item name to keep selected if it exists

        @return: None
        """
        self.items = items[:]
        if keep_selection_name and keep_selection_name in self.items:
            self.selected = self.items.index(keep_selection_name)
        else:
            self.selected = 0 if self.items else -1
        self.scroll = 0

    def handle_event(self, e):
        """
        Handle Pygame events for the list box.

        @param e: Pygame event to handle

        @return: None
        """
        if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1 and self.rect.collidepoint(e.pos):
            # pick by click
            idx = (e.pos[1] - self.rect.y) // self.item_h + self.scroll
            if 0 <= idx < len(self.items):
                self.selected = idx
        elif e.type == pygame.MOUSEWHEEL and self.rect.collidepoint(pygame.mouse.get_pos()):
            self.scroll = max(0, min(self.scroll - e.y, max(0, len(self.items) - self.visible_count())))
        elif e.type == pygame.KEYDOWN:
            if e.key in (pygame.K_DOWN, pygame.K_s):
                if self.selected < len(self.items) - 1:
                    self.selected += 1
                    if self.selected >= self.scroll + self.visible_count():
                        self.scroll += 1
            if e.key in (pygame.K_UP, pygame.K_w):
                if self.selected > 0:
                    self.selected -= 1
                    if self.selected < self.scroll:
                        self.scroll -= 1

    def visible_count(self):
        """
        Calculate the number of visible items in the list box.

        @return: Number of visible items
        """
        return max(1, self.rect.h // self.item_h)

    def get_selected(self):
        """
        Get the currently selected item.

        @return: Selected item string or None if no selection
        """
        if 0 <= self.selected < len(self.items):
            return self.items[self.selected]
        return None

    def draw(self, surf, font, label, *, bg=(34, 38, 44), row=(45, 50, 58), row_hover=(70, 80, 95),
             text=(235, 239, 245), muted=(170, 178, 189), accent=(86, 156, 255)):
        """
        Draw the list box on the given surface.

        @param surf: Pygame surface to draw on
        @param font: Pygame font to use for text
        @param label: Label text for the list box
        @param bg: Background color of the list box
        @param row: Color of the list box rows
        @param row_hover: Color of the row when hovered
        @param text: Color of the item text
        @param muted: Color for muted text
        @param accent: Color for the selected item accent

        @return: None
        """

        # label
        lab = font.render(label, True, muted)
        surf.blit(lab, (self.rect.x, self.rect.y - 28))

        # box
        _draw_shadow(surf, self.rect, radius=12, offset=(0, 4), blur=8, alpha=100)
        _draw_round_rect(surf, self.rect, bg, radius=12)

        # items
        mx, my = pygame.mouse.get_pos()
        hover_idx = None
        if self.rect.collidepoint((mx, my)):
            hover_idx = (my - self.rect.y) // self.item_h + self.scroll

        vis = self.visible_count()
        for i in range(vis):
            idx = self.scroll + i
            if idx >= len(self.items):
                break
            r = pygame.Rect(self.rect.x + self.pad, self.rect.y + i * self.item_h + self.pad // 2,
                            self.rect.w - 2 * self.pad, self.item_h - self.pad)
            bgc = row_hover if idx == hover_idx else row
            if idx == self.selected:
                # selection tint
                bgc = tuple(min(255, int(a * 0.6 + b * 0.4)) for a, b in zip(bgc, accent))
                pygame.draw.rect(surf, bgc, r, border_radius=8)
                pygame.draw.rect(surf, accent, r, width=2, border_radius=8)
            else:
                pygame.draw.rect(surf, bgc, r, border_radius=8)
            txt = font.render(self.items[idx], True, text)
            surf.blit(txt, (r.x + 10, r.y + (r.h - txt.get_height()) // 2))

        # empty note
        if not self.items:
            note = font.render("(no models found)", True, muted)
            surf.blit(note, note.get_rect(center=self.rect.center))

# ---------- utilities ----------
def _scan_models(models_dir):
    """
    Scan the models directory for available model files (.txt).
    Returns a sorted list of model names (file stems).

    @param models_dir: Directory to scan for model files

    @return: Sorted list of model names
    """
    names = []
    try:
        for fn in os.listdir(models_dir):
            if fn.lower().endswith(".txt"):
                names.append(os.path.splitext(fn)[0])  # stem as model name
    except FileNotFoundError:
        pass
    return sorted(names, key=str.lower)

# ---------- settings screen ----------
def settings_screen(screen, *, grid_size=10, model_name=None, models_dir="models", bg_color=(18, 20, 24)):
    """
    Draws Settings screen for grid size and model selection.
    Blocks until user saves or backs out.
    Returns: ("save", grid, model) or ("back", grid, model) or ("quit", grid, model)

    @param screen: Pygame display surface
    @param grid_size: Initial grid size value
    @param model_name: Initially selected model name
    @param models_dir: Directory to scan for model files
    @param bg_color: Background color of the screen

    @return: Tuple (action: str, grid_size: int, model_name: str)
    """
    w, h = screen.get_size()

    title_f = pygame.font.SysFont(None, 56, bold=True)
    small_f = pygame.font.SysFont(None, 22)
    body_f = pygame.font.SysFont(None, 28)
    btn_f = pygame.font.SysFont(None, 30)

    # panel
    panel_w, panel_h = min(900, int(w * 0.92)), min(540, int(h * 0.85))
    panel = pygame.Rect((w - panel_w) // 2, (h - panel_h) // 2, panel_w, panel_h)

    # left: slider area
    slider_w = min(420, panel_w // 2 - 40)
    slider_rect = pygame.Rect(panel.left + 40, panel.top + 140, slider_w, 18)

    slider = Slider(slider_rect, 8, 20, grid_size, integer=True)

    # right: models list
    list_w = panel_w - slider_w - 40 - 40 - 40
    list_h = panel_h - 220
    list_rect = pygame.Rect(panel.left + 40 + slider_w + 40, panel.top + 120, list_w, list_h)

    model_items = _scan_models(models_dir)
    if model_name is None and model_items:
        model_name = model_items[0]
    listbox = ListBox(list_rect, model_items, selected=model_name)

    # buttons
    bw, bh, gap = 180, 54, 16
    btn_save = pygame.Rect(panel.right - bw - 24, panel.bottom - bh - 20, bw, bh)
    btn_back = pygame.Rect(btn_save.x - bw - gap,  panel.bottom - bh - 20, bw, bh)

    fade_ms = 220
    t0 = time.time()

    while True:
        # events
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return "quit", slider.value, listbox.get_selected()
            if e.type == pygame.KEYDOWN:
                if e.key in (pygame.K_ESCAPE, pygame.K_q):
                    return "back", slider.value, listbox.get_selected()
                elif e.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    return "save", slider.value, listbox.get_selected()
                elif e.key in (pygame.K_LEFT, pygame.K_a):
                    slider.nudge(-1)
                elif e.key in (pygame.K_RIGHT, pygame.K_d):
                    slider.nudge(+1)

            slider.handle_event(e)
            listbox.handle_event(e)

        # background/panel
        screen.fill(bg_color)
        _draw_shadow(screen, panel, radius=22, offset=(0,10), blur=14, alpha=150)
        _draw_round_rect(screen, panel, (28, 32, 38), radius=22)

        # title + subtitle
        title = title_f.render("Settings", True, (240, 244, 248))
        screen.blit(title, title.get_rect(midtop=(w // 2, panel.top + 22)))
        subtitle = small_f.render("Configure grid size and pick an AI model", True, (170, 178, 188))
        screen.blit(subtitle, subtitle.get_rect(midtop=(w // 2, panel.top + 22 + 46)))

        # left column: grid size slider
        left_title = body_f.render("Grid Size", True, (200, 210, 220))
        screen.blit(left_title, (panel.left + 40, panel.top + 90))
        slider.draw(screen, body_f, "Grid", accent=(86, 156, 255))

        # right column: model list
        listbox.draw(screen, body_f, label="Models", accent=(86, 156, 255))

        # buttons
        _, click_back = _button(screen, btn_back, "Back", btn_f)
        _, click_save = _button(screen, btn_save, "Save", btn_f)

        if click_back:
            return "back", slider.value, listbox.get_selected()
        if click_save:
            return "save", slider.value, listbox.get_selected()

        # fade-in
        elapsed = (time.time() - t0) * 1000.0
        if elapsed < fade_ms:
            a = int(255 * (1 - elapsed / fade_ms))
            f = pygame.Surface((w, h))
            f.set_alpha(a)
            f.fill((0, 0, 0))
            screen.blit(f, (0, 0))

        pygame.display.flip()
