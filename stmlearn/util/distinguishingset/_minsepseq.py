import subprocess
import tempfile
from graphviz import Digraph
from stmlearn.suls import MealyMachine, DFA
import re
from pathlib import Path
from os.path import abspath

distsetpath = Path(abspath(__file__)).parent.joinpath('distset')


def _render(fsm: MealyMachine, filename):
    states = sorted(fsm.get_states(), key=lambda x: int(x.name.strip('s')))
    alphabet = sorted(fsm.get_alphabet())

    g = Digraph('G', filename=filename)
    g.attr(rankdir='LR')

    # Add states
    for state in states:
        g.node(state.name)

    # Add transitions:
    for state in states:
        for action, (other_state, output) in sorted(state.edges.items(), key=lambda x: x[0]):
            g.edge(state.name, other_state.name, label=f'{action}/{output}')

    g.save()


def check_distinguishing_set(fsm, dset):
    outputs = get_dset_outputs(fsm, dset)

    if len(set(outputs.values())) < len(outputs):
        print("Dset outputs not unique!")
        print('Dset size:', len(dset))
        print("Dset: ", dset)
        print("Outputs:", list(outputs.values()))
        return False
    else:
        print('Dset succes!', len(outputs), 'states,', len(set(outputs)), 'unique outputs')
        print('Dset size:', len(dset))
        return True


def get_dset_outputs(fsm, dset):
    states = fsm.get_states()
    outputs = {}
    for state in states:
        if isinstance(fsm, MealyMachine):
            mm = MealyMachine(state)
        elif isinstance(fsm, DFA):
            mm = DFA(state, fsm.accepting_states)

        out = []
        for dseq in dset:
            out.append(mm.process_input(dseq))
            mm.reset()
        outputs[state] = tuple(out.copy())
    return outputs


def get_distinguishing_set(fsm: MealyMachine, check=True):
    path = tempfile.mktemp(".gv")
    print("TMP PATH: ", path)

    _render(fsm, path)

    dset = set(_run_distset(path))
    dset.remove(tuple())

    if check:
        check_distinguishing_set(fsm, dset)

    return dset


def _run_distset(path_to_dot, return_mappings=False):
    cases = {
        "State": {},
        "Output": {},
        "Input": {}
    }

    suffixes = []

    result = subprocess.run([distsetpath, '-path', path_to_dot, '-strategy', '0'], capture_output=True)
    for line in result.stdout.decode().split('\n'):

        if re.match("State|Output|Input .*", line):
            case, original, id = line.split(' ')
            cases[case][id] = original

        if re.match("Suffix .*", line):
            suffix = []
            line = line.replace("Suffix ", "")
            for a in line.strip().split(" "):
                if len(a) > 0:
                    suffix.append(cases["Input"][a])

            suffixes.append(tuple(suffix))

    if return_mappings:
        return suffixes, cases
    else:
        return suffixes

