# Equivalence checker base class
from ._equivalencechecker import EquivalenceChecker

# Equivalence checker classes - TODO: big cleanup before exposing more
from ._wmethod import \
    WmethodEquivalenceChecker,\
    SmartWmethodEquivalenceCheckerV4 as SmartWmethodEquivalenceChecker
from ._bruteforce import BFEquivalenceChecker
from ._randomwalk import RandomWalkEquivalenceChecker

