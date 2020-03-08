from dataclasses import dataclass
from enum import Enum
from typing import Dict, Optional, Tuple
import random

import tcod
import tcod.event

CONSOLE_WIDTH = 80
CONSOLE_HEIGHT = 50


@dataclass
class Mob:
    hp: int


@dataclass
class Game:
    # drawing context
    root_console: tcod.console.Console
    draw_console: tcod.console.Console
    # world state
    map_height: int
    map_width: int


class State(Enum):
    MAP = 'map'
    ENDGAME = 'endgame'


class StateHandler(tcod.event.EventDispatch):

    def __init__(self, next_state: Optional[State], game: Game) -> None:
        """Constructor"""
        self.next_state = next_state
        self.game = game

    def handle(self) -> Tuple[Optional[State], Game]:
        """
        Dispatch pending input events to handler methods, and then return the
        next state and a game instance to use in that state.
        """
        for event in tcod.event.wait():
            self.dispatch(event)
        return self.next_state, self.game

    def draw(self) -> None:
        """Override this to draw the screen for this state."""
        pass

    def on_enter_state(self) -> None:
        self.draw()
        blit_and_flush(self.game.draw_console, self.game.root_console)

    def on_reenter_state(self) -> None:
        self.draw()
        blit_and_flush(self.game.draw_console, self.game.root_console)


def blit_and_flush(
        from_console: tcod.console.Console,
        to_console: tcod.console.Console
) -> None:
    from_console.blit(
        to_console,
        width=from_console.width,
        height=from_console.height
    )
    tcod.console_flush()


def draw_endgame(game: Game):
        game.draw_console.clear()
        game.draw_console.print(1, 1, 'You win!')
        game.draw_console.print(1, 3, 'Press R to play again')
        game.draw_console.print(1, 5, 'Press Q to quit')
        game.draw_console.blit(
            game.root_console,
            width=game.draw_console.width,
            height=game.draw_console.height
        )
        tcod.console_flush()


def draw_map(game: Game) -> None:
    game.draw_console.clear()
    game.draw_console.draw_rect(
        game.map_width // 2,
        game.map_height // 2,
        1,
        1,
        ord('@'),
        fg=tcod.yellow
    )

class MapStateHandler(StateHandler):

    def draw(self):
        draw_map(self.game)

    def ev_quit(self, event):
        self.next_state = None

    def ev_keydown(self, event):
        if event.scancode == tcod.event.SCANCODE_F:
            fullscreen = not tcod.console_is_fullscreen()
            tcod.console_set_fullscreen(fullscreen)
        elif event.scancode == tcod.event.SCANCODE_Q:
            self.next_state = None  # quit
        elif event.scancode == tcod.event.SCANCODE_W:
            self.next_state = State.ENDGAME  # win


class EndgameStateHandler(StateHandler):

    def draw(self):
        draw_endgame(self.game)

    def ev_quit(self, event):
        self.next_state = None

    def ev_keydown(self, event):
        if event.scancode == tcod.event.SCANCODE_F:
            fullscreen = not tcod.console_is_fullscreen()
            tcod.console_set_fullscreen(fullscreen)
        elif event.scancode == tcod.event.SCANCODE_Q:
            self.next_state = None  # quit
        elif event.scancode == tcod.event.SCANCODE_R:
            self.next_state = State.MAP  # restart
            self.game = build_game(self.game.root_console, self.game.draw_console)


def run_fsm(
        state_handlers: Dict[State, StateHandler],
        state: State,
        game: Game
) -> None:
    last_state = None
    while state is not None:
        handler_class = state_handlers[state]
        handler = handler_class(state, game)
        if state == last_state:
            handler.on_reenter_state()
        else:
            handler.on_enter_state()
        last_state = state
        state, game = handler.handle()


def build_game(
        root_console: tcod.console.Console,
        draw_console: tcod.console.Console
) -> Game:
    map_width = CONSOLE_WIDTH
    map_height = CONSOLE_HEIGHT
    return Game(
        root_console=root_console,
        draw_console=draw_console,
        map_width=map_width,
        map_height=map_height
    )


def main():
    tcod.console_set_custom_font(
        'arial10x10.png',
        tcod.FONT_LAYOUT_TCOD | tcod.FONT_TYPE_GREYSCALE,
    )
    with tcod.console_init_root(
            CONSOLE_WIDTH,
            CONSOLE_HEIGHT,
            order='F',
            renderer=tcod.RENDERER_SDL2,
            title='FSM Game',
            vsync=True
    ) as root_console:
        draw_console = tcod.console.Console(CONSOLE_WIDTH, CONSOLE_HEIGHT, order='F')
        state_handlers = {
            State.MAP: MapStateHandler,
            State.ENDGAME: EndgameStateHandler,
        }
        game = build_game(root_console, draw_console)
        run_fsm(state_handlers, State.MAP, game)


if __name__ == '__main__':
    main()
