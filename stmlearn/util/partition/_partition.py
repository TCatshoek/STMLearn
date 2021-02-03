# Port of https://gitlab.science.ru.nl/rick/partition/-/blob/master/partition.go
# All credits to Rick Smetsers

from __future__ import annotations
from copy import copy
from typing import Dict, List, Union, Callable
from queue import Queue
from dataclasses import dataclass
from bisect import bisect_left
from stmlearn.util.distinguishingset import check_distinguishing_set
from stmlearn.suls import MealyMachine, DFA


@dataclass
class Element:
    value: int
    block: int


@dataclass
class Block:
    begin: int
    end: int
    parent: int
    pivots: List[int]
    witness: Witness
    marks: List[List[int]]


@dataclass
class Witness:
    prefix: int
    suffix: Witness


# The output funtion first takes an input symbol, then a state label, and returns the output for that transition
class Partition:
    def __init__(self, n: int, degree: int, f_output: Dict[int, Dict[int, int]]):
        self.blocks: List[Block] = [Block(0, n, -1, None, None, [[] for _ in range(degree)])]

        self.size = 1
        self.degree = degree
        self.n_states = n

        self.indices: List[int] = [i for i in range(n)]
        self.elements: List[Element] = [Element(i, 0) for i in range(n)]

        self.splitters: 'Queue[int]' = Queue(maxsize=n)

        for prefix, cls in f_output.items():
            w = Witness(prefix, None)
            for b in self.getBlocks(0, n):
                parent = self.split(b, degree, cls, w)
                if parent >= 0:
                    self.splitters.put(parent)

    # The original code uses a goroutine for this, but this is python
    # and python hates multithreading so I'm not even gonna bother
    def getBlocks(self, begin: int, end: int) -> List[int]:
        ch = []

        n = len(self.elements)
        if end > n:
            end = n

        i = begin
        while i < end:
            b = self.elements[i].block
            i = self.blocks[b].end
            ch.append(b)

        return ch

    def getBlock(self, val: int) -> int:
        if val >= len(self.elements) or val < 0:
            return -1
        i = self.indices[val]
        return self.elements[i].block

    def index(self, val: int) -> int:
        return self.indices[val]

    def value(self, i: int) -> int:
        return self.elements[i].value

    def refineHopcroft(self, f_transition: Dict[int, Dict[int, int]]):
        n = len(self.elements)

        # Construct preimage for all functions
        preimages = [preimage(f, n) for f in f_transition.values()]

        # Refine until there are no groups of splitters left, or if all blocks are singletons
        done = False
        while (not self.splitters.empty()) and (not done):
            splitter = self.splitters.get()

            # Identify largest subblock of splitter.
            # The loop below does not check the last subblock of splitter;
            # therefore, we put it here.
            largest = len(self.blocks[splitter].pivots)
            delta = self.blocks[splitter].end - self.blocks[splitter].pivots[largest - 1]
            begin = self.blocks[splitter].begin
            for cls, pivot in enumerate(self.blocks[splitter].pivots):
                if pivot - begin > delta:
                    delta = pivot - begin
                    largest = cls
                begin = pivot

            for prefix, _ in f_transition.items():
                w = Witness(prefix, self.blocks[splitter].witness)

                # Mark the predecessors of all but the largest subblock of the splitter.
                # marks := make([]map[int][]int, len(p.blocks[splitter].pivots)+1)
                # marks[class][block] is a list of values in block whose successors are in the class-th child of the splitter
                count = [0] * len(self.blocks)
                # count[block] is the number of values in block that have been marked
                markblocks = []

                for cls in range(len(self.blocks[splitter].pivots) + 1):
                    if cls == largest:
                        continue

                    begin = self.blocks[splitter].begin
                    if cls != 0:
                        begin = self.blocks[splitter].pivots[cls - 1]

                    end = self.blocks[splitter].end
                    if cls != len(self.blocks[splitter].pivots):
                        end = self.blocks[splitter].pivots[cls]

                    for i in range(begin, end):
                        for val in preimages[prefix](self.value(i)):
                            b = self.getBlock(val)

                            if self.blocks[b].end - self.blocks[b].begin == 1:
                                # Singleton block cannot be split
                                continue

                            if count[b] == 0:
                                markblocks.append(b)

                            self.blocks[b].marks[cls].append(val)
                            count[b] += 1

                # Move the marked values to subblocks.
                for b in markblocks:
                    parent: int = 0
                    pos = self.blocks[b].end - count[b]
                    if pos == self.blocks[b].begin:
                        # the implicit child is empty
                        parent = b
                    else:
                        parent = len(self.blocks)
                        self.blocks.append(copy(self.blocks[b]))  # Gotcha, copy bug >_>
                        self.blocks[parent].pivots = [pos]

                        self.blocks[b].end = pos
                        self.blocks[b].parent = parent

                    first = True
                    for cls in range(len(self.blocks[splitter].pivots) + 1):

                        if cls == largest or self.blocks[b].marks[cls] is None or len(self.blocks[b].marks[cls]) == 0:
                            continue

                        if first:
                            first = False

                            if len(self.blocks[b].marks[cls]) == self.blocks[parent].end - self.blocks[parent].begin:
                                # Not a real split
                                self.blocks[b].marks[cls] = []
                                break

                            self.blocks[parent].witness = w
                            self.splitters.put(parent)

                            if pos > self.blocks[parent].begin:
                                self.size += 1

                        else:
                            # Apparently go automatically creates an array if you append to nil?
                            # What a headache lol
                            if self.blocks[parent].pivots is None:
                                self.blocks[parent].pivots = []
                            self.blocks[parent].pivots.append(pos)
                            self.size += 1

                        sb = len(self.blocks)
                        self.blocks.append(Block(pos, pos + len(self.blocks[b].marks[cls]), parent, None, None,
                                                 [[] for _ in range(self.degree)]))

                        # Swap the value at the current pos with val and increase pos
                        for val in self.blocks[b].marks[cls]:
                            i = self.index(val)
                            other = self.value(pos)
                            self.elements[pos] = Element(val, sb)
                            self.indices[val] = pos
                            self.elements[i].value = other
                            self.indices[other] = i
                            pos += 1

                        self.blocks[b].marks[cls] = []  # self.blocks[b].marks[cls][:0]

                if self.size == n:
                    done = True

    def refineMoore(self, f_transition: Dict[int, Dict[int, int]]):
        n = len(self.elements)
        done = False
        while (not self.splitters.empty()) and (not done):
            splitter = self.splitters.get()
            for prefix, f in f_transition.items():
                w = Witness(prefix, self.blocks[splitter].witness)
                for b in self.getBlocks(0, n):

                    # Figure out the range of the successors of elements in b.
                    begin = n
                    end = 0
                    for i in range(self.blocks[b].begin, self.blocks[b].end):
                        j = self.index(f[self.value(i)])
                        if j < begin:
                            begin = j
                        if j > end:
                            end = j

                    # If all successors of elements in b are in the splitgroup, try to split.
                    if begin >= self.blocks[splitter].begin and end <= self.blocks[splitter].end:

                        # class_func returns the index of the splitter in which the successor of e is.
                        def class_func(val: int) -> int:
                            x = self.index(f[val])
                            search_n = len(self.blocks[splitter].pivots)
                            # TODO: triple check this line, might be wrong
                            return bisect_left(
                                [(lambda i_: self.blocks[splitter].pivots[i_] > x)(i_) for i_ in range(search_n)],
                                True)

                        parent = self.split(b, len(self.blocks[splitter].pivots) + 1, class_func, w)
                        if parent >= 0:
                            self.splitters.put(parent)

                    if self.size == n:
                        done = True

    def split(self, b: int, degree: int,
              cls: Union[Dict[int, int], Callable[[int], int]],
              w: Witness) -> int:

        # Since cls can either be a dict or a function,
        # we wrap it to give it a consistent interface
        def cls_get(val: int) -> int:
            if isinstance(cls, dict):
                cls_r = cls[val]
            else:
                cls_r = cls(val)
            return cls_r

        parent = -1
        refinement: List[List[int]] = [[] for _ in range(degree)]

        begin = self.blocks[b].begin
        end = self.blocks[b].end

        for i in range(begin, end):
            val = self.elements[i].value
            cls_ = cls_get(val)
            refinement[cls_].append(val)

        # Apparently we are done if this is the case?
        if len(refinement[cls_get(self.elements[begin].value)]) == end - begin:
            # All elements have the same class. No moves are needed.
            return parent

        # A split has been made, so make a parent
        parent = len(self.blocks)
        self.blocks.append(Block(begin, end, self.blocks[b].parent, [], w, None))
        self.blocks[b].parent = parent

        # Construct subblocks and move elements to them.
        pos = begin
        first = True
        for cls_ in range(degree):
            if len(refinement[cls_]) == 0:
                continue

            sb = b

            if not first:  # Make a new block
                sb = len(self.blocks)
                self.blocks.append(
                    Block(pos, pos + len(refinement[cls_]), parent, None, None, [[] for _ in range(self.degree)]))
                self.blocks[parent].pivots.append(pos)
                self.size += 1
            else:  # Modify interval b == sb
                self.blocks[sb].end = pos + len(refinement[cls_])
                first = False

            for val in refinement[cls_]:
                self.elements[pos] = Element(val, sb)
                self.indices[val] = pos
                pos += 1

        return parent

    def getWitnesses(self) -> Dict[str, bool]:
        witnesses: Dict[str, bool] = dict()

        for block in self.blocks:
            cur_witness = tuple()
            w = block.witness
            while w is not None:
                cur_witness += (w.prefix,)
                w = w.suffix
            witnesses[cur_witness] = True

        return witnesses


