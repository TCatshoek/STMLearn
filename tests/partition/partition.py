import unittest

from stmlearn.suls import MealyState, MealyMachine
from stmlearn.util.partition import get_distinguishing_set
from stmlearn.util import load_mealy_dot

from zipfile import ZipFile
from shutil import rmtree

def _check_distinguishing_set(fsm, dset):
    outputs = _get_dset_outputs(fsm, dset)

    if len(set(outputs.values())) < len(outputs):
        print("Dset outputs not unique!")
        print("Dset: ", dset)
        print("Outputs:", list(outputs.values()))
        return False
    else:
        print('Dset succes!', len(outputs), 'states,', len(set(outputs)), 'unique outputs')
        print('Dset size:', len(dset))
        return True


def _get_dset_outputs(fsm, dset):
    states = fsm.get_states()
    outputs = {}
    for state in states:
        mm = MealyMachine(state)
        out = []
        for dseq in dset:
            out.append(mm.process_input(dseq))
            mm.reset()
        outputs[state] = tuple(out.copy())
    return outputs


class SimpleTestPartition(unittest.TestCase):
    def setUp(self):
        # Set up an example mealy machine
        s1 = MealyState('1')
        s2 = MealyState('2')
        s3 = MealyState('3')

        s1.add_edge('a', 'nice', s2)
        s1.add_edge('b', 'B', s1)
        s2.add_edge('a', 'nice', s3)
        s2.add_edge('b', 'back', s1)
        s3.add_edge('a', 'A', s3)
        s3.add_edge('b', 'back', s1)

        self.mm = MealyMachine(s1)

    def test_simple_hopcroft(self):
        dset = get_distinguishing_set(self.mm, method="Hopcroft")
        self.assertEqual(set([('a',), ('b',)]), dset)

    def test_simple_moore(self):
        dset = get_distinguishing_set(self.mm, method="Moore")
        self.assertEqual(set([('a',), ('b',)]), dset)


class SimpleSingleTestPartition(unittest.TestCase):
    def setUp(self):
        # Set up an example mealy machine
        s1 = MealyState('1')
        s2 = MealyState('2')
        s3 = MealyState('3')

        s1.add_edge('a', '1', s2)
        s1.add_edge('b', 'next', s1)
        s2.add_edge('a', '2', s3)
        s2.add_edge('b', 'next', s1)
        s3.add_edge('a', '3', s3)
        s3.add_edge('b', 'next', s1)

        self.mm = MealyMachine(s1)

    def test_single_simple_hopcroft(self):
        dset = get_distinguishing_set(self.mm, method="Hopcroft")
        self.assertEqual({('a',)}, dset)

    def test_single_simple_moore(self):
        dset = get_distinguishing_set(self.mm, method="Moore")
        self.assertEqual({('a',)}, dset)


class LongSingleTestPartition(unittest.TestCase):
    def setUp(self):
        # Set up an example mealy machine
        states = [MealyState(f'{i}') for i in range(100)]

        for state_a, state_b in [states[i: i + 2] for i in range(len(states) - 1)]:
            state_a.add_edge('a', state_a.name, state_b)
            state_a.add_edge('b', 'loop', state_a)
            state_a.add_edge('c', 'loop', state_a)
            state_a.add_edge('d', 'loop', state_a)

        states[-1].add_edge('a', states[-1].name, states[0])
        states[-1].add_edge('b', 'loop', states[-1])
        states[-1].add_edge('c', 'loop', states[-1])
        states[-1].add_edge('d', 'loop', states[-1])

        self.mm = MealyMachine(states[0])

    def test_single_long_hopcroft(self):
        dset = get_distinguishing_set(self.mm, method="Hopcroft")
        self.assertEqual({('a',)}, dset)

    def test_single_long_moore(self):
        dset = get_distinguishing_set(self.mm, method="Moore")
        self.assertEqual({('a',)}, dset)


class RersIndustrialTestPartitionSmall(unittest.TestCase):
    def setUp(self):
        # Unzip test cases
        with ZipFile('rers_industrial_tests.zip', 'r') as zipfile:
            zipfile.extractall('testcases')

        # Load testcases
        self.m54 = load_mealy_dot("testcases/m54.dot")
        self.m164 = load_mealy_dot("testcases/m164.dot")
        self.m22 = load_mealy_dot("testcases/m22.dot")
        self.m182 = load_mealy_dot("testcases/m182.dot")

    def tearDown(self):
        rmtree('testcases')

    def test_m54_hopcroft(self):
        dset = get_distinguishing_set(self.m54, method="Hopcroft")
        self.assertTrue(_check_distinguishing_set(self.m54, dset))

    def test_m54_moore(self):
        dset = get_distinguishing_set(self.m54, method="Moore")
        self.assertTrue(_check_distinguishing_set(self.m54, dset))

    def test_m164_hopcroft(self):
        dset = get_distinguishing_set(self.m164, method="Hopcroft")
        self.assertTrue(_check_distinguishing_set(self.m164, dset))

    def test_m164_moore(self):
        dset = get_distinguishing_set(self.m164, method="Moore")
        self.assertTrue(_check_distinguishing_set(self.m164, dset))

    def test_m22_hopcroft(self):
        dset = get_distinguishing_set(self.m22, method="Hopcroft")
        self.assertTrue(_check_distinguishing_set(self.m22, dset))

    def test_m22_moore(self):
        dset = get_distinguishing_set(self.m22, method="Moore")
        self.assertTrue(_check_distinguishing_set(self.m22, dset))

    def test_m182_hopcroft(self):
        dset = get_distinguishing_set(self.m182, method="Hopcroft")
        self.assertTrue(_check_distinguishing_set(self.m182, dset))

    def test_m182_moore(self):
        dset = get_distinguishing_set(self.m182, method="Moore")
        self.assertTrue(_check_distinguishing_set(self.m182, dset))

# Sloooow
# class HugeRersTestPartition(unittest.TestCase):
#     def setUp(self):
#         # Load RERS industrial m85
#         self.mm = load_mealy_dot("m85.dot")
#         print(len(self.mm.get_states()), "States - good luck")
#
#     def test_m85_hopcroft(self):
#         dset = get_distinguishing_set(self.mm, method="Hopcroft")
#         self.assertTrue(_check_distinguishing_set(self.mm, dset))
#
#     def test_m85_moore(self):
#         dset = get_distinguishing_set(self.mm, method="Moore")
#         self.assertTrue(_check_distinguishing_set(self.mm, dset))
