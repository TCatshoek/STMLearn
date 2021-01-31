from abc import ABC, abstractmethod
from stmlearn.teachers import Teacher
from stmlearn.suls import SUL


class Learner(ABC):
    def __init__(self, teacher: Teacher):
        self.teacher = teacher

    @abstractmethod
    def run(self) -> SUL:
        pass
