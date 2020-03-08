import random
from dataclasses import dataclass
from enum import Enum
from typing import Dict, Optional, Tuple


class State(Enum):
    MAP = 'map'
    ENDGAME = 'endgame'


@dataclass
class Game:
    pass


class StateHandler:
    def __init__(self, next_state: State, game: Game):
        self.next_state = next_state
        self.game = game

    def handle(self) -> Tuple[Optional[State], Game]:
        """
        Override this to handle the state. Returning `None` will cause the
        state machine to terminate. Otherwise, return the next state and the
        game data to use in that state.
        """
        # For demo purposes, choose a random next state or `None`.
        self.next_state = random.choice(list(State) + [None])
        print(f'{self.__class__} -> {self.next_state}, {self.game}')
        return self.next_state, self.game


class MapStateHandler(StateHandler):
    pass


class EndgameStateHandler(StateHandler):
    pass


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
    state_handlers = {
        State.MAP: MapStateHandler,
        State.ENDGAME: EndgameStateHandler,
    }
    run_fsm(state_handlers, State.MAP, Game())


if __name__ == '__main__':
    main()
