import unittest

from stmlearn.equivalencecheckers import WmethodEquivalenceChecker, BFEquivalenceChecker, SmartWmethodEquivalenceChecker
from stmlearn.learners import LStarMealyLearner, TTTMealyLearner
from stmlearn.suls import MealyState, MealyMachine, DFAState, DFA
from stmlearn.teachers import Teacher
from stmlearn.util import load_mealy_dot
from stmlearn.suls.caches.dictcache import DictCache

from zipfile import ZipFile
from shutil import rmtree

# These may not be very good tests, since L* kinda finds everything without an equivalence check in this case
# but it is nice to see if all the different combination work at least
class LearnSimpleMealy(unittest.TestCase):
    def setUp(self):
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

    def test_lstar_wmethod(self):
        eqc = WmethodEquivalenceChecker(self.mm, m=len(self.mm.get_states()))
        teacher = Teacher(self.mm, eqc)
        learner = LStarMealyLearner(teacher)
        hyp = learner.run()
        equivalent, _ = eqc.test_equivalence(hyp)
        self.assertTrue(equivalent)
        self.assertEqual(
            len(self.mm.get_states()),
            len(hyp.get_states()),
        )

    def test_lstar_bruteforce(self):
        eqc = BFEquivalenceChecker(self.mm, max_depth=len(self.mm.get_states()))
        teacher = Teacher(self.mm, eqc)
        learner = LStarMealyLearner(teacher)
        hyp = learner.run()
        equivalent, _ = WmethodEquivalenceChecker(self.mm, m=len(self.mm.get_states())).test_equivalence(hyp)
        self.assertTrue(equivalent)
        self.assertEqual(
            len(self.mm.get_states()),
            len(hyp.get_states()),
        )


# More thorough, but slower
class LearnIndustrialMealy(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        super(LearnIndustrialMealy, cls).setUpClass()
        # Unzip test cases
        with ZipFile('../data/rers_industrial_tests.zip', 'r') as zipfile:
            zipfile.extractall('testcases')

    @classmethod
    def tearDownClass(cls):
        super(LearnIndustrialMealy, cls).tearDownClass()
        rmtree('testcases')

    def setUp(self):
        # Load testcases
        self.m54 = load_mealy_dot("testcases/m54.dot")
        self.m164 = load_mealy_dot("testcases/m164.dot")
        self.m22 = load_mealy_dot("testcases/m22.dot")
        self.m182 = load_mealy_dot("testcases/m182.dot")

        self.systems = {
            'm54': self.m54,
            'm164': self.m164,
            # 'm22':  self.m22,      # too slow
            # 'm182': self.m182      # too slow
        }

    def test_lstar_wmethod(self):
        for name, system in self.systems.items():
            n_states = len(system.get_states())
            sul = DictCache(system)
            eqc = WmethodEquivalenceChecker(sul, m=n_states)
            teacher = Teacher(sul, eqc)
            learner = LStarMealyLearner(teacher)
            hyp = learner.run()
            equivalent, _ = eqc.test_equivalence(hyp)
            self.assertTrue(equivalent)
            self.assertEqual(
                n_states,
                len(hyp.get_states()),
            )

    def test_TTT_wmethod(self):
        for name, system in self.systems.items():
            n_states = len(system.get_states())
            sul = DictCache(system)
            eqc = SmartWmethodEquivalenceChecker(sul, horizon=6, stop_on={"error"}, order_type='ce count')

            teacher = Teacher(sul, eqc)
            learner = TTTMealyLearner(teacher)
            hyp = learner.run()
            equivalent, _ = eqc.test_equivalence(hyp)
            self.assertTrue(equivalent)
            self.assertEqual(
                n_states,
                len(hyp.get_states()),
            )
