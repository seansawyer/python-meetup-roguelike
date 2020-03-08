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
    player_hp: int
    # world state
    map_tiles: List[List[str]]
    occupied_coords: Set[Tuple[int, int]]
    mobs: Dict[Tuple[int, int], Mob]
    fov_map: tcod.map.Map
    exit_x: int
    exit_y: int
    # meta state
    map_height: int
    map_width: int
    won: Optional[bool] = None  # True if won, False if lost, None if in progress


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
        result_msg = 'You win!' if game.won else 'You lose.'
        game.draw_console.clear()
        game.draw_console.print(1, 1, result_msg)
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
    # Draw visible walls and floors.
    for y, row in enumerate(game.map_tiles):
        for x, tile in enumerate(row):
            if game.fov_map.fov[y][x]:
                game.draw_console.draw_rect(x, y, 1, 1, ord(tile), fg=tcod.white)
    # Draw the exit if it is visible.
    if game.fov_map.fov[game.exit_y][game.exit_x]:
        game.draw_console.draw_rect(
            game.exit_x,
            game.exit_y,
            1,
            1,
            ord('<'),
            fg=tcod.green
        )
    # Draw the mobs after the exit, so they can hide it by standing on it. ;)
    for mob_x, mob_y in game.mobs.keys():
        if game.fov_map.fov[mob_y][mob_x]:
            game.draw_console.draw_rect(mob_x, mob_y, 1, 1, ord('O'), fg=tcod.red)
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

    def on_reenter_state(self):
        self.game.fov_map.compute_fov(self.game.player_x, self.game.player_y, 10)
        super().on_reenter_state()

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
            self.game.won = True  # win
            self.next_state = State.ENDGAME
        elif event.scancode == tcod.event.SCANCODE_H:
            self.maybe_move(-1, 0)  # left
        elif event.scancode == tcod.event.SCANCODE_J:
            self.maybe_move(0, 1)  # down
        elif event.scancode == tcod.event.SCANCODE_K:
            self.maybe_move(0, -1)  # up
        elif event.scancode == tcod.event.SCANCODE_L:
            self.maybe_move(1, 0)  # right

    def handle_attack(self, coords: Tuple[int, int], mob: Mob):
        # We let the player strike first, then check if the mob is dead prior
        # to counterattack. This gives the player a slight advantage.
        mob.hp -= 1
        if mob.hp <= 0:
            self.game.mobs.pop(coords)
            self.game.occupied_coords.remove(coords)
        else:
            self.game.player_hp -= 1
        # If the player's hit points reach zero, they lose of course!
        if self.game.player_hp <= 0:
            self.game.won = False
            self.next_state = State.ENDGAME

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
        # Move the player and record their new position
        self.game.occupied_coords.remove((self.game.player_x, self.game.player_y))
        self.game.player_x = limit_x_fn(limit_x, self.game.player_x + dx)
        self.game.player_y = limit_y_fn(limit_y, self.game.player_y + dy)
        self.game.occupied_coords.add((self.game.player_x, self.game.player_y))

    def maybe_move(self, dx, dy):
        # A move can imply an action, like attacking a mob, opening a
        # closed door, opening a chest, etc.
        coords, action_type, action_target = self.check_move(
            self.game.player_x,
            self.game.player_y,
            dx,
            dy,
            allow_attack=True
        )
        if not action_type:
            # This indicates that the action is blocked. Skip the turn.
            return
        if action_type == 'attack':
            self.handle_attack(coords, action_target)
        elif action_type == 'move':
            self.handle_move(dx, dy)
        # Now move the mobs. We freeze the keys view using a list so we can
        # change the dict as we go.
        for mob_coords in list(self.game.mobs.keys()):
            # Choose a random direction
            mob_move = random.choice([
                (0, 0),  # sit still
                (-1, 0),  # left
                (1, 0),  # right
                (0, -1),  # up
                (0, 1),  # down
            ])
            # If the mob chose to sit still, skip to the next mob.
            if not any(mob_move):
                continue
            # Mobs only retaliate for now (see handle_attack()) - other than
            # that they just wander aimlessly. So we ignore moves that would
            # result in attack.
            mob_x, mob_y = mob_coords
            mob_dx, mob_dy = mob_move
            mob_move_coords, mob_action_type, _ = self.check_move(
                mob_x,
                mob_y,
                mob_dx,
                mob_dy
            )
            if mob_action_type == 'move':
                mob = self.game.mobs.pop(mob_coords)
                self.game.occupied_coords.remove(mob_coords)
                self.game.mobs[mob_move_coords] = mob
                self.game.occupied_coords.add(mob_move_coords)
        # Send the player to endgame if they reached the exit.
        player_coords = self.game.player_x, self.game.player_y
        exit_coords = self.game.exit_x, self.game.exit_y
        if player_coords == exit_coords:
            self.game.won = True
            self.next_state = State.ENDGAME

    def check_move(
        self,
        from_x: int,
        from_y: int,
        dx: int,
        dy: int,
        allow_attack: bool = False
    ) -> Tuple[Tuple[int, int], Optional[str], Optional[Mob]]:
        x = from_x + dx
        y = from_y + dy
        coords = x, y
        # The exit is a special case - it's considered "occupied" but you can move there
        # And yes, mobs can stand on it and hide it :)
        exit_coords = self.game.exit_x, self.game.exit_y
        if coords == exit_coords:
            return coords, 'move', None
        if allow_attack:
            attack_target = self.game.mobs.get(coords)
            if attack_target:
                return coords, 'attack', attack_target
        if not is_wall(x, y, self.game.map_tiles) and coords not in self.game.occupied_coords:
            return coords, 'move', None
        return coords, None, None


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
    # start with all walls
    map_tiles = [['#'] * width for y in range(height)]
    # choose a random starting point
    x = random.randint(1, width - 2)
    y = random.randint(1, height - 2)
    # walk in a random direction
    possible_moves = [(0, -1), (0, 1), (-1, 0), (1, 0)]
    map_tiles[y][x] = '.'
    for i in range(10000):
        choice = random.randint(0, len(possible_moves) - 1)
        dx, dy = possible_moves[choice]
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
    # Coordinates outside the map are considered walls.
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
    mobs_coords = set()
    player_x, player_y = place_randomly(map_tiles, occupied_coords)
    exit_x, exit_y = place_randomly(map_tiles, occupied_coords)
    mobs = {}
    for i in range(25):
        mob_coords = place_randomly(map_tiles, occupied_coords)
        mobs[mob_coords] = Mob(5)
    fov_map = tcod.map.Map(CONSOLE_WIDTH, CONSOLE_HEIGHT)
    # Transparent tiles are everything except the walls.
    for y, row in enumerate(map_tiles):
        for x, tile in enumerate(row):
            if tile != '#':
                fov_map.transparent[y][x] = True
    fov_map.compute_fov(player_x, player_y, 10)
    return Game(
        root_console=root_console,
        draw_console=draw_console,
        player_x=player_x,
        player_y=player_y,
        player_hp=10,
        map_tiles=map_tiles,
        occupied_coords=occupied_coords,
        mobs=mobs,
        fov_map=fov_map,
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
