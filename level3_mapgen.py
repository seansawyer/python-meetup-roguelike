from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Dict, List, Optional, Set, Tuple
import random

import numpy as np
import tcod
import tcod.event

CONSOLE_WIDTH = 80
CONSOLE_HEIGHT = 50


@dataclass
class Mob:
    hp: int


@dataclass
class Game:
    # drawing context
    root_console: tcod.console.Console
    draw_console: tcod.console.Console
    # player state
    player_x: int
    player_y: int
    # world state
    map_tiles: List[List[str]]
    occupied_coords: Set[Tuple[int, int]]
    exit_x: int
    exit_y: int
    # other state
    map_height: int
    map_width: int


class State(Enum):
    MAP = 'map'
    ENDGAME = 'endgame'


class StateHandler(tcod.event.EventDispatch):

    def __init__(self, next_state: Optional[State], game: Game) -> None:
        """Constructor"""
        self.next_state = next_state
        self.game = game

    def handle(self) -> Tuple[Optional[State], Game]:
        """
        Dispatch pending input events to handler methods, and then return the
        next state and a game instance to use in that state.
        """
        for event in tcod.event.wait():
            self.dispatch(event)
        return self.next_state, self.game

    def draw(self) -> None:
        """Override this to draw the screen for this state."""
        pass

    def on_enter_state(self) -> None:
        self.draw()
        blit_and_flush(self.game.draw_console, self.game.root_console)

    def on_reenter_state(self) -> None:
        self.draw()
        blit_and_flush(self.game.draw_console, self.game.root_console)


def blit_and_flush(
        from_console: tcod.console.Console,
        to_console: tcod.console.Console
) -> None:
    from_console.blit(
        to_console,
        width=from_console.width,
        height=from_console.height
    )
    tcod.console_flush()


def draw_endgame(game: Game):
        game.draw_console.clear()
        game.draw_console.print(1, 1, 'You win!')
        game.draw_console.print(1, 3, 'Press R to play again')
        game.draw_console.print(1, 5, 'Press Q to quit')
        game.draw_console.blit(
            game.root_console,
            width=game.draw_console.width,
            height=game.draw_console.height
        )
        tcod.console_flush()


def draw_map(game: Game) -> None:
    game.draw_console.clear()
    # Draw walls and floors.
    for y, row in enumerate(game.map_tiles):
        for x, tile in enumerate(row):
            game.draw_console.draw_rect(x, y, 1, 1, ord(tile), fg=tcod.white)
    # Draw the exit.
    game.draw_console.draw_rect(
        game.exit_x,
        game.exit_y,
        1,
        1,
        ord('<'),
        fg=tcod.green
    )
    # Draw the player.
    game.draw_console.draw_rect(
        game.player_x,
        game.player_y,
        1,
        1,
        ord('@'),
        fg=tcod.yellow
    )

class MapStateHandler(StateHandler):

    def draw(self):
        draw_map(self.game)

    def ev_quit(self, event):
        self.next_state = None

    def ev_keydown(self, event):
        if event.scancode == tcod.event.SCANCODE_F:
            fullscreen = not tcod.console_is_fullscreen()
            tcod.console_set_fullscreen(fullscreen)
        elif event.scancode == tcod.event.SCANCODE_Q:
            self.next_state = None  # quit
        elif event.scancode == tcod.event.SCANCODE_W:
            self.next_state = State.ENDGAME
        elif event.scancode == tcod.event.SCANCODE_H:
            self.maybe_move(-1, 0)  # left
        elif event.scancode == tcod.event.SCANCODE_J:
            self.maybe_move(0, 1)  # down
        elif event.scancode == tcod.event.SCANCODE_K:
            self.maybe_move(0, -1)  # up
        elif event.scancode == tcod.event.SCANCODE_L:
            self.maybe_move(1, 0)  # right

    def handle_move(self, dx, dy):
        # When moving left, don't let x go below zero
        # When moving right, don't let x reach the console width
        if dx < 0:
            limit_x_fn = max
            limit_x = 0
        else:
            limit_x_fn = min
            limit_x = self.game.map_width - 1
        # When moving up, don't let y go below zero
        # When moving down, don't let x reach the console height
        if dy < 0:
            limit_y_fn = max
            limit_y = 0
        else:
            limit_y_fn = min
            limit_y = self.game.map_height - 1
        # Move the player.
        self.game.player_x = limit_x_fn(limit_x, self.game.player_x + dx)
        self.game.player_y = limit_y_fn(limit_y, self.game.player_y + dy)

    def maybe_move(self, dx, dy):
        coords, action_type = self.check_move(
            self.game.player_x,
            self.game.player_y,
            dx,
            dy
        )
        if not action_type:
            # This indicates that the action is blocked, so skip the turn.
            return
        if action_type == 'move':
            self.handle_move(dx, dy)
        # Send the player to endgame if they reached the exit.
        player_coords = self.game.player_x, self.game.player_y
        exit_coords = self.game.exit_x, self.game.exit_y
        if player_coords == exit_coords:
            self.next_state = State.ENDGAME

    def check_move(
        self,
        from_x: int,
        from_y: int,
        dx: int,
        dy: int
    ) -> Tuple[Tuple[int, int], Optional[str]]:
        x = from_x + dx
        y = from_y + dy
        coords = x, y
        if not is_wall(x, y, self.game.map_tiles):
            return coords, 'move'
        return coords, None


