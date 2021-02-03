import unittest

from stmlearn.suls import MealyState, MealyMachine, DFAState, DFA
from stmlearn.util.partition import get_distinguishing_set
from stmlearn.util import load_mealy_dot

from zipfile import ZipFile
from shutil import rmtree

from stmlearn.util.distinguishingset import check_distinguishing_set


class MealySimpleTestPartition(unittest.TestCase):
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
        self.assertTrue(check_distinguishing_set(self.mm, dset))
        self.assertEqual({('a',), ('b',)}, dset)

    def test_simple_moore(self):
        dset = get_distinguishing_set(self.mm, method="Moore")
        self.assertTrue(check_distinguishing_set(self.mm, dset))
        self.assertEqual({('a',), ('b',)}, dset)

class DFASimpleTestPartition(unittest.TestCase):
    def setUp(self):
        # Set up an example mealy machine
        s1 = DFAState('1')
        s2 = DFAState('2')
        s3 = DFAState('3')

        s1.add_edge('a', s2)
        s1.add_edge('b', s1)
        s2.add_edge('a', s3)
        s2.add_edge('b', s1)
        s3.add_edge('a', s3)
        s3.add_edge('b', s1)

        self.dfa = DFA(s1, [s3])

    def test_simple_hopcroft(self):
        dset = get_distinguishing_set(self.dfa, method="Hopcroft")
        self.assertTrue(check_distinguishing_set(self.dfa, dset))
        self.assertEqual({('a',), tuple()}, dset)

    def test_simple_moore(self):
        dset = get_distinguishing_set(self.dfa, method="Moore")
        self.assertTrue(check_distinguishing_set(self.dfa, dset))
        self.assertEqual({('a',), tuple()}, dset)

class DFASimpleTestPartition2(unittest.TestCase):
    def setUp(self):
        s1 = DFAState('s1')
        s2 = DFAState('s2')
        s3 = DFAState('s3')
        s1.add_edge('a', s2)
        s1.add_edge('b', s1)
        s2.add_edge('a', s2)
        s2.add_edge('b', s3)
        s3.add_edge('a', s3)
        s3.add_edge('b', s3)
        self.dfa = DFA(s1, [s3])

    def test_simple_hopcroft(self):
        dset = get_distinguishing_set(self.dfa, method="Hopcroft")
        self.assertTrue(check_distinguishing_set(self.dfa, dset))
        self.assertEqual({tuple(), ('b',)}, dset)

    def test_simple_moore(self):
        dset = get_distinguishing_set(self.dfa, method="Moore")
        self.assertTrue(check_distinguishing_set(self.dfa, dset))
        self.assertEqual({tuple(), ('b',)}, dset)



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


class RersIndustrialTestPartition(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        super(RersIndustrialTestPartition, cls).setUpClass()
        # Unzip test cases
        with ZipFile('../data/rers_industrial_tests.zip', 'r') as zipfile:
            zipfile.extractall('testcases')

    @classmethod
    def tearDownClass(cls):
        super(RersIndustrialTestPartition, cls).tearDownClass()
        rmtree('testcases')

    def setUp(self):
        # Load testcases
        self.m54 = load_mealy_dot("testcases/m54.dot")
        self.m164 = load_mealy_dot("testcases/m164.dot")
        self.m22 = load_mealy_dot("testcases/m22.dot")
        self.m182 = load_mealy_dot("testcases/m182.dot")

    def test_deterministic_moore(self):
        for i in range(10):
            dset1 = get_distinguishing_set(self.m54, method="Moore")
            dset2 = get_distinguishing_set(self.m54, method="Moore")
            self.assertEqual(dset1, dset2)

    def test_deterministic_hopcroft(self):
        for i in range(10):
            dset1 = get_distinguishing_set(self.m54, method="Hopcroft")
            dset2 = get_distinguishing_set(self.m54, method="Hopcroft")
            self.assertEqual(dset1, dset2)

    def test_m54_hopcroft(self):
        dset = get_distinguishing_set(self.m54, method="Hopcroft")
        self.assertTrue(check_distinguishing_set(self.m54, dset))

    def test_m54_moore(self):
        dset = get_distinguishing_set(self.m54, method="Moore")
        self.assertTrue(check_distinguishing_set(self.m54, dset))

    def test_m164_hopcroft(self):
        dset = get_distinguishing_set(self.m164, method="Hopcroft")
        self.assertTrue(check_distinguishing_set(self.m164, dset))

    def test_m164_moore(self):
        dset = get_distinguishing_set(self.m164, method="Moore")
        self.assertTrue(check_distinguishing_set(self.m164, dset))

    def test_m22_hopcroft(self):
        dset = get_distinguishing_set(self.m22, method="Hopcroft")
        self.assertTrue(check_distinguishing_set(self.m22, dset))

    def test_m22_moore(self):
        dset = get_distinguishing_set(self.m22, method="Moore")
        self.assertTrue(check_distinguishing_set(self.m22, dset))

    def test_m182_hopcroft(self):
        dset = get_distinguishing_set(self.m182, method="Hopcroft")
        self.assertTrue(check_distinguishing_set(self.m182, dset))

    def test_m182_moore(self):
        dset = get_distinguishing_set(self.m182, method="Moore")
        self.assertTrue(check_distinguishing_set(self.m182, dset))


# Takes over 5 minutes, too slow
# class HugeRersTestPartition(unittest.TestCase):
#     def setUp(self):
#         # Load RERS industrial m85
#         self.mm = load_mealy_dot("/home/tom/projects/lstar/rers/industrial/m85.dot")
#         print(len(self.mm.get_states()), "States - good luck")
#
#     def test_m85_hopcroft(self):
#         dset = get_distinguishing_set(self.mm, method="Hopcroft")
#         self.assertTrue(check_distinguishing_set(self.mm, dset))
#
#     def test_m85_moore(self):
#         dset = get_distinguishing_set(self.mm, method="Moore")
#         self.assertTrue(check_distinguishing_set(self.mm, dset))
