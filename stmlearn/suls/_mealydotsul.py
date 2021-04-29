from typing import Iterable
from stmlearn.suls import SUL
import pydot
import networkx
from networkx.algorithms.traversal.breadth_first_search import bfs_edges

class MealyDotSUL(SUL):
    def __init__(self, dotfile,
                 initial_state_name="0",
                 edge_attr_name="label",
                 edge_attr_parser=lambda x: tuple(x.strip("\"").split("/"))):

        self.graph = pydot.graph_from_dot_file(dotfile)[0]
        self.nx_graph = networkx.drawing.nx_pydot.from_pydot(self.graph)

        self.initial_state_name = initial_state_name
        self.cur_state_name = self.initial_state_name

        self.edge_attr_name = edge_attr_name
        self.edge_attr_parser = edge_attr_parser

        self.edge_map = {}

        self.alphabet = set()

        node_names = self._get_node_names()
        for node_name in node_names:
            self._get_edges(node_name)


    def _get_node_names(self):
        edges = bfs_edges(self.nx_graph, self.initial_state_name)
        nodes = [self.initial_state_name] + [v for u, v in edges]
        return nodes

    def _get_edges(self, cur_node_name):
        cur_node = self.nx_graph[cur_node_name]
        cur_node_edge_map = {}
        for target_node_name, edges in cur_node.items():
            for edge in edges.values():
                action, output = self.edge_attr_parser(edge[self.edge_attr_name])
                cur_node_edge_map[action] = (target_node_name, output)
                self.alphabet.add(action)
            self.edge_map[cur_node_name] = cur_node_edge_map


    def process_input(self, inputs):
        last_output = None

        if isinstance(inputs, str) or not isinstance(inputs, Iterable):
            inputs = [inputs]

        for input in inputs:
            next_state_name, output = self.edge_map[self.cur_state_name][input]
            self.cur_state_name = next_state_name
            last_output = output

        return last_output

    def reset(self):
        self.cur_state_name = self.initial_state_name

    def get_alphabet(self):
        return self.alphabet

    def render_graph(self):
        self.graph.set('rankdir', 'LR')
        self.graph.create_svg()