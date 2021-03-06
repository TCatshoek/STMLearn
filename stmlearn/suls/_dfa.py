# Need this to fix types
from __future__ import annotations

import tempfile
from typing import Union, Iterable
from stmlearn.suls import SUL

from graphviz import Digraph


class DFAState:
    def __init__(self, name: str, edges=None):
        if edges is None:
            edges = {}

        self.name = name
        self.edges = edges
        self.isAccepting = False

    def __str__(self):
        return f'[State: {self.name}, edges: {[f"{a}:{n.name}" for a, n in self.edges.items()]}]'

    def add_edge(self, action: str, other_state: DFAState, override=False):
        if override:
            self.edges[action] = other_state
        else:
            if action not in self.edges.keys():
                self.edges[action] = other_state
            else:
                raise Exception(f'{action} already defined in state {self.name}')

    def next(self, action):
        if action in self.edges.keys():
            nextstate = self.edges.get(action)
            return nextstate, nextstate.isAccepting
        else:
            raise Exception(f'Invalid action {action} from state {self.name}')

    def next_state(self, action):
        return self.next(action)[0]


# A statemachine can represent a system under learning
class DFA(SUL):
    def __init__(self, initial_state: DFAState, accepting_states: Union[DFAState, Iterable[DFAState]]):
        self.initial_state = initial_state
        self.state = initial_state

        if not isinstance(accepting_states, Iterable):
            accepting_states = [accepting_states]
        self.accepting_states = accepting_states
        for state in self.accepting_states:
            state.isAccepting = True

    def __str__(self):
        states = self.get_states()

        # Hacky backslash thing
        tab = '\t'
        nl = '\n'
        return f'[DFA: \n {nl.join([f"{tab}{str(state)}" for state in states])} ' \
               f'\n\n\t[Initial state: {self.initial_state.name}]' \
               f'\n\t[Accepting states: {[s.name for s in self.accepting_states]}]' \
               f'\n]'

    def get_states(self):
        to_visit = [self.initial_state]
        visited = []

        while len(to_visit) > 0:
            cur_state = to_visit.pop()
            if cur_state not in visited:
                visited.append(cur_state)

            for action, other_state in cur_state.edges.items():
                if other_state not in visited and other_state not in to_visit:
                    to_visit.append(other_state)

        return visited

    # Traverses all states and collects all possible actions (i.e. the alphabet of the language)
    def get_alphabet(self):
        states = self.get_states()
        actions = set()

        for state in states:
            actions = actions.union(set(state.edges.keys()))

        return actions

    # Runs the given inputs on the state machine
    def process_input(self, inputs):
        if not isinstance(inputs, Iterable):
            inputs = [inputs]

        for input in inputs:
            try:
                nextstate = self.state.next_state(input)
                # print(f'({self.state.name}) ={input}=> ({nextstate.name})')
                self.state = nextstate
            except Exception as e:
                print(e)
                return False

        return self.state in self.accepting_states

    def reset(self):
        self.state = self.initial_state

    def render_graph(self, filename=None, format='pdf'):
        if filename is None:
            filename = tempfile.mktemp('.gv')

        g = Digraph('G', filename=filename)
        g.attr(rankdir='LR')

        # Collect nodes and edges
        to_visit = [self.initial_state]
        visited = []

        # Hacky way to draw start arrow pointing to first node
        g.attr('node', shape='none')
        g.node('startz', label='', _attributes={'height': '0', 'width': '0'})

        # Draw initial state
        if self.initial_state in self.accepting_states:
            g.attr('node', shape='doublecircle')
        else:
            g.attr('node', shape='circle')
        g.node(self.initial_state.name)

        g.edge('startz', self.initial_state.name)

        while len(to_visit) > 0:
            cur_state = to_visit.pop()
            visited.append(cur_state)

            g.attr('node', shape='circle')
            for action, other_state in cur_state.edges.items():
                # Draw other states, but only once
                if other_state not in visited and other_state not in to_visit:
                    to_visit.append(other_state)
                    if other_state in self.accepting_states:
                        g.attr('node', shape='doublecircle')
                        g.node(other_state.name)
                        g.attr('node', shape='circle')
                    else:
                        g.node(other_state.name)

                # Draw edges too
                g.edge(cur_state.name, other_state.name, label=action)

        g.render(format=format, view=True)
