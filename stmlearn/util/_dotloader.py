import tempfile
from stmlearn.suls import MealyState, MealyMachine
import re


# Edge regex
# ^\s*(.*\s*->\s*\S*)\s*\[((?:\w*=\S*\s*)+)\];

# Node regex
# ^\s*([a-zA-Z0-9"^(\->)]*)\s\[((?:\w*=\S*\s*)+)\];

def _process_mealy_node(match, context):
    node = match.group(1).strip('"')
    if len(match.groups()) > 1:
        node_properties = dict([tuple(x.split('=')) for x in match.group(2).strip().split(' ')])
    else:
        node_properties = {}
    context['nodes'].append((node, node_properties))


def _process_mealy_edge(match, context):
    edge = tuple([x.strip().strip('"') for x in match.group(1).split('->')])
    edge_properties = dict(
        [(a.strip('"'), b.strip('"')) for a, b in [tuple(x.split('=')) for x in match.group(2).strip().split(' ')]])
    context['edges'].append((edge, edge_properties))


def _process_mealy_start(match, context):
    start = match.group(1)
    context['start'] = start.strip('"')


# Loads the dot files in rers/industrial
industrial_mealy_parser = [
    (r'^\s*([a-zA-Z0-9"^(\->)]*)\s\[((?:\w*=\S*\s*)+)\];', _process_mealy_node),
    (r'^\s*(.*\s*->\s*\S*)\s*\[((?:\w*=\S*\s*)+)\];', _process_mealy_edge),
    (r'^\s*(?:.*\s*->\s*(\S*));', _process_mealy_start)
]

# Loads hypotheses saved by util/savehypothesis
hyp_mealy_parser = [
    (r'^\s*([a-zA-Z0-9]+)$', _process_mealy_node),
    (r'^\s*(.*\s*->\s*\S*)\s*\[((?:\w*=\S*\s*)+)\]', _process_mealy_edge),
    (r'^\s*(?:__start0\s*->\s*(\S*))', _process_mealy_start)
]

# Loads hypotheses generated to send to the Go code
go_mealy_parser = [
    (r'^\s*([a-zA-Z0-9]+)$', _process_mealy_node),
    (r'^\s*(.*\s*->\s*\S*)\s*\[((?:\w*=\S*\s*)+)\]', _process_mealy_edge),
    # (r'^\s*(0)$', _process_mealy_start)
]


def _parse(process, line, context):
    for (regex, process_func) in process:
        if (match := re.match(regex, line)) is not None:
            return process_func(match, context)


def load_mealy_dot(path, parse_rules=industrial_mealy_parser):  # industrial_mealy_parser):
    # Parse the dot file
    context = {'nodes': [], 'edges': []}
    with open(path, 'r') as file:
        for line in file.readlines():
            _parse(parse_rules, line, context)

    # Build the mealy graph
    nodes = {name: MealyState(name) for (name, _) in context['nodes']}
    for (frm, to), edge_properties in context['edges']:
        input, output = edge_properties['label'].strip('"').split('/')
        nodes[frm].add_edge(input, output, nodes[to])

    if 'start' in context:
        startnode = nodes[context['start']]
    else:
        startnode = nodes["0"]

    return MealyMachine(startnode)


if __name__ == "__main__":
    path = "/tmp/tmp_u10p3fj.dot"
    mm = load_mealy_dot(path, parse_rules=go_mealy_parser)
    mm.render_graph(tempfile.mktemp('.gv'))
