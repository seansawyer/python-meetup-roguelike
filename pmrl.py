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

def check_move(
        map_coords: Coordinates,
        mobs_coords: List[Coordinates],
        move_coords: Coordinates
):
    if move_coords in mobs_coords:
        return False
    if map_coords.x < move_coords.x < map_coords.x + map_width - 1:
        if map_coords.y < move_coords.y < map_coords.y + map_height - 1:
            return True
    return False

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
    libtcod.console_flush()

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
    player_coords = Coordinates(1, 1)
    libtcod.console_set_custom_font('arial10x10.png', libtcod.FONT_TYPE_GRAYSCALE | libtcod.FONT_LAYOUT_TCOD)
    libtcod.console_init_root(screen_width, screen_height, 'pmrl', False)
    # set up input devices
    key = libtcod.Key()
    mouse = libtcod.Mouse()
    running = True
    endgame = False
    while running and not libtcod.console_is_window_closed():
        libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS, key, mouse)
        libtcod.console_set_default_foreground(0, libtcod.white)
        # endgame sequence
        if endgame:
            draw_map(map_coords, exit_coords, player_coords, mobs_coords)
            msg_y = map_coords.y + map_height + 1
            libtcod.console_print(0, 0, msg_y, 'You win!')
            libtcod.console_flush()
            running = False
            time.sleep(5)
            continue
        # main game loop
        draw_map(map_coords, exit_coords, player_coords, mobs_coords)
        # input handling
        command = keypress_to_command(key)
        running = not command.get('quit', False)
        move = command.get('move')
        if move:
            dx, dy = move
            new_player_coords = Coordinates(
                player_coords.x + dx,
                player_coords.y + dy
            )
            if check_move(map_coords, mobs_coords, new_player_coords):
                player_coords = new_player_coords
        endgame = player_coords == exit_coords


if __name__ == '__main__':
    main()
