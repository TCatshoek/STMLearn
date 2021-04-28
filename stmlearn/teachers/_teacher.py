from typing import Type, Union
from stmlearn.util import Logger, Log
from stmlearn.suls import SUL
from stmlearn.equivalencecheckers import EquivalenceChecker

# Simple wrapper class around the system under learning and equivalencechecker



class Teacher:
    def __init__(self, sul: SUL, eqc: Union[EquivalenceChecker, Type[EquivalenceChecker]]):
        self.sul = sul
        self.logger = Logger()
        # if we got passed a constructor as eqc, we need to initialize it
        # not sure if this is the best way to check it?
        if callable(eqc):
            self.eqc = eqc(sul=self.sul)
        else:
            self.eqc = eqc

        # Pass sul to checkers that don't have it yet
        if self.eqc.sul is None:
            self.eqc.sul = self.sul

        # Register the teacher in the checker for logging etc.
        self.eqc.set_teacher(self)

        self.member_query_counter = 0
        self.equivalence_query_counter = 0
        self.test_query_counter = 0

    def member_query(self, inputs):
        self.member_query_counter += 1

        self.logger.increment(Log.MEMBERSHIP)

        self.sul.reset()
        return self.sul.process_input(inputs)

    def equivalence_query(self, hypothesis: SUL):
        self.equivalence_query_counter += 1

        self.logger.increment(Log.EQUIVALENCE)

        return self.eqc.test_equivalence(hypothesis)

    def get_alphabet(self):
        return self.sul.get_alphabet()
