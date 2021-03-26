import unittest
from stmlearn.util import load_mealy_dot
import tempfile
from stmlearn.util._dotloader import go_mealy_parser
from stmlearn.util.distinguishingset._minsepseq import _render
from stmlearn.equivalencecheckers import WmethodEquivalenceChecker

class SimpleTestPartition(unittest.TestCase):

    def test_read_write_dset_go(self):

        # Load a test mealy machine
        mm_og = load_mealy_dot("../partition/rers_industrial_tests/m182.dot")
        print("Original:", len(mm_og.get_states()), "States")

        # Write it to disk
        path = tempfile.mktemp(".dot")
        _render(mm_og, path)

        # And load it again
        mm_loaded = load_mealy_dot(path, parse_rules=go_mealy_parser)

        # Do we have the same amount of states?
        self.assertEqual(
            len(mm_og.get_states()),
            len(mm_loaded.get_states()),
        msg="Amount of states not equal")

        # Do a W-method equivalence check to ensure the state machines are equal
        eqc = WmethodEquivalenceChecker(mm_og, m=len(mm_og.get_states()))
        equivalent, _ = eqc.test_equivalence(mm_loaded)

        self.assertTrue(
            equivalent,
            msg="Loaded state machine is not equal to the original!"
        )

    def test_double_read_write_dset_go(self):

        # Load a test mealy machine
        mm_og = load_mealy_dot("../partition/rers_industrial_tests/m54.dot")
        print("Original:", len(mm_og.get_states()), "States")

        # Write it to disk
        path = tempfile.mktemp(".dot")
        _render(mm_og, path)

        # And load it again
        mm_loaded = load_mealy_dot(path, parse_rules=go_mealy_parser)

        # Write it to disk again
        path2 = tempfile.mktemp(".dot")
        _render(mm_og, path2)

        # And load it again
        mm_loaded_2 = load_mealy_dot(path, parse_rules=go_mealy_parser)

        # Do we have the same amount of states?
        self.assertEqual(
            len(mm_loaded.get_states()),
            len(mm_og.get_states()),
            msg="Amount of states not equal")
        self.assertEqual(
            len(mm_loaded.get_states()),
            len(mm_loaded_2.get_states()),
            msg="Amount of states not equal")

        # Do a W-method equivalence check to ensure the state machines are equal
        eqc = WmethodEquivalenceChecker(mm_loaded, m=len(mm_loaded.get_states()))
        equivalent, _ = eqc.test_equivalence(mm_loaded_2)

        self.assertTrue(
            equivalent,
            msg="Loaded state machine is not equal to the original!"
        )