def get_distinguishing_set(fsm: Union[MealyMachine, DFA], method="Hopcroft"):
    if isinstance(fsm, MealyMachine):
        alphabet = list(sorted(fsm.get_alphabet()))
        tmp = set(_do_partition(fsm, alphabet, method))
        tmp.remove(tuple())  # Meaningless in the case of a Mealy machine
    elif isinstance(fsm, DFA):
        # In the case of a DFA, we need to consider the empty string as part of the alphabet as well
        alphabet = list(sorted(fsm.get_alphabet()))
        alphabet = ['λ'] + alphabet
        tmp = set(_do_partition(fsm, alphabet, method))
        if ('λ',) in tmp:
            tmp.remove(('λ',))
        else:
            tmp.remove(tuple())
    else:
        raise NotImplementedError

    check_ok = check_distinguishing_set(fsm, tmp)
    assert check_ok, "If this goes wrong your fsm is probably not minimal"
    return tmp

def _do_partition(fsm: Union[MealyMachine, DFA], alphabet, method):
    states = sorted(fsm.get_states(), key=lambda x: int(x.name.strip('s')))

    # Map states to ints
    state_num_map = {state: num for num, state in enumerate(states)}

    # Map inputs to ints
    input_num_map = {inp: num for num, inp in enumerate(alphabet)}

    # Map outputs to ints
    # We do this as-we-go, is easier
    output_num_map = dict()

    # FOR DEBUGGING - get the same mapping as the go code
    # from stmlearn.util.distinguishingset._minsepseq import _run_distset
    # dset_go, mappings_go = _run_distset("/tmp/tmp4xl31c2w.gv", return_mappings=True)
    # output_num_map = {outp: int(num) for num, outp in mappings_go['Output'].items()}

    # Create transition and output functions
    t_func = dict()  # Maps inputs to maps of state -> next state
    o_func = dict()  # Maps inputs to maps of state -> output

    for inp in alphabet:
        t_func_sub = dict()  # The state -> next state map for the current input
        o_func_sub = dict()  # The state -> output map for the current input
        for state in states:

            if inp == 'λ' and isinstance(fsm, DFA): # Special case for DFAs
                next_state, output = state, state in fsm.accepting_states
            else:
                next_state, output = state.next(inp)

            cur_id = state_num_map[state]
            next_id = state_num_map[next_state]

            if output not in output_num_map:
                output_num_map[output] = len(output_num_map)
            output_id = output_num_map[output]

            o_func_sub[cur_id] = output_id
            t_func_sub[cur_id] = next_id

        inp_id = input_num_map[inp]
        t_func[inp_id] = t_func_sub
        o_func[inp_id] = o_func_sub

    # Construct the partition
    p = Partition(len(states), len(output_num_map), o_func)
    if method == "Hopcroft":
        p.refineHopcroft(t_func)
    elif method == "Moore":
        p.refineMoore(t_func)
    else:
        raise Exception("unknown minimization method")

    witnesses = p.getWitnesses()

    # Now we have to translate them back to the input alphabet
    num_input_map = {num: inp for inp, num in input_num_map.items()}
    translated_witnesses = []

    for witness in witnesses.keys():
        translated_witnesses.append(tuple([num_input_map[x] for x in witness]))

    return translated_witnesses


def preimage(f: Dict[int, int], n: int) -> Callable[[int], List[int]]:
    p = [[] for _ in range(n)]

    for i in range(n):
        j = f[i]
        p[j].append(i)

    def preimage_func(j: int) -> List[int]:
        return p[j]

    return preimage_func