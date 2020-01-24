import time
from dataclasses import dataclass

import tcod
import tcod.event


@dataclass
class GameState:
    # console settings
    width: int = 80
    height: int = 50
    # game progression flags
    endgame: bool = False
    running: bool = True
    # player state
    player_x: int = 40
    player_y: int = 25


class EndgameEventDispatch(tcod.event.EventDispatch):
    def __init__(self, state: GameState):
        self.state = state

    def ev_quit(self, event):
        raise SystemExit()

    def ev_keydown(self, event):
        if event.scancode == tcod.event.SCANCODE_F:
            fullscreen = not tcod.console_is_fullscreen()
            tcod.console_set_fullscreen(fullscreen)
        elif event.scancode == tcod.event.SCANCODE_Q:
            raise SystemExit()
        elif event.scancode == tcod.event.SCANCODE_R:
            self.state.endgame = False


class MainEventDispatch(tcod.event.EventDispatch):
    def __init__(self, state: GameState):
        self.state = state

    def ev_quit(self, event):
        raise SystemExit()

    def ev_keydown(self, event):
        if event.scancode == tcod.event.SCANCODE_F:
            fullscreen = not tcod.console_is_fullscreen()
            tcod.console_set_fullscreen(fullscreen)
        elif event.scancode == tcod.event.SCANCODE_Q:
            raise SystemExit()
        elif event.scancode == tcod.event.SCANCODE_W:
            self.state.endgame = True


def setup():
    tcod.console_set_custom_font(
        "arial10x10.png",
        tcod.FONT_LAYOUT_TCOD | tcod.FONT_TYPE_GREYSCALE,
    )


def draw_endgame(is_win, root_console, draw_console):
    verb = 'win' if is_win else 'lose'
    draw_console.print(1, 1, f'You {verb}!')
    draw_console.print(1, 3, 'Press R to play again')
    draw_console.print(1, 5, 'Press Q to quit')
    draw_console.blit(
        root_console,
        width=draw_console.width,
        height=draw_console.height
    )
    tcod.console_flush()


def handle_endgame(
        state: GameState,
        is_win: bool,
        root_console: tcod.console.Console,
        draw_console: tcod.console.Console
) -> None:
    """
    Show the endgame sequence, prompting the user to either quit or play again.
    Loop until they make a choice, raising `SystemExit` if they chose to quit.

    Args:
        is_win: `True` if the game was won, `False` if lost
        root_console: the root console, to which we will blit
        draw_console: the console to which we draw and from which we blit

    Raises:
        SystemExit: if the player chooses to quit
    """
    draw_endgame(is_win, root_console, draw_console)
    while state.endgame:
        dispatch = EndgameEventDispatch(state)
        for event in tcod.event.wait():
            dispatch.dispatch(event)


def main():
    # what do i wish the main loop looked like?
    # set up the console
    # set up event dispatching
    # draw game state
    # dispatch events, which should create commands
    # process commands by updating game state

    # i wish the game was set up like a state machine though
    # where you start in the main event "state"
    # and can transition to the endgame "state"
    # this could be useful later for things like menus
    setup()
    state = GameState()
    with tcod.console_init_root(
            state.width,
            state.height,
            order='F',
            renderer=tcod.RENDERER_SDL2,
            title='No Warning',
            vsync=True
    ) as root_console:
        draw_console = tcod.console.Console(state.width, state.height, order='F')
        dispatch = MainEventDispatch(state)
        while True:
            if state.endgame:
                handle_endgame(state, True, root_console, draw_console)
                draw_console.clear()
                root_console.clear()
                continue
            draw_console.put_char(state.player_x, state.player_y, ord('@'))
            draw_console.blit(
                root_console,
                width=draw_console.width,
                height=draw_console.height
            )
            tcod.console_flush()
            for event in tcod.event.wait():
                dispatch.dispatch(event)


if __name__ == '__main__':
    main()
