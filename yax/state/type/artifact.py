from .base import Type

import os


class Artifact(Type):

    def _get_complete_flag_path(self):
        os.path.join(self.data_dir, '.complete')

    @property
    def is_complete(self):
        return os.isfile(self._get_complete_flag_path())

    def __init__(self, dir_):
        self.data_dir = dir_
        if not self.is_complete:
            self.setup()

    def setup(self):
        pass

    def complete(self):
        os.utime(self._get_complete_flag_path(), None)
