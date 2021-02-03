import unittest

from stmlearn.equivalencecheckers import WmethodEquivalenceChecker, BFEquivalenceChecker
from stmlearn.learners import LStarDFALearner, TTTDFALearner
from stmlearn.suls import DFAState, DFA
from stmlearn.teachers import Teacher


# These may not be very good tests, since L* kinda finds everything without an equivalence check in this case
# but it is nice to see if all the different combination work at least
class LearnSimpleDFA(unittest.TestCase):
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

    def test_lstar_wmethod(self):
        eqc = WmethodEquivalenceChecker(self.dfa, m=len(self.dfa.get_states()))
        teacher = Teacher(self.dfa, eqc)
        learner = LStarDFALearner(teacher)
        hyp = learner.run()
        equivalent, _ = eqc.test_equivalence(hyp)
        self.assertTrue(equivalent)
        self.assertEqual(
            len(self.dfa.get_states()),
            len(hyp.get_states()),
        )

    def test_lstar_bruteforce(self):
        eqc = BFEquivalenceChecker(self.dfa, max_depth=len(self.dfa.get_states()))
        teacher = Teacher(self.dfa, eqc)
        learner = LStarDFALearner(teacher)
        hyp = learner.run()
        equivalent, _ = WmethodEquivalenceChecker(self.dfa, m=len(self.dfa.get_states())).test_equivalence(hyp)
        self.assertTrue(equivalent)
        self.assertEqual(
            len(self.dfa.get_states()),
            len(hyp.get_states()),
        )

    def test_ttt_wmethod(self):
        eqc = WmethodEquivalenceChecker(self.dfa, m=len(self.dfa.get_states()))
        teacher = Teacher(self.dfa, eqc)
        learner = TTTDFALearner(teacher)
        hyp = learner.run()
        equivalent, _ = eqc.test_equivalence(hyp)
        self.assertTrue(equivalent)
        self.assertEqual(
            len(self.dfa.get_states()),
            len(hyp.get_states()),
        )

    def test_ttt_bruteforce(self):
        eqc = BFEquivalenceChecker(self.dfa, max_depth=len(self.dfa.get_states()))
        teacher = Teacher(self.dfa, eqc)
        learner = TTTDFALearner(teacher)
        hyp = learner.run()
        equivalent, _ = WmethodEquivalenceChecker(self.dfa, m=len(self.dfa.get_states())).test_equivalence(hyp)
        self.assertTrue(equivalent)
        self.assertEqual(
            len(self.dfa.get_states()),
            len(hyp.get_states()),
        )