from stmlearn.equivalencecheckers._stackedchecker import StackedChecker, Sequential
from stmlearn.equivalencecheckers import EquivalenceChecker, WmethodEquivalenceChecker
from pathlib import Path
from stmlearn.util import Logger
from datetime import datetime

from stmlearn.util._savehypothesis import savehypothesis


class MATExperiment:
    def __init__(self, learner, teacher):
        self.teacher = teacher
        self.learner = learner(self.teacher)
        self.logger = Logger()
        self.run_kwargs = {}

    def run(self, *args, **kwargs):
        cur_kwargs = {**kwargs, **self.run_kwargs}
        hyp = self.learner.run(*args, **cur_kwargs)
        return hyp

    def enable_logging(self, log_dir, name, log_interval=60, write_on_change=None):
        # Enable logfile logging
        if write_on_change is None:
            write_on_change = set()

        now = datetime.now().strftime('%Y-%m-%d_%H:%M:%S')

        log_dir = Path(log_dir).joinpath(name).joinpath(now)
        log_dir.mkdir(exist_ok=True, parents=True)
        log_path = log_dir.joinpath("log.txt")

        self.logger.set_log_path(log_path)
        self.logger.set_log_interval(log_interval)
        self.logger.set_write_on_change(write_on_change)

        # Enable hypothesis logging
        self.run_kwargs['on_hypothesis'] = savehypothesis(log_dir.joinpath(f'hypotheses'))



if __name__ == "__main__":
    from stmlearn.learners import LStarMealyLearner
    from stmlearn.suls import MealyState, MealyMachine
    from stmlearn.teachers import Teacher

    # Set up an example mealy machine
    s1 = MealyState('1')
    s2 = MealyState('2')
    s3 = MealyState('3')

    s1.add_edge('a', 'nice', s2)
    s1.add_edge('b', 'B', s1)
    s2.add_edge('a', 'nice', s3)
    s2.add_edge('b', 'back', s1)
    s3.add_edge('a', 'A', s3)
    s3.add_edge('b', 'back', s1)

    mm = MealyMachine(s1)

    experiment = MATExperiment(
        learner=LStarMealyLearner,
        teacher=Teacher(
            sul=mm,
            eqc=Sequential(
                WmethodEquivalenceChecker,
                WmethodEquivalenceChecker,
            )
        )
    )

    experiment.enable_logging(
        log_dir="logs",
        name="test"
    )

    hyp = experiment.run()