
from abc import ABCMeta, abstractmethod


class Module(metaclass=ABCMeta):
    @abstractmethod
    def __call__(self):
        pass

    def get_input_artifacts(self):
        pass

    def get_output_artifacts(self):
        pass
