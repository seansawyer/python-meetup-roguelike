import time
from typing import Tuple

import tcod as libtcod

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
        map_coords: Tuple[int, int],
        new_player_coords: Tuple[int, int]
):
    map_x, map_y = map_coords
    new_player_x, new_player_y = new_player_coords
    if map_x < new_player_x < map_x + map_width - 1:
        if map_y < new_player_y < map_y + map_height - 1:
            return True
    return False

def draw_map(
    map_coords: Tuple[int, int],
    player_coords: Tuple[int, int]
):
    map_x, map_y = map_coords
    player_x, player_y = player_coords
    y = map_y
    for row in map:
        x = map_x
        for tile in row:
            if x == player_x and y == player_y:
                libtcod.console_put_char(0, x, y, '@', libtcod.BKGND_NONE)
            #elif x == end_coords[0] and y == end_coords[1]:
            #    print('*', end='')
            else:
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
        'w': {'win': True},  # win the game
    }
    if key.vk == libtcod.KEY_CHAR:
        return key_char_command_map.get(chr(key.c), {})
    return key_vk_command_map.get(key.vk, {})

def main():
    screen_width = 80
    screen_height = 50
    map_x = 0
    map_y = 0
    player_coords = (
        int((map_x + map_width) / 2),
        int((map_y + map_height) / 2),
    )
    map_coords = (0, 0)
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
            libtcod.console_print(0, 1, 1, 'You win!')
            libtcod.console_flush()
            running = False
            time.sleep(5)
            continue
        # main game loop
        draw_map(map_coords, player_coords)
        # input handling
        command = keypress_to_command(key)
        running = not command.get('quit', False)
        endgame = command.get('win', False)
        move = command.get('move')
        if move:
            player_x, player_y = player_coords
            dx, dy = move
            new_player_x = player_x + dx
            new_player_y = player_y + dy
            new_player_coords = new_player_x, new_player_y
            if check_move(map_coords, new_player_coords):
                player_coords = new_player_coords





if __name__ == '__main__':
    main()
