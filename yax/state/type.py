
class Type:
    pass


class Artifact(Type):
    pass


class Parameter(Type):

    def __init__(self, key, value):
        self.key = key
        self.value = value

    def _validate_(self):
        pass

    def validate(self):
        try:
            return self._validate_()
        except Exception:
            return False
