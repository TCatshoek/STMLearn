import unittest

from stmlearn.equivalencecheckers import WmethodEquivalenceChecker, SmartWmethodEquivalenceChecker
from stmlearn.util import load_mealy_dot
import random
from zipfile import ZipFile
from shutil import rmtree


class WmethodTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        super(WmethodTests, cls).setUpClass()
        # Unzip test cases
        with ZipFile('../data/rers_industrial_tests.zip', 'r') as zipfile:
            zipfile.extractall('testcases')

    @classmethod
    def tearDownClass(cls):
        super(WmethodTests, cls).tearDownClass()
        rmtree('testcases')

    def setUp(self):
        # Load testcases
        testcases = [
            "testcases/m54.dot",
            "testcases/m164.dot",
            "testcases/m22.dot",
            #"testcases/m182.dot" # slow
        ]
        self.systems = {name: load_mealy_dot(name) for name in testcases}

    def test_wmethod_equal(self):
        for name, system in self.systems.items():
            n_states = len(system.get_states())
            eqc = WmethodEquivalenceChecker(system, m=n_states)
            equivalent, _ = eqc.test_equivalence(system)
            self.assertTrue(equivalent)

    def test_wmethod_random_changes(self):
        for i in range(10):  # try a bunch of random changes
            for name, system in self.systems.items():
                # Change one output
                system2 = load_mealy_dot(name)
                modified_state = random.choice(system2.get_states())
                # Choose random input
                random_inp = random.choice(list(system.get_alphabet()))
                og_next_state, og_out = modified_state.edges[random_inp]
                modified_state.edges[random_inp] = (og_next_state, 'FKSLDJFKSLDJFLSKDJ')
                print(f"Modified state {modified_state.name}, action {random_inp} -> ({og_next_state.name}, {og_out})")
                n_states = len(system.get_states())
                eqc = WmethodEquivalenceChecker(system, m=n_states)
                equivalent, _ = eqc.test_equivalence(system2)

                self.assertFalse(equivalent, msg=f'Failure in {name}')

    def test_smart_wmethod_random_changes(self):
        for i in range(10):  # try a bunch of random changes
            for name, system in self.systems.items():
                # Change one output
                system2 = load_mealy_dot(name)
                modified_state = random.choice(system2.get_states())
                # Choose random input
                random_inp = random.choice(list(system.get_alphabet()))
                og_next_state, og_out = modified_state.edges[random_inp]
                modified_state.edges[random_inp] = (og_next_state, 'FKSLDJFKSLDJFLSKDJ')
                print(f"Modified state {modified_state.name}, action {random_inp} -> ({og_next_state.name}, {og_out})")
                n_states = len(system.get_states())
                eqc = SmartWmethodEquivalenceChecker(system, m=n_states)
                equivalent, _ = eqc.test_equivalence(system2)

                self.assertFalse(equivalent, msg=f'Failure in {name}')

    # This test fails if we forget to check without distinguishing sequence as well
    def test_wmethod_different_problematic(self):
        name = "testcases/m164.dot"
        system = self.systems[name]

        # Change one output
        system2 = load_mealy_dot(name)
        modified_state = [state for state in system2.get_states() if state.name == '3'][0]

        # Choose random input
        random_inp = 'usr2_ai3_re5'
        og_next_state, og_out = modified_state.edges[random_inp]
        modified_state.edges[random_inp] = (og_next_state, 'FKSLDJFKSLDJFLSKDJ')
        print(f"Modified state {modified_state.name}, action {random_inp} -> ({og_next_state.name}, {og_out})")
        n_states = len(system.get_states())

        eqc = WmethodEquivalenceChecker(system, m=n_states)

        equivalent, _ = eqc.test_equivalence(system2)

        self.assertFalse(equivalent, msg=f'Failure in {name}')

    def test_smart_wmethod_different_problematic(self):
        name = "testcases/m164.dot"
        system = self.systems[name]

        # Change one output
        system2 = load_mealy_dot(name)
        modified_state = [state for state in system2.get_states() if state.name == '3'][0]

        # Choose random input
        random_inp = 'usr2_ai3_re5'
        og_next_state, og_out = modified_state.edges[random_inp]
        modified_state.edges[random_inp] = (og_next_state, 'FKSLDJFKSLDJFLSKDJ')
        print(f"Modified state {modified_state.name}, action {random_inp} -> ({og_next_state.name}, {og_out})")
        n_states = len(system.get_states())

        eqc = SmartWmethodEquivalenceChecker(system, m=n_states)

        equivalent, _ = eqc.test_equivalence(system2)

        self.assertFalse(equivalent, msg=f'Failure in {name}')
