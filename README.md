# STMLearn

STMLearn is a python library which implements several active state machine learning algorithms.
This library is currently under active development, and things may change at any time. If you want to use this for anything important right now you would probably be better off with [LearnLib](https://github.com/LearnLib/learnlib)  :)

### Learning algorithms:
at the moment L* and TTT are supported for DFAs and Mealy machines.

| Algorithm | DFA | Mealy machine |
| ---       | :---: | :---:           |
| L*        | ✔️ | ✔ |️
| TTT       | ✔️ | ✔ |

### Equivalence checking methods:

The following equivalence checking methods are available, or will be soon:

- [x] W-method
- [ ] Smart W-method (early stopping etc.)
- [x] Random walk
- [x] Brute force

### Simple example:
```python
# Set up a SUL using regex
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
```
For the SUL described by the regular expression `(bb)*(aa)*(bb)*` the following dfa is learned:
![simple dfa](https://i.imgur.com/vlqQcCH.png)



