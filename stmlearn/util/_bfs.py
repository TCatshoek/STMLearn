# Attempt to implement a general purpose BFS to prevent code duplication
from abc import ABC, abstractmethod
from typing import Union, Callable, Any, Tuple

from stmlearn.suls import DFA, MealyMachine, MealyState, DFAState
from collections import deque


class BFSStrategy(ABC):
    @abstractmethod
    def __call__(self, path, state, seen_before):
        pass


class TransitionCoverStrategy(BFSStrategy):
    def __init__(self):
        self.paths = set()

    def __call__(self, path, state, seen_before):
        self.paths.add(path)


class StateCoverStrategy(BFSStrategy):
    def __init__(self):
        self.paths = set()

    def __call__(self, path, state, seen_before):
        if not seen_before:
            self.paths.add(path)


# Takes a function (path, state, seen_before) -> any that gets called whenever a new state is reached
# return value of the provided function is ignored
def bfs(fsm: Union[MealyMachine, DFA],
        strategy: Callable[[Tuple, Union[MealyState, DFAState], bool], Any] = None):
    to_visit = deque([(tuple(), fsm.initial_state)])
    visited = []
    alphabet = fsm.get_alphabet()

    while len(to_visit) > 0:
        cur_path, cur_state = to_visit.popleft()

        # Call the hook
        if strategy is not None:
            strategy(cur_path, cur_state, False)

        for a in alphabet:
            next_state = cur_state.next_state(a)
            next_path = cur_path + (a,)

            if next_state not in visited:
                to_visit.append((next_path, next_state))
            else:
                if strategy is not None:
                    strategy(next_path, next_state, True)

    return visited
