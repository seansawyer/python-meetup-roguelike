import time

import tcod as libtcod


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
    player_x = int(screen_width / 2)
    player_y = int(screen_height / 2)
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
        libtcod.console_put_char(0, player_x, player_y, '@', libtcod.BKGND_NONE)
        libtcod.console_flush()
        # input handling
        command = keypress_to_command(key)
        running = not command.get('quit', False)
        endgame = command.get('win', False)
        move = command.get('move')
        if move:
            dx, dy = move
            player_x += dx
            player_y += dy





if __name__ == '__main__':
    main()
