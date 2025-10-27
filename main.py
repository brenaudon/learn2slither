import math
import os
import pygame
from typing import List, Tuple

GRID = 10
CELL = 48
MARGIN = 4
W, H = GRID * CELL, GRID * CELL
SNAKE_COLOR = (108, 190, 66)

def load_images(cell_size: int):
    def _ld(name):
        surf = pygame.image.load(os.path.join("assets", name)).convert_alpha()
        return pygame.transform.smoothscale(surf, (cell_size, cell_size))

    imgs = {
        "green": _ld("green_apple.png"),
        "red":   _ld("red_apple.png"),
    }

    return {
        "green": imgs["green"],
        "red": imgs["red"],
    }

def get_board():
    # Replace with: ask C++ over socket/FIFO
    # Return dict: {"snake":[(hx,hy),(x,y),...], "greens":[(x,y),(x,y)], "red":(x,y) or None}
    return {
        "snake": [(5,5), (5,6), (5,7), (6,7), (7,7), (7,6), (7,5), (7,4), (6,4),
                  (5,4), (4,4), (4,5), (4,6), (4,7), (3,7), (2,7), (2,6), (2,5),
                  (3,5), (3,4), (3,3), (4,3), (5,3)],
        "greens": [(2,3),(8,1)],
        "red": (7,8),
        "head_dir": "UP",
    }

def blit_scaled_center(screen, img, cell_x, cell_y, scale = 1.0):
    """Scale `img` by `scale` and blit centered in the (cell_x, cell_y) tile."""
    w = h = max(1, int(CELL * scale))
    scaled = pygame.transform.smoothscale(img, (w, h))
    px = cell_x * CELL + (CELL - w) // 2 + MARGIN // 2
    py = cell_y * CELL + (CELL - h) // 2 + MARGIN // 2
    screen.blit(scaled, (px, py))

def draw_cell(screen, x, y, color):
    r = pygame.Rect(x * CELL + MARGIN , y * CELL + MARGIN, CELL - MARGIN, CELL - MARGIN)
    pygame.draw.rect(screen, color, r)

def draw_board(screen, board, imgs, percentage=1.0):
    BG = (68, 90, 144)
    EMPTY_ODD = (45, 60, 96)
    EMPTY_EVEN = (57, 69, 107)

    AMP = 0.10
    scale = 0.7 + AMP * math.sin(percentage * 2 * math.pi)

    screen.fill(BG)
    for y in range(GRID):
        for x in range(GRID):
            if (x + y) % 2 == 0:
                draw_cell(screen, x, y, EMPTY_EVEN)
            else:
                draw_cell(screen, x, y, EMPTY_ODD)
    for (gx, gy) in board["greens"]:
        blit_scaled_center(screen, imgs["green"], gx, gy, scale)
    if board["red"] is not None:
        rx, ry = board["red"]
        blit_scaled_center(screen, imgs["red"], rx, ry, scale)

    snake: List[Tuple[int, int]] = board.get("snake", [])
    if not snake: return

    for i in range(len(snake)):
        x, y = snake[i]
        draw_cell(screen, x, y, SNAKE_COLOR)

    head_x = snake[0][0] * CELL
    head_y = snake[0][1] * CELL
    match board.get("head_dir", "UP"):
        case "UP":
            pygame.draw.rect(screen, (0,0,0), (head_x + CELL//4 + 1, head_y + CELL//8, CELL//8, CELL//4))
            pygame.draw.rect(screen, (0,0,0), (head_x + 5*CELL//8 + 1, head_y + CELL//8, CELL//8, CELL//4))
        case "DOWN":
            pygame.draw.rect(screen, (0,0,0), (head_x + CELL//4 + 1, head_y + 5*CELL//8, CELL//8, CELL//4))
            pygame.draw.rect(screen, (0,0,0), (head_x + 5*CELL//8 + 1, head_y + 5*CELL//8, CELL//8, CELL//4))
        case "LEFT":
            pygame.draw.rect(screen, (0,0,0), (head_x + CELL//8, head_y + CELL//4 + 1, CELL//4, CELL//8))
            pygame.draw.rect(screen, (0,0,0), (head_x + CELL//8, head_y + 5*CELL//8 + 1, CELL//4, CELL//8))
        case "RIGHT":
            pygame.draw.rect(screen, (0,0,0), (head_x + 5*CELL//8, head_y + CELL//4 + 1, CELL//4, CELL//8))
            pygame.draw.rect(screen, (0,0,0), (head_x + 5*CELL//8, head_y + 5*CELL//8 + 1, CELL//4, CELL//8))
        case _:
            pass

def main():
    pygame.init()
    screen = pygame.display.set_mode((W, H))
    pygame.display.set_caption("Snake Viewer")
    clock = pygame.time.Clock()

    paused = False
    step_mode = True       # project requires a step-by-step mode
    base_fps = 20
    speed_mult = 1.0
    PULSE_PERIOD = 1.2

    images = load_images(CELL)

    running = True
    while running:
        # ---- input ----
        for e in pygame.event.get():
            if e.type == pygame.QUIT: running = False
            elif e.type == pygame.KEYDOWN:
                print(e.key)
                print("Paused:", pygame.K_SPACE, " Step:", pygame.K_s, " Next:", pygame.K_n)
                if e.key == pygame.K_SPACE: paused = not paused
                elif e.key == pygame.K_n:    pass  # single step tick (ask agent to advance 1 step)
                elif e.key == pygame.K_s:    step_mode = not step_mode
                elif e.key == pygame.K_LEFTBRACKET:  speed_mult = max(0.25, speed_mult/1.5)
                elif e.key == pygame.K_RIGHTBRACKET: speed_mult = min(8.0, speed_mult*1.5)

        # ---- advance game (agent tick) ----
        if not paused and not step_mode:
            pass  # tell C++ agent to tick here

        t = pygame.time.get_ticks() / 1000.0
        percentage = (t % PULSE_PERIOD) / PULSE_PERIOD

        # ---- render ----
        state = get_board()  # or cache last reply from tick
        draw_board(screen, state, images, percentage)
        pygame.display.flip()

        clock.tick(int(base_fps * speed_mult))

    pygame.quit()

if __name__ == "__main__":
    main()
