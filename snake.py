import curses
from curses import textpad
import random


class Grid:
    def __init__(self, r, c, even, treat, snake, empty):
        self.r = r
        self.c = c
        self.even = even
        self.treat = treat
        self.snake = snake
        self.empty = empty

    # Choosing type of printed field
    def hexagon(self):
        if self.even:
            hex = [[self.r, self.c], [self.r, self.c+1], [self.r, self.c+2], [self.r, self.c+3], [self.r, self.c+4],
                [self.r+1, self.c], [self.r+1, self.c+1], [self.r+1, self.c+2], [self.r+1, self.c+3], [self.r+1, self.c+4],
                [self.r+2, self.c], [self.r+2, self.c+1], [self.r+2, self.c+2], [self.r+2, self.c+3], [self.r+2, self.c+4]]
        else:
            hex = [[self.r, self.c+2], [self.r, self.c+3], [self.r, self.c+4], [self.r, self.c + 5], [self.r, self.c+6],
                   [self.r+1, self.c+2], [self.r+1, self.c+3], [self.r+1, self.c+4], [self.r+1, self.c+5], [self.r+1, self.c+6],
                   [self.r+2, self.c+2], [self.r+2, self.c+3], [self.r+2, self.c+4], [self.r+2, self.c+5], [self.r+2, self.c+6]]
        return hex

    # Displaying treat
    def print_treat(self, stdscr):
        tx = self.r + 1
        if self.even:
            ty = self.c + 2
        else:
            ty = self.c + 4

        curses.init_pair(1, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        stdscr.addstr(tx, ty, '$', curses.color_pair(1))
        self.treat = True
        self.snake = False


class Snake:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    # Displaying snake
    def add_snake(self, stdscr):
        curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
        stdscr.addstr(self.y, self.x, '#', curses.color_pair(2))

    def delete_tail(self, stdscr):
        stdscr.addstr(self.y, self.x, ' ')


# Finding empty field to add treat
def place_for_treat(grid, stdscr):
    located = False
    idx = 0
    while not located:
        idx = random.randint(0, len(grid) - 1)
        located = grid[idx].empty

    grid[idx].print_treat(stdscr)


# Printing hexagonal grid
def print_grid(stdscr, field):
    elements = [' ', '/', ' ', '\\', ' ',
                '|', ' ', ' ', ' ', '|',
                ' ', '\\', ' ', '/', ' ']

    hexagon = field.hexagon()
    for i, [y, x] in enumerate(hexagon):
        stdscr.addstr(y, x, elements[i])


def init_game(stdscr, rows, columns, r):
    grid = []

    # Creating grid
    for row in range(rows):
        c = 4
        if row % 2 == 0:
            for column in range(columns):
                grid.append(Grid(r, c, True, False, False, True))
                c += 4
        else:
            for column in range(columns):
                grid.append(Grid(r, c, False, False, False, True))
                c += 4
        r += 2

    # Printing grid
    for field in grid:
        print_grid(stdscr, field)

    # Finding field in the middle of grid
    middle = (len(grid) - columns) // 2

    # Adding first element of snake
    if grid[middle].even:
        head = Snake(grid[middle].c + 2, grid[middle].r + 1)
        head.add_snake(stdscr)
    else:
        head = Snake(grid[middle].c + 4, grid[middle].r + 1)
        head.add_snake(stdscr)
    grid[middle].snake = True
    grid[middle].empty = False

    # Addding treat
    place_for_treat(grid, stdscr)
    return head, middle, grid


def game(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(1)
    stdscr.timeout(800)

    rows, columns = 10, 10
    r, c = 4, 4
    height = rows*3 - r - 1
    width = columns*5 - c + 1
    box = [[r - 1, c - 1], [height, width]]
    textpad.rectangle(stdscr, box[0][0], box[0][1], box[1][0], box[1][1])

    head, idx, grid = init_game(stdscr, rows, columns, r)

    snake = [head]
    grid_idx = [idx]

    # Displaying score
    score = 0
    score_text = "SCORE: {}".format(score)
    stdscr.addstr(1, width // 2 - len(score_text) // 2, score_text)

    play = True
    direction = ord('d')
    while play:
        key = stdscr.getch()

        key_a = ord('a')
        key_d = ord('d')
        key_q = ord('q')
        key_e = ord('e')
        key_z = ord('z')
        key_x = ord('x')

        if key in [key_a, key_d, key_q, key_e, key_z, key_x]:
            direction = key

        head = snake[0]
        idx = grid_idx[0]  # index of field where snake's head is
        if direction == key_d:
            new_head = Snake(head.x + 4, head.y)
            grid_idx.insert(0, idx + 1)
        elif direction == key_a:
            new_head = Snake(head.x - 4, head.y)
            grid_idx.insert(0, idx - 1)
        elif direction == key_q:
            new_head = Snake(head.x - 2, head.y - 2)
            if grid[grid_idx[0]].even:
                grid_idx.insert(0, idx - 11)
            else:
                grid_idx.insert(0, idx - 10)
        elif direction == key_e:
            new_head = Snake(head.x + 2, head.y - 2)
            if grid[grid_idx[0]].even:
                grid_idx.insert(0, idx - 10)
            else:
                grid_idx.insert(0, idx - 9)
        elif direction == key_z:
            new_head = Snake(head.x - 2, head.y + 2)
            if grid[grid_idx[0]].even:
                grid_idx.insert(0, idx + 9)
            else:
                grid_idx.insert(0, idx + 10)
        elif direction == key_x:
            new_head = Snake(head.x + 2, head.y + 2)
            if grid[grid_idx[0]].even:
                grid_idx.insert(0, idx + 10)
            else:
                grid_idx.insert(0, idx + 11)

        # Game over if snake bites itself or hit the wall
        if grid[grid_idx[0]].snake or snake[0].x < r + 2 or snake[0].x > r + 40 or snake[0].y < c + 1 or snake[0].y > c + 20:
            msg = "GAME OVER"
            stdscr.addstr(height // 2, width // 2 - len(msg) // 2, msg)
            stdscr.nodelay(0)
            stdscr.getch()
            play = False

        # If snake found treat
        if grid[grid_idx[0]].treat:
            grid[grid_idx[0]].treat = False
            grid[grid_idx[0]].snake = True
            grid[grid_idx[-1]].snake = True
            snake.insert(0, new_head)
            snake[0].add_snake(stdscr)
            place_for_treat(grid, stdscr)
            score += 1
            score_text = "SCORE: {}".format(score)
            stdscr.addstr(1, width // 2 - len(score_text) // 2, score_text)
        elif not grid[grid_idx[0]].treat:
            grid[grid_idx[0]].snake = True
            grid[grid_idx[-1]].snake = False
            snake.insert(0, new_head)
            snake[0].add_snake(stdscr)
            snake[-1].delete_tail(stdscr)
            snake.pop()
            grid_idx.pop()
    stdscr.refresh()


curses.wrapper(game)
