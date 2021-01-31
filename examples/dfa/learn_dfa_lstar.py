import tempfile

from stmlearn.equivalencecheckers import BFEquivalenceChecker
from stmlearn.learners import LStarDFALearner
from stmlearn.suls import RegexMachine
from stmlearn.suls import DFA, DFAState
from stmlearn.teachers import Teacher

# Set up a simple state machine (S1) =a> (S2) =b> ((S3))

s1 = DFAState('s1')
s2 = DFAState('s2')
s3 = DFAState('s3')

s1.add_edge('a', s2)
s2.add_edge('b', s3)

sm = DFA(s1, [s3])

# Note: We need edges for the whole alphabet in every state, so add them too
s1.add_edge('b', s1)
s2.add_edge('a', s2)
s3.add_edge('a', s3)
s3.add_edge('b', s3)

sm = DFA(s1, [s3])

# We are using the brute force equivalence checker
eqc = BFEquivalenceChecker(sm, max_depth=4)

# Set up the teacher, with the system under learning and the equivalence checker
teacher = Teacher(sm, eqc)

# Set up the learner who only talks to the teacher
learner = LStarDFALearner(teacher)

# Get the learners hypothesis
hyp = learner.run(show_intermediate=True)

hyp.render_graph(tempfile.mktemp('.gv'))
