from .base import Type
import os.path


class Parameter(Type):
    def from_string(self, string):
        return string


class Int(Parameter):
    def from_string(self, string):
        return int(string)


class Float(Parameter):
    def from_string(self, string):
        return float(string)


class File(Parameter):
    def from_string(self, string):
        if not os.path.isfile(string):
            raise ValueError("")
        return os.path.abspath(string)


class Directory(Parameter):
    def from_string(self, string):
        if not os.path.isdir(string):
            raise ValueError("")
        return os.path.abspath(string)


class Str(Parameter):
    pass
