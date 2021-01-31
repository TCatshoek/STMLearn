
import tempfile

from stmlearn.equivalencecheckers import BFEquivalenceChecker
from stmlearn.suls import RegexMachine
from stmlearn.teachers import Teacher
from stmlearn.learners import LStarDFALearner

# Set up a SUT using regex
sm = RegexMachine('(bb)*(aa)*(bb)*')

# We are using the brute force equivalence checker
eqc = BFEquivalenceChecker(sm, max_depth=15)

# Set up the teacher, with the system under learning and the equivalence checker
teacher = Teacher(sm, eqc)

# Set up the learner who only talks to the teacher
learner = LStarDFALearner(teacher)

# Get the learners hypothesis
hyp = learner.run()

# Draw the learned dfa
hyp.render_graph(tempfile.mktemp('.gv'))
