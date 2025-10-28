import random
import time

DIR = {
    "UP":    (0, -1),
    "DOWN":  (0, 1),
    "LEFT":  (-1, 0),
    "RIGHT": (1, 0),
}
OPPOSITE = {"UP":"DOWN", "DOWN":"UP", "LEFT":"RIGHT", "RIGHT":"LEFT"}

def init_board(grid_size=10):
    """Return initial game state."""
    random.seed(time.time())
    green1 = (random.randint(0, grid_size - 1), random.randint(0, grid_size - 1))
    green2 = (random.randint(0, grid_size - 1), random.randint(0, grid_size - 1))
    while green1 == green2:
        green2 = (random.randint(0, grid_size - 1), random.randint(0, grid_size - 1))
    red = (random.randint(0, grid_size - 1), random.randint(0, grid_size - 1))
    while red == green1 or red == green2:
        red = (random.randint(0, grid_size - 1), random.randint(0, grid_size - 1))

    snake = place_snake(green1, green2, red, grid_size)

    head_dir = OPPOSITE[get_neck_dir(snake)]

    while snake[0][0] + DIR[head_dir][0] < 0 or snake[0][0] + DIR[head_dir][0] >= grid_size or \
          snake[0][1] + DIR[head_dir][1] < 0 or snake[0][1] + DIR[head_dir][1] >= grid_size or \
          (snake[0][0] + DIR[head_dir][0], snake[0][1] + DIR[head_dir][1]) in snake:
        head_dir = random.choice(list(DIR.keys()))

    return {
        "snake": snake,
        "greens": [green1, green2],
        "red": red,
        "head_dir": head_dir,
        "game_over": False,
    }

def place_snake(green1, green2, red, grid_size=10):
    """Ensure snake does not start on an apple."""
    while True:
        snake = [(random.randint(0, grid_size - 1), random.randint(0, grid_size - 1))]

        for _i in range(1, 3):
            x, y = snake[-1]
            direction = random.choice(list(DIR.values()))
            nx, ny = (x + direction[0]), (y + direction[1])
            while nx < 0 or nx >= grid_size or ny < 0 or ny >= grid_size or (nx, ny) in snake:
                direction = random.choice(list(DIR.values()))
                nx, ny = (x + direction[0]), (y + direction[1])
            snake.append((nx, ny))

        if green1 not in snake and green2 not in snake and red not in snake:
            break
    return snake

def step_forward(state, grid_size=10):
    """Advance snake one cell in head_dir. No collisions/apples yet; just move."""
    snake = state["snake"]
    hx, hy = snake[0]
    dx, dy = DIR[state["head_dir"]]

    nx, ny = hx + dx, hy + dy

    if nx < 0 or nx >= grid_size or ny < 0 or ny >= grid_size or (nx, ny) in snake:
        state["game_over"] = True
        return state  # collision; game over

    #eat green mean growing
    if (nx, ny) in state["greens"]:
        state["greens"].remove((nx, ny))
        new_green = (random.randint(0, grid_size - 1), random.randint(0, grid_size - 1))
        while (new_green in state["greens"] or new_green in snake) and len(snake) != grid_size * grid_size:
            new_green = (random.randint(0, grid_size - 1), random.randint(0, grid_size - 1))
        state["greens"].append(new_green)
        new_snake = [(nx, ny)] + snake
    elif state["red"] == (nx, ny):
        state["red"] = (random.randint(0, grid_size - 1), random.randint(0, grid_size - 1))
        while (state["red"] in state["greens"] or state["red"] in snake) and len(snake) != grid_size * grid_size:
            state["red"] = (random.randint(0, grid_size - 1), random.randint(0, grid_size - 1))
        new_snake = [(nx, ny)] + snake[:-2]
        if len(snake) == 1:
            state["game_over"] = True
            return state
    else:
        new_snake = [(nx, ny)] + snake[:-1]
    state["snake"] = new_snake
    return state

def get_neck_dir(snake):
    """Return direction from head to neck."""
    if len(snake) < 2:
        return None
    hx, hy = snake[0]
    nx, ny = snake[1]
    dx = nx - hx
    dy = ny - hy
    for d, (ddx, ddy) in DIR.items():
        if (dx, dy) == (ddx, ddy):
            return d
    return None

def change_dir(state, new_dir):
    """Set new direction if it's not the opposite of current."""
    if new_dir != get_neck_dir(state["snake"]):
        state["head_dir"] = new_dir