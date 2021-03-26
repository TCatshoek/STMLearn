import unittest
from typing import Dict

from stmlearn.suls import MealyMachine
from stmlearn.util import get_state_cover_set
from stmlearn.util import load_mealy_dot
import random
from zipfile import ZipFile
from shutil import rmtree

class StateCoverTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        super(StateCoverTests, cls).setUpClass()
        # Unzip test cases
        with ZipFile('../data/rers_industrial_tests.zip', 'r') as zipfile:
            zipfile.extractall('testcases')

    @classmethod
    def tearDownClass(cls):
        super(StateCoverTests, cls).tearDownClass()
        rmtree('testcases')

    def setUp(self):
        # Load testcases
        testcases = [
            "testcases/m54.dot",
            "testcases/m164.dot",
            "testcases/m22.dot",
            "testcases/m182.dot"
        ]
        self.systems: Dict[str, MealyMachine] = {name: load_mealy_dot(name) for name in testcases}

    # Ensure all states are reached by the state cover set
    def test_statecover(self):
        for name, system in self.systems.items():
            states = system.get_states()
            p = get_state_cover_set(system)

            reached_by_statecover = []
            for acc_seq in p:
                system.reset()
                system.process_input(acc_seq)
                reached_by_statecover.append(system.state)

            self.assertCountEqual(states, reached_by_statecover)
