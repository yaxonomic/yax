from .base import Type
import os.path


class Parameter(Type):

    def from_string(self, string):
        return string

    def validate(self, string):
        try:
            self.from_string(string)
        except Exception:
            return False
        return True


class Int(Parameter):

    def from_string(self, string):
        return int(string)


class Float(Parameter):

    def from_string(self, string):
        return float(string)


class File(Parameter):
    def validate(self, string):
        return os.path.isfile(string)


class Directory(Parameter):
    def validate(self, string):
        return os.path.isdir(string)


class Str(Parameter):
    pass