class EndgameStateHandler(StateHandler):

    def draw(self):
        draw_endgame(self.game)

    def ev_quit(self, event):
        self.next_state = None

    def ev_keydown(self, event):
        print(event)
        if event.scancode == tcod.event.SCANCODE_F:
            fullscreen = not tcod.console_is_fullscreen()
            tcod.console_set_fullscreen(fullscreen)
        elif event.scancode == tcod.event.SCANCODE_Q:
            # quit
            self.next_state = None
        elif event.scancode == tcod.event.SCANCODE_R:
            # restart
            self.next_state = State.MAP
            self.game = build_game(self.game.root_console, self.game.draw_console)


def run_fsm(
        state_handlers: Dict[State, StateHandler],
        state: State,
        game: Game
) -> None:
    last_state = None
    while state is not None:
        handler_class = state_handlers[state]
        handler = handler_class(state, game)
        if state == last_state:
            handler.on_reenter_state()
        else:
            handler.on_enter_state()
        last_state = state
        state, game = handler.handle()


def build_map(width: int, height: int) -> List[List[str]]:
    """Generate a map by carving out a random walk."""
    # Start with all walls.
    map_tiles = [['#'] * width for y in range(height)]
    # Choose a random starting point.
    x = random.randint(1, width - 2)
    y = random.randint(1, height - 2)
    # Walk in a random direction.
    possible_moves = [(0, -1), (0, 1), (-1, 0), (1, 0)]
    map_tiles[y][x] = '.'
    for i in range(10000):
        dx, dy= random.choice(possible_moves)
        if 0 < x + dx < width - 1 and 0 < y + dy < height - 1:
            x = x + dx
            y = y + dy
        map_tiles[y][x] = '.'
    return map_tiles


def is_wall(
    x: int,
    y: int,
    map_tiles: List[List[str]]
) -> bool:
    height = len(map_tiles)
    width = len(map_tiles[0])
    # Is it even in the map?
    if not 0 <= x < width:
        return True
    if not 0 <= y < height:
        return True
    # Is it a wall tile?
    tile = map_tiles[y][x]
    return tile == '#'


def place_randomly(
    map_tiles: List[List[str]],
    occupied_coords: Set[Tuple[int, int]]
) -> Tuple[int, int]:
    height = len(map_tiles)
    width = len(map_tiles[0])
    coords = None, None
    tile = '#'
    while tile != '.' and coords not in occupied_coords:
        x = random.randint(1, width - 2)
        y = random.randint(1, height - 2)
        coords = x, y
        tile = map_tiles[y][x]
    occupied_coords.add(coords)
    return coords


def build_game(
        root_console: tcod.console.Console,
        draw_console: tcod.console.Console
) -> Game:
    map_tiles = build_map(CONSOLE_WIDTH, CONSOLE_HEIGHT)
    occupied_coords = set()
    exit_x, exit_y = place_randomly(map_tiles, occupied_coords)
    player_x, player_y = place_randomly(map_tiles, occupied_coords)
    return Game(
        root_console=root_console,
        draw_console=draw_console,
        player_x=player_x,
        player_y=player_y,
        map_tiles=map_tiles,
        occupied_coords=occupied_coords,
        exit_x=exit_x,
        exit_y=exit_y,
        map_width=CONSOLE_WIDTH,
        map_height=CONSOLE_HEIGHT
    )


def main():
    tcod.console_set_custom_font(
        'arial10x10.png',
        tcod.FONT_LAYOUT_TCOD | tcod.FONT_TYPE_GREYSCALE,
    )
    with tcod.console_init_root(
            CONSOLE_WIDTH,
            CONSOLE_HEIGHT,
            order='F',
            renderer=tcod.RENDERER_SDL2,
            title='FSM Game',
            vsync=True
    ) as root_console:
        draw_console = tcod.console.Console(CONSOLE_WIDTH, CONSOLE_HEIGHT, order='F')
        my_state_handlers = {
            State.MAP: MapStateHandler,
            State.ENDGAME: EndgameStateHandler,
        }
        game = build_game(root_console, draw_console)
        run_fsm(my_state_handlers, State.MAP, game)


if __name__ == '__main__':
    main()
