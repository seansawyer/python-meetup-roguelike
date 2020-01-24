from dataclasses import dataclass
from enum import Enum
from typing import Callable, Dict, Optional, Tuple

import tcod
import tcod.event

CONSOLE_WIDTH = 80
CONSOLE_HEIGHT = 50


@dataclass
class Game:
    # drawing context
    root_console: tcod.console.Console
    draw_console: tcod.console.Console
    # player state
    player_x: int = CONSOLE_WIDTH // 2
    player_y: int = CONSOLE_HEIGHT // 2


class State(Enum):
    MAP = 'map'
    ENDGAME = 'endgame'


class StateHandler(tcod.event.EventDispatch):

    def __init__(self, next_state: Optional[State], game: Game) -> None:
        self.next_state = next_state
        self.game = game

    def handle(self) -> Tuple[Optional[State], Game]:
        self.draw()
        for event in tcod.event.wait():
            self.dispatch(event)
        return self.next_state, self.game

    def draw(self) -> None:
        pass


class MapStateHandler(StateHandler):

    def draw(self):
        self.game.draw_console.clear()
        self.game.draw_console.put_char(
            self.game.player_x,
            self.game.player_y,
            ord('@')
        )
        self.game.draw_console.blit(
            self.game.root_console,
            width=self.game.draw_console.width,
            height=self.game.draw_console.height
        )
        tcod.console_flush()

    def ev_quit(self, event):
        self.next_state = None

    def ev_keydown(self, event):
        print(event)
        if event.scancode == tcod.event.SCANCODE_F:
            fullscreen = not tcod.console_is_fullscreen()
            tcod.console_set_fullscreen(fullscreen)
        elif event.scancode == tcod.event.SCANCODE_Q:
            self.next_state = None
        elif event.scancode == tcod.event.SCANCODE_W:
            self.next_state = State.ENDGAME
        elif event.scancode == tcod.event.SCANCODE_H:
            # left
            self.game.player_x = max(0, self.game.player_x - 1)
        elif event.scancode == tcod.event.SCANCODE_J:
            # down
            self.game.player_y = min(CONSOLE_HEIGHT - 1, self.game.player_y + 1)
        elif event.scancode == tcod.event.SCANCODE_K:
            # up
            self.game.player_y = max(0, self.game.player_y - 1)
        elif event.scancode == tcod.event.SCANCODE_L:
            # right
            self.game.player_x = min(CONSOLE_WIDTH - 1, self.game.player_x + 1)


class EndgameStateHandler(StateHandler):

    def draw(self):
        self.game.draw_console.clear()
        self.game.draw_console.print(1, 1, f'You win!')
        self.game.draw_console.print(1, 3, 'Press R to play again')
        self.game.draw_console.print(1, 5, 'Press Q to quit')
        self.game.draw_console.blit(
            self.game.root_console,
            width=self.game.draw_console.width,
            height=self.game.draw_console.height
        )
        tcod.console_flush()

    def ev_quit(self, event):
        self.next_state = None

    def ev_keydown(self, event):
        print(event)
        if event.scancode == tcod.event.SCANCODE_F:
            fullscreen = not tcod.console_is_fullscreen()
            tcod.console_set_fullscreen(fullscreen)
        elif event.scancode == tcod.event.SCANCODE_Q:
            # quit
            self.next_state = None
        elif event.scancode == tcod.event.SCANCODE_R:
            # restart
            self.next_state = State.MAP
            self.game = Game(
                root_console=self.game.root_console,
                draw_console=self.game.draw_console
            )


def run_fsm(
        state_handlers: Dict[State, StateHandler],
        state: State,
        game: Game
) -> None:
    while state is not None:
        handler_class = state_handlers[state]
        handler = handler_class(state, game)
        state, game = handler.handle()


def main():
    tcod.console_set_custom_font(
        "arial10x10.png",
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
        game = Game(root_console=root_console, draw_console=draw_console)
        my_state_handlers = {
            State.MAP: MapStateHandler,
            State.ENDGAME: EndgameStateHandler,
        }
        run_fsm(my_state_handlers, State.MAP, game)


if __name__ == '__main__':
    main()
