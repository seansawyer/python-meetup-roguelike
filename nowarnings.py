import tcod
import tcod.event


def setup():
    tcod.console_set_custom_font(
        "arial10x10.png",
        tcod.FONT_LAYOUT_TCOD | tcod.FONT_TYPE_GREYSCALE,
    )


def main():
    setup()
    console_width = 80
    console_height = 50
    player_x = console_width // 2
    player_y = console_height // 2
    with tcod.console_init_root(
            console_width,
            console_height,
            order='F',
            renderer=tcod.RENDERER_SDL2,
            title='No Warning',
            vsync=True
    ) as root_console:
        console = tcod.console.Console(console_width, console_height, order='F')
        while True:
            console.put_char(player_x, player_y, ord('@'))
            console.blit(root_console, width=console_width, height=console_height)
            tcod.console_flush()
            console.put_char(player_x, player_y, ord(' '))
            for event in tcod.event.wait():
                if event.type == 'QUIT':
                    raise SystemExit()
                elif event.type == "KEYDOWN":
                    print(event)
                    if event.scancode == tcod.event.SCANCODE_F:
                        # toggle fullscreen
                        tcod.console_set_fullscreen(not tcod.console_is_fullscreen())
                    elif event.scancode == tcod.event.SCANCODE_H:
                        # left
                        player_x = max(0, player_x - 1)
                    elif event.scancode == tcod.event.SCANCODE_J:
                        # down
                        player_y = min(console_height - 1, player_y + 1)
                    elif event.scancode == tcod.event.SCANCODE_K:
                        # up
                        player_y = max(0, player_y - 1)
                    elif event.scancode == tcod.event.SCANCODE_L:
                        # right
                        player_x = min(console_width - 1, player_x + 1)
                    elif event.scancode == tcod.event.SCANCODE_Q:
                        raise SystemExit()


if __name__ == '__main__':
    main()
