#!/usr/bin/env python

import random
import time
from typing import Any, Dict, NamedTuple, Set, Tuple

import tcod as libtcod


class Coordinates(NamedTuple):
    x: int
    y: int


class PMRL(object):
    # Defaults
    SCREEN_WIDTH = 80
    SCREEN_HEIGHT = 50
    MAP_WIDTH = SCREEN_WIDTH
    MAP_HEIGHT = SCREEN_HEIGHT - 2
    NUM_MOBS = 40
    PLAYER_HP = 10

    # Instance vars
    screen_width = None
    screen_height = None
    map_width = None
    map_height = None
    num_mobs = None
    player_hp = None

    # Input devices
    key = libtcod.Key()
    mouse = libtcod.Mouse()

    # List[List[str]]
    map_tiles = None
    # List[Coordinates]
    occupied_coords = None
    # Coordinates
    exit_coords = None
    # List[Coordinates]
    mobs_coords = None
    # List[int]
    mobs_hp = None
    # Coordinates
    player_coords = None
    # bool
    running = None
    # bool
    dying = None
    # bool
    winning = None
    # int
    turn_counter = None

    def __init__(self, screen_width=SCREEN_WIDTH, screen_height=SCREEN_HEIGHT,
                 map_width=MAP_WIDTH, map_height=MAP_HEIGHT,
                 num_mobs=NUM_MOBS, player_hp=PLAYER_HP) -> None:
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.map_width = map_width
        self.map_height = map_height
        self.num_mobs = num_mobs
        self.player_hp = player_hp
        self.setup_game()

    def setup_game(self) -> None:
        self.generate_map()
        self.occupied_coords = []
        # pick a random tile to place the exit
        self.exit_coords = self.choose_random_open_tile()
        self.mobs_coords = [
            self.choose_random_open_tile() for i in range(self.num_mobs)
        ]
        self.mobs_hp = [random.randint(1, 5) for i in range(self.num_mobs)]
        self.player_coords = self.choose_random_open_tile()
        libtcod.console_set_custom_font('arial10x10.png',
                                        libtcod.FONT_TYPE_GRAYSCALE | libtcod.FONT_LAYOUT_TCOD)
        self.running = True
        self.dying = False
        self.winning = False
        self.turn_counter = 0

    def generate_map(self) -> None:
        # start with all walls
        self.map_tiles = [['#'] * self.map_width for y in range(self.map_height)]
        # choose a random starting point
        x = random.randint(1, self.map_width - 2)
        y = random.randint(1, self.map_height - 2)
        # walk in a random direction
        possible_moves = [(0, -1), (0, 1), (-1, 0), (1, 0)]
        self.map_tiles[y][x] = '.'
        for i in range(10000):
            choice = random.randint(0, len(possible_moves) - 1)
            dx, dy = possible_moves[choice]
            if 0 < x + dx < self.map_width - 2 and 0 < y + dy < self.map_height - 2:
                x = x + dx
                y = y + dy
            self.map_tiles[y][x] = '.'

    def choose_random_open_tile(self) -> Coordinates:
        coords = None
        tile = '#'
        while tile != '.' and coords not in self.occupied_coords:
            x = random.randint(1, self.map_width - 2)
            y = random.randint(1, self.map_height - 2)
            tile = self.map_tiles[y][x]
            coords = Coordinates(x, y)
        self.occupied_coords.append(coords)
        return coords

    def run(self) -> None:
        with libtcod.console_init_root(w=self.screen_width,
                                       h=self.screen_height,
                                       title='pmrl',
                                       fullscreen=False,
                                       renderer=libtcod.RENDERER_SDL2,
                                       vsync=False) as root_console:
            # The libtcod window will be closed at the end of this with-block.
            self.run_with_console(root_console)

    def run_with_console(self, root_console: libtcod.console.Console) -> None:
        # TODO: Move away from deprecated libtcod.console_is_window_closed()
        while self.running and not libtcod.console_is_window_closed():
            self.turn_counter += 1
            # TODO: Use libtcod.event.get()
            # https://python-tcod.readthedocs.io/en/latest/tcod/event.html#tcod.event.get
            libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS,
                                        self.key,
                                        self.mouse)
            # update the screen
            self.draw_map(root_console)
            self.draw_status(root_console)
            libtcod.console_flush()
            # endgame sequence
            if self.dying or self.winning:
                msg_y = self.map_height + 1
                msg = 'You win!' if self.winning else 'You die.'
                color = libtcod.green if self.winning else libtcod.red
                root_console.print(x=0, y=msg_y, string=msg, fg=color)
                libtcod.console_flush()
                self.running = False
                time.sleep(5)
                continue
            # input handling
            command = self.keypress_to_command(self.key)
            if not command:
                continue
            # move mobs first
            dead_mobs = self.move_mobs()
            self.running = not command.get('quit', False)
            self.move_player(command.get('move'), dead_mobs)
            # new mobs are all that are not dead
            # find the indices of the dead ones
            self.mobs_coords = [coords for _, coords in filter(lambda e: e[0] not in dead_mobs, enumerate(self.mobs_coords))]
            self.mobs_hp = [hp for _, hp in filter(lambda e: e[0] not in dead_mobs, enumerate(self.mobs_hp))]
            self.dying = self.player_hp <= 0
            self.winning = self.player_coords == self.exit_coords

    def move_mobs(self) -> Set[int]:
        dead_mobs = set()
        for mob_i, mob_coords in enumerate(self.mobs_coords):
            # choose a random move
            possible_moves = [
                (0, 0),  # stay
                (0, -1),  # up
                (0, 1),  # down
                (-1, 0),  # left
                (1, 0),  # right
            ]
            choice = random.randint(0, len(possible_moves) - 1)
            mob_move = possible_moves[choice]
            mob_dx, mob_dy = mob_move
            new_mob_coords = Coordinates(
                mob_coords.x + mob_dx,
                mob_coords.y + mob_dy
            )
            if new_mob_coords == self.player_coords:
                self.player_hp -= 1
                self.mobs_hp[mob_i] -= 1
                if self.mobs_hp[mob_i] == 0:
                    dead_mobs.add(mob_i)
            elif not self.is_wall(new_mob_coords):
                # check if it's another mob
                try:
                    is_other_mob = mob_i == self.mobs_coords.index(new_mob_coords)
                except ValueError:
                    is_other_mob = False
                if not is_other_mob:
                    self.mobs_coords[mob_i] = new_mob_coords
        return dead_mobs

    def move_player(self, move: Tuple[int, int], dead_mobs: Set[int]) -> None:
        if not move:
            return
        dx, dy = move
        new_player_coords = Coordinates(
            self.player_coords.x + dx,
            self.player_coords.y + dy
        )
        try:
            mob_i = self.mobs_coords.index(new_player_coords)
        except ValueError:
            if not self.is_wall(new_player_coords):
                self.player_coords = new_player_coords
        else:
            self.player_hp -= 1
            self.mobs_hp[mob_i] -= 1
            if self.mobs_hp[mob_i] == 0:
                dead_mobs.add(mob_i)

    def is_wall(self, coords: Coordinates) -> bool:
        # Is it even in the map?
        if not 0 <= coords.x < self.map_width:
            return True
        if not 0 <= coords.y < self.map_height:
            return True
        # Is it a wall tile?
        tile = self.map_tiles[coords.y][coords.x]
        return tile == '#'

    def draw_status(self, root_console: libtcod.console.Console) -> None:
        msg = f'HP: {self.player_hp:2}'
        root_console.print(x=0, y=self.map_height, string=msg, fg=libtcod.blue)

    def draw_map(self, root_console: libtcod.console.Console) -> None:
        y = 0
        for row in self.map_tiles:
            x = 0
            for tile in row:
                color = libtcod.white
                if x == self.player_coords.x and y == self.player_coords.y:
                    tile = '@'
                    color = libtcod.yellow
                elif Coordinates(x, y) in self.mobs_coords:
                    tile = 'o'
                    color = libtcod.red
                elif x == self.exit_coords.x and y == self.exit_coords.y:
                    tile = '<'
                    color = libtcod.green
                root_console.draw_rect(x=x,
                                       y=y,
                                       width=1,
                                       height=1,
                                       ch=ord(tile),
                                       fg=color,
                                       bg_blend=libtcod.BKGND_NONE)
                x += 1
            y += 1

    def keypress_to_command(self, key: libtcod.Key) -> Dict[str, Any]:
        key_vk_command_map = {
            libtcod.KEY_ESCAPE: {'quit': True},
            libtcod.KEY_UP: {'move': (0, -1)},
            libtcod.KEY_DOWN: {'move': (0, 1)},
            libtcod.KEY_LEFT: {'move': (-1, 0)},
            libtcod.KEY_RIGHT: {'move': (1, 0)},
        }
        key_char_command_map = {
            'h': {'move': (-1, 0)},  # move left
            'j': {'move': (0, 1)},  # move down
            'k': {'move': (0, -1)},  # move up
            'l': {'move': (1, 0)},  # move right
            'q': {'quit': True},  # quit the game
        }
        if key.vk == libtcod.KEY_CHAR:
            return key_char_command_map.get(chr(key.c), {})
        return key_vk_command_map.get(key.vk, {})


if __name__ == '__main__':
    PMRL().run()
