from stmlearn.equivalencecheckers._equivalencechecker import EquivalenceChecker
from stmlearn.suls import SUL

from typing import List, Optional, Iterable, Tuple, Callable

def Sequential(*args, **kwargs):
    def makeStacked(*inner_args, **kwargs):
        return StackedChecker(*args, **kwargs)
    return makeStacked

class StackedChecker(EquivalenceChecker):
    def __init__(self, *args, **kwargs):
        super().__init__(None)
        self.checkers: List[EquivalenceChecker] = []

        self.sul = None

        if 'sul' in kwargs:
            self.sul = kwargs['sul']

        for arg in args:
            if callable(arg):
                if self.sul is None:
                    raise Exception("Please specify SUL if you provide constructors to the stacked checker")
                self.checkers.append(arg(sul=self.sul))
            else:
                self.checkers.append(arg)
                if arg.sul is None:
                    arg.sul = self.sul

    # Gets the equivalence checkers in this stack by class name
    def get_eqc(self, eqc_name):
        return list(filter(lambda checker: eqc_name == type(checker).__name__, self.checkers))

    def set_teacher(self, teacher):
        self.teacher = teacher
        for checker in self.checkers:
            checker.set_teacher(teacher)

    def test_equivalence(self, test_sul: SUL) -> Tuple[bool, Optional[Iterable]]:
        for checker in self.checkers:
            print('EQ check using', type(checker).__name__)
            equivalent, input = checker.test_equivalence(test_sul)

            if not equivalent:
                return False, input

        return True, None

    def onCounterexample(self, fun: Callable[[Iterable], None]):
        for checker in self.checkers:
            checker.onCounterexample(fun)

    def _are_equivalent(self, fsm, input):
        assert False, "Don't call the _are_equivalent of the stacker directly"
