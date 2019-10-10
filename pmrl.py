import random
import time
from typing import List, NamedTuple

import tcod as libtcod


class Coordinates(NamedTuple):
    x: int
    y: int

screen_width = 80
screen_height = 50
map_width = screen_width
map_height = screen_height - 2

def generate_map():
    # start with all walls
    map_tiles = [['#'] * map_width for y in range(map_height)]
    # choose a random starting point
    x = random.randint(1, map_width - 2)
    y = random.randint(1, map_height - 2)
    # walk in a random direction
    possible_moves = [
        (0, -1),  # up
        (0, 1),  # down
        (-1, 0),  # left
        (1, 0),  # right
    ]
    map_tiles[y][x] = '.'
    for i in range(10000):
        choice = random.randint(0, len(possible_moves) - 1)
        dx, dy = possible_moves[choice]
        if 0 < x + dx < map_width - 2 and 0 < y + dy < map_height - 2:
            x = x + dx
            y = y + dy
        map_tiles[y][x] = '.'
    return map_tiles


def is_mob(coords: Coordinates, mobs_coords: List[Coordinates]):
    return coords in mobs_coords

def is_wall(coords: Coordinates, map_tiles: List[List[str]]):
    # Is it even in the map?
    if not 0 <= coords.x < map_width:
        return True
    if not 0 <= coords.y < map_height:
        return True
    # Is it a wall tile?
    tile = map_tiles[coords.y][coords.x]
    return tile == '#'

def draw_status(
    status_y: Coordinates,
    player_hp: int
):
    msg = f'HP: {player_hp:2}'
    libtcod.console_set_default_foreground(0, libtcod.blue)
    libtcod.console_print(0, 0, status_y, msg)
    libtcod.console_set_default_foreground(0, libtcod.white)

def draw_map(
    map_tiles: List[List[str]],
    exit_coords: Coordinates,
    player_coords: Coordinates,
    mobs_coords: List[Coordinates]
):
    y = 0
    for row in map_tiles:
        x = 0
        for tile in row:
            color = libtcod.white
            if x == player_coords.x and y == player_coords.y:
                tile = '@'
                color = libtcod.yellow
            elif Coordinates(x, y) in mobs_coords:
                tile = 'o'
                color = libtcod.red
            elif x == exit_coords.x and y == exit_coords.y:
                tile = '<'
                color = libtcod.green
            libtcod.console_set_default_foreground(0, color)
            libtcod.console_put_char(0, x, y, tile, libtcod.BKGND_NONE)
            libtcod.console_set_default_foreground(0, libtcod.white)
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

def choose_random_open_tile(map_tiles: List[List[str]], occupied_coords: List[Coordinates]):
    coords = None
    tile = '#'
    while tile != '.' and coords not in occupied_coords:
        x = random.randint(1, map_width - 2)
        y = random.randint(1, map_height - 2)
        tile = map_tiles[y][x]
        coords = Coordinates(x, y)
    occupied_coords.append(coords)
    return coords

def main():
    map_tiles = generate_map()
    # pick a random tile to place the exit
    occupied_coords = []
    exit_coords = choose_random_open_tile(map_tiles, occupied_coords)
    mobs_coords = [
        choose_random_open_tile(map_tiles, occupied_coords),
        choose_random_open_tile(map_tiles, occupied_coords),
        choose_random_open_tile(map_tiles, occupied_coords),
    ]
    mobs_hp = [
        5,
        4,
        3,
    ]
    # pick a random tile to place the player
    tile = '#'
    player_coords = choose_random_open_tile(map_tiles, occupied_coords)
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
        draw_map(map_tiles, exit_coords, player_coords, mobs_coords)
        draw_status(map_height, player_hp)
        libtcod.console_flush()
        # endgame sequence
        if dying or winning:
            msg_y = map_height + 1
            msg = 'You win!' if winning else 'You die.'
            color = libtcod.green if winning else libtcod.red
            libtcod.console_set_default_foreground(0, color)
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
            elif not is_wall(new_mob_coords, map_tiles):
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
                if not is_wall(new_player_coords, map_tiles):
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
