import time

import tcod as libtcod


def main():
    screen_width = 80
    screen_height = 50
    libtcod.console_set_custom_font('arial10x10.png', libtcod.FONT_TYPE_GRAYSCALE | libtcod.FONT_LAYOUT_TCOD)
    libtcod.console_init_root(screen_width, screen_height, 'pmrl', False)
    running = True
    endgame = False
    while running and not libtcod.console_is_window_closed():
        libtcod.console_set_default_foreground(0, libtcod.white)
        # endgame sequence
        if endgame:
            libtcod.console_print(0, 1, 1, 'You win!')
            libtcod.console_flush()
            running = False
            time.sleep(5)
            continue
        # main game loop
        libtcod.console_put_char(0, 1, 1, '@', libtcod.BKGND_NONE)
        libtcod.console_flush()
        # input handling
        key = libtcod.console_check_for_keypress()
        if key.vk == libtcod.KEY_ESCAPE:
            running = False
        elif key.vk == libtcod.KEY_CHAR:
            key_char = chr(key.c)
            if key_char == 'w':
                endgame = True
            elif key_char == 'q':
                running = False


if __name__ == '__main__':
    main()
