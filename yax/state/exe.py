from yax.state.type import Artifact
from yax.state.type.parameter import Parameter


class ExeNode:
    def __init__(self, name, module):
        self.name = name
        self.module = module
        self._annotations = self.module.__annotations__.copy()

        if 'output' not in self._annotations:
            raise TypeError("Must include `output` as a parameter for a "
                            "module's main function.")

    def __repr__(self):
        return ("%s \n\tArtifacts: %r\n\tParams: %r\n\tOut: %r"
                % (self.name, self._get_input_artifacts(),
                   self._get_input_params(),
                   self._get_output_artifacts()))

    def _get_input_params(self):
        return {k: v for k, v in self._annotations.items()
                if not k == 'output' and issubclass(v, Parameter)}

    def _get_input_artifacts(self):
        return {k: v for k, v in self._annotations.items()
                if not k == 'output' and issubclass(v, Artifact)}

    def _get_output_artifacts(self):
        return self._annotations['output']


class ExeGraph:
    def __init__(self):
        self.nodes = []

    def append(self, exe_node):
        self.nodes.append(exe_node)

    def __iter__(self):
        return iter(self.nodes)
