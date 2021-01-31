import tempfile

from stmlearn.equivalencecheckers import WmethodEquivalenceChecker
from stmlearn.learners import TTTMealyLearner
from stmlearn.teachers import Teacher
from stmlearn.util import MakeRandomMealyMachine

## Randomly generate a mealy machine and learn from it

# input alphabet
A = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j']
# output alphabet
O = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10']

# Generate a mealy machine and try to minimize it
# Minimization is kinda broken so may sometimes result in non-minimal mealy machines
# In this case the assertion below will fail
mm = MakeRandomMealyMachine(100, A, O, minimize=True)

# Use the W method equivalence checker
eqc = WmethodEquivalenceChecker(mm,
                                m=len(mm.get_states()))

teacher = Teacher(mm, eqc)

learner = TTTMealyLearner(teacher)

hyp = learner.run(show_intermediate=False)

assert len(hyp.get_states()) == len(mm.get_states())

hyp.render_graph(tempfile.mktemp('.gv'))

print("done")