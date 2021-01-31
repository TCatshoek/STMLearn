from typing import Tuple, Iterable
from util.transitioncover import get_state_cover_set
from equivalencecheckers.equivalencechecker import EquivalenceChecker
from suls.dfa import DFA
from suls.mealymachine import MealyMachine, MealyState
from suls.sul import SUL
from typing import Union
from itertools import product, chain
from pathlib import Path
from shutil import rmtree
from afl.util import decode_afl_file, strip_invalid, trim
import pickle


class AFLEquivalenceChecker(EquivalenceChecker):
    def __init__(self, sul: SUL, exec_path,
                 afl_out_dir="/tmp/afl/output",
                 parse_bin_path="../afl/parse"):

        super().__init__(sul)
        self.afl_out_dir = afl_out_dir
        self.sul_alphabet = [str(x) for x in sul.get_alphabet()]
        self.parse_bin_path = parse_bin_path
        self.exec_path = exec_path
        self.try_minimizing = set()
        self.testcase_cache = {}

        # Keep track of file names for access sequences [maps state names to id for file names]
        self.state_id = {}


    def _get_testcases(self, type="queue"):
        #h4x
        #if Path('tmpstorage').exists():
        #   self.testcase_cache = pickle.load(open('tmpstorage', 'rb'))

        testcases = []
        paths = [x for x in Path(self.afl_out_dir).glob('**/id:*') if x.match(f'**/{type}/**') and not x.match('**/leaner*/**')]
        for path in paths:
            if path in self.testcase_cache:
                testcases.append((path, self.testcase_cache[path]))
            else:
                if path in self.try_minimizing:
                    testcase = decode_afl_file(path.absolute(), self.parse_bin_path, self.exec_path, minimize=True)
                else:
                    testcase = decode_afl_file(path.absolute(), self.parse_bin_path, self.exec_path)

                if len(testcase) > 0:
                    stripped = strip_invalid(testcase, self.sul_alphabet)
                    trimmed = trim(stripped, self.sul)
                    testcases.append((path, trimmed))
                    self.testcase_cache[path] = trimmed

        #pickle.dump(self.testcase_cache, open('tmpstorage', 'wb'))

        return testcases

    def _update_afl_queue(self, fsm: Union[DFA, MealyMachine]):
        # Make sure we have a folder to put our stuff in
        queuepath = Path(self.afl_out_dir).joinpath('learner01/queue')
        queuepath.mkdir(exist_ok=True, parents=True)

        state_cover = get_state_cover_set(fsm)
        for acc_seq in state_cover:
            fsm.reset()
            fsm.process_input(acc_seq)
            statename = fsm.state.name

            if statename in self.state_id:
                filename = self.state_id[statename]
            else:
                filename = f'id:{statename.rjust(6, "0")}'
                self.state_id[statename] = filename

            with open(queuepath.joinpath(filename), 'w') as file:
                for a in acc_seq:
                    file.write(f'{a} ')
                file.write('0 \n')


    def test_equivalence(self, fsm: Union[DFA, MealyMachine]) -> Tuple[bool, Iterable]:
        self._update_afl_queue(fsm)

        crashes = self._get_testcases('crashes')
        # queries = self._get_testcases('queue')

        def test_queries(queries):
            for path, query in queries:
                #print("testing", query)
                if self.sul.process_input(query) == "invalid_input":
                    print("NO CRASH:", path)
                    self.try_minimizing.add(path)
                equivalent, counterexample = self._are_equivalent(fsm, query)
                if not equivalent:
                    return equivalent, counterexample
            return True, None

        print("[Info] testing crashing afl queries")

        equivalent, counterexample = test_queries(crashes)
        if not equivalent:
            return equivalent, tuple(counterexample)
        #
        # print("[Info] testing normal afl queries")
        # equivalent, counterexample = test_queries(queries)
        # if not equivalent:
        #     return equivalent, tuple(counterexample)

        return True, None