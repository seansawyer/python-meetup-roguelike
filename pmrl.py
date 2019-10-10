import random
import time
from typing import List, NamedTuple

import tcod as libtcod


class Coordinates(NamedTuple):
    x: int
    y: int

map_s = [
    '##########',
    '#........#',
    '#........#',
    '#........#',
    '#........#',
    '#........#',
    '#........#',
    '#........#',
    '#........#',
    '##########',
]
map = [list(r) for r in map_s]
map_width = len(map[0])
map_height = len(map)

def is_mob(coords: Coordinates, mobs_coords: List[Coordinates]):
    return coords in mobs_coords

def is_wall(coords: Coordinates, map_coords: Coordinates):
    # Is it even in the map?
    if not map_coords.x <= coords.x < map_coords.x + map_width:
        return True
    if not map_coords.y <= coords.y < map_coords.y + map_height:
        return True
    # Is it a wall tile?
    tile = map[coords.y][coords.x]
    return tile == '#'

def draw_status(
    map_coords: Coordinates,
    player_hp: int
):
    msg = f'HP: {player_hp:2}'
    libtcod.console_print(0, 0, map_coords.y + map_height, msg)

def draw_map(
    map_coords: Coordinates,
    exit_coords: Coordinates,
    player_coords: Coordinates,
    mobs_coords: List[Coordinates]
):
    y = map_coords.y
    for row in map:
        x = map_coords.x
        for tile in row:
            if x == player_coords.x and y == player_coords.y:
                tile = '@'
            elif Coordinates(x, y) in mobs_coords:
                tile = 'o'
            elif x == exit_coords.x and y == exit_coords.y:
                tile = '<'
            libtcod.console_put_char(0, x, y, tile, libtcod.BKGND_NONE)
            x += 1
        y += 1

def keypress_to_command(key: libtcod.Key):
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

def main():
    screen_width = map_width
    screen_height = map_height + 2
    map_coords = Coordinates(0, 0)
    exit_coords = Coordinates(8, 8)
    mobs_coords = [
        Coordinates(3, 4),
        Coordinates(6, 5),
        Coordinates(2, 7),
    ]
    mobs_hp = [
        5,
        4,
        3,
    ]
    player_coords = Coordinates(1, 1)
    player_hp = 10
    libtcod.console_set_custom_font('arial10x10.png', libtcod.FONT_TYPE_GRAYSCALE | libtcod.FONT_LAYOUT_TCOD)
    libtcod.console_init_root(screen_width, screen_height, 'pmrl', False)
    # set up input devices
    key = libtcod.Key()
    mouse = libtcod.Mouse()
    running = True
    dying = False
    winning = False
    turn_counter = 0
    while running and not libtcod.console_is_window_closed():
        turn_counter += 1
        libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS, key, mouse)
        libtcod.console_set_default_foreground(0, libtcod.white)
        # update the screen
        draw_map(map_coords, exit_coords, player_coords, mobs_coords)
        draw_status(map_coords, player_hp)
        libtcod.console_flush()
        # endgame sequence
        if dying or winning:
            msg_y = map_coords.y + map_height + 1
            msg = 'You win!' if winning else 'You die.'
            libtcod.console_print(0, 0, msg_y, msg)
            libtcod.console_flush()
            running = False
            time.sleep(5)
            continue
        # input handling
        command = keypress_to_command(key)
        if not command:
            continue
        # move mobs first
        dead_mobs = set()
        for mob_i, mob_coords in enumerate(mobs_coords):
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
            if new_mob_coords == player_coords:
                player_hp -= 1
                mobs_hp[mob_i] -= 1
                if mobs_hp[mob_i] == 0:
                    dead_mobs.add(mob_i)
            elif not is_wall(new_mob_coords, map_coords):
                # check if it's another mob
                try:
                    is_other_mob = mob_i == mobs_coords.index(new_mob_coords)
                except ValueError:
                    is_other_mob = False
                if not is_other_mob:
                    mobs_coords[mob_i] = new_mob_coords
        running = not command.get('quit', False)
        move = command.get('move')
        if move:
            dx, dy = move
            new_player_coords = Coordinates(
                player_coords.x + dx,
                player_coords.y + dy
            )
            try:
                mob_i = mobs_coords.index(new_player_coords)
            except ValueError:
                if not is_wall(new_player_coords, map_coords):
                    player_coords = new_player_coords
            else:
                player_hp -= 1
                mobs_hp[mob_i] -= 1
                if mobs_hp[mob_i] == 0:
                    dead_mobs.add(mob_i)
        # new mobs are all that are not dead
        # find the indices of the dead ones
        mobs_coords = [coords for _, coords in filter(lambda e: e[0] not in dead_mobs, enumerate(mobs_coords))]
        mobs_hp = [hp for _, hp in filter(lambda e: e[0] not in dead_mobs, enumerate(mobs_hp))]
        dying = player_hp == 0
        winning = player_coords == exit_coords

if __name__ == '__main__':
    main()
