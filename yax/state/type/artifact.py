from .base import Type

import os


class Artifact(Type):
    final_user_output = False

    def _get_complete_flag_path(self):
        os.path.join(self.data_dir, '.complete')

    @property
    def is_complete(self):
        return os.isfile(self._get_complete_flag_path())

    @classmethod
    def declare(cls, dir_, id_):
        instance = cls.__new__()
        instance.data_dir = dir_
        instance.module_id = id_
        instance.__init__(completed=instance.is_complete)

    def __init__(self, completed):
        pass

    def complete(self):
        self.__complete__()
        os.utime(self._get_complete_flag_path(), None)

    def __complete__(self):
        pass
