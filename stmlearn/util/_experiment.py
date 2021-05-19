
from pathlib import Path
from stmlearn.util import Logger, CounterexampleTracker
from stmlearn.util._savehypothesis import savehypothesis
from datetime import datetime
import sys
import threading
import _thread
import os
import signal
import time


class MATExperiment:
    def __init__(self, learner, teacher):
        self.teacher = teacher
        self.learner = learner(self.teacher)
        self.logger = Logger()
        self.run_kwargs = {}
        self.ct_tracker = None

    def run(self, *args, **kwargs):
        cur_kwargs = {**kwargs, **self.run_kwargs}
        hyp = self.learner.run(*args, **cur_kwargs)
        return hyp

    def enable_ct_tracking(self):
        self.ct_tracker = CounterexampleTracker()
        self.ct_tracker.reset()
        self.teacher.eqc.onCounterexample(lambda ce: self.ct_tracker.add(ce))

    def enable_logging(self, log_dir, name, log_interval=60, write_on_change=None):
        # Enable logfile logging
        if write_on_change is None:
            write_on_change = set()

        now = datetime.now().strftime('%Y-%m-%d_%H:%M:%S')

        log_dir = Path(log_dir).joinpath(name).joinpath(now)
        log_dir.mkdir(exist_ok=True, parents=True)
        log_path = log_dir.joinpath("log.txt")

        self.logger.reset()
        self.logger.set_log_path(log_path)
        self.logger.set_log_interval(log_interval)
        self.logger.set_write_on_change(write_on_change)

        # Enable hypothesis logging
        self.run_kwargs['on_hypothesis'] = savehypothesis(log_dir.joinpath(f'hypotheses'))

    def set_timeout(self, timeout):
        def quit():
            time.sleep(timeout)
            print("Timeout reached")
            os.kill(os.getpid(), signal.SIGUSR1)

        # Set a custom signal handler in the main thread to handle a clean shutdown
        signal.signal(signal.SIGUSR1, lambda a, b: sys.exit())
        thr = threading.Thread(target=quit, daemon=True)
        thr.start()