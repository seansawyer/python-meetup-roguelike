import time

import tcod as libtcod


def main():
    screen_width = 80
    screen_height = 50
    libtcod.console_set_custom_font('arial10x10.png', libtcod.FONT_TYPE_GRAYSCALE | libtcod.FONT_LAYOUT_TCOD)
    libtcod.console_init_root(screen_width, screen_height, 'pmrl', False)
    libtcod.console_set_default_foreground(0, libtcod.white)
    libtcod.console_print(0, 1, 1, 'You win!')
    libtcod.console_flush()
    time.sleep(5)
    return


if __name__ == '__main__':
    main()
