import pygame
from pathlib import Path
from render import load_images, draw_board, CELL, game_over_screen, home_menu, pause_menu, settings_screen
import agent

def game_loop(screen, grid_size=10, assets_path=Path("./assets")):
    running = True
    clock = pygame.time.Clock()

    paused = False
    step_mode = True # step-by-step mode by default
    base_fps = 60
    speed_mult = 1.0
    pulse_period = 1.2

    # how often the snake advances when running (seconds per cell)
    step_period = 0.12
    step_accum = 0.0

    engine = agent.Engine()
    engine.reset_board(grid_size)

    images = load_images(CELL, assets_path=assets_path)

    while running:
        dt = clock.tick(int(base_fps * speed_mult)) / 1000.0
        step_accum += dt

        # ---- input ----
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return False
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_SPACE and not paused:
                    bg_shot = screen.copy()
                    choice = pause_menu(screen, bg_surface=bg_shot)
                    if choice == "resume":
                        clock.tick(int(base_fps * speed_mult))
                        step_accum = 0.0
                        break
                    elif choice == "home":
                        return True
                    else:  # "quit"
                        return False

                elif e.key == pygame.K_ESCAPE:
                    running = False
                elif not paused:
                    if e.key == pygame.K_n and step_mode:
                        engine.step_forward()
                    elif e.key == pygame.K_m:
                        step_mode = not step_mode
                        step_accum = 0.0
                    elif e.key == pygame.K_MINUS:
                        speed_mult = max(0.25, speed_mult / 1.1)
                    elif e.key == pygame.K_EQUALS:
                        speed_mult = min(8.0, speed_mult * 1.1)
                    elif e.key == pygame.K_w:
                        engine.change_dir("UP")
                    elif e.key == pygame.K_s:
                        engine.change_dir("DOWN")
                    elif e.key == pygame.K_a:
                        engine.change_dir("LEFT")
                    elif e.key == pygame.K_d:
                        engine.change_dir("RIGHT")

        # ---- advance game (agent tick) ----
        if not paused and not step_mode:
            while step_accum >= (step_period / speed_mult):
                step_accum -= (step_period / speed_mult)
                engine.step_forward()

        state = engine.get_board()

        if state.get("game_over", False):
            bg_shot = screen.copy()
            choice = game_over_screen(
                screen,
                bg_surface=bg_shot,
                length=len(state["snake"])
            )
            if choice == "restart":
                engine.reset_board(grid_size)
                step_accum = 0.0
                step_mode = True
                continue  # back into the game loop
            elif choice == "quit":
                return True
            else:  # "quit_window"
                return False

        t = pygame.time.get_ticks() / 1000.0
        percentage = (t % pulse_period) / pulse_period

        # ---- render ----
        draw_board(screen, state, grid_size, images, percentage)
        pygame.display.flip()
    return True


def main():
    pygame.init()

    current_grid = 10
    current_model = "model1"
    w, h = current_grid * CELL, current_grid * CELL
    screen = pygame.display.set_mode((w, h))
    pygame.display.set_caption("Learn2Slither")

    file_path = Path(__file__).resolve().parent
    root_path = file_path / ".."
    models_path = root_path / "models"
    assets_path = root_path / "assets"

    running = True

    while running:
        choice = home_menu(screen)
        if choice == "play":
            running = game_loop(screen, grid_size=current_grid, assets_path=assets_path)
        elif choice == "ai":
            pass
            # start AI-controlled game
        elif choice == "settings":
            choice, grid_size, model = settings_screen(screen, grid_size=current_grid, model_name=current_model, models_dir=models_path)
            if choice == "save":
                current_grid = grid_size
                current_model = model
                w, h = max(480, current_grid * CELL), max(480, current_grid * CELL)
                screen = pygame.display.set_mode((w, h))
            elif choice == "back":
                pass  # nothing changed
            elif choice == "quit":
                running = False
        elif choice == "quit":
            running = False

    pygame.quit()

if __name__ == "__main__":
    main()
