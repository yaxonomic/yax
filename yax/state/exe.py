import collections

from yax.state.type import Artifact
from yax.state.type.parameter import Parameter


class ExeNode:
    def __init__(self, name, module):
        self.name = name
        self.module = module
        self._annotations = self.module.__annotations__.copy()

    def __repr__(self):
        return "NODE<%r>" % self.name
        # return ("%s \n\tArtifacts: %r\n\tParams: %r\n\tOut: %r"
        #         % (self.name, self.get_input_artifacts(),
        #            self.get_input_params(),
        #            self.get_output_artifacts()))

    def get_input_params(self):
        return {k: v for k, v in self._annotations.items()
                if issubclass(v, Parameter)}

    def get_input_artifacts(self):
        return {k: v for k, v in self._annotations.items()
                if issubclass(v, Artifact)}

    def get_output_artifacts(self):
        return self._annotations['return']


class ExeGraph:
    def __init__(self):
        self.edges_from_node = collections.OrderedDict()
        self.nodes_from_edge = collections.OrderedDict()

    def add(self, exe_node, requires=(), returns=()):
        for edge in requires:
            if edge not in self.nodes_from_edge:
                self.nodes_from_edge[edge] = []
            self.nodes_from_edge[edge].append(exe_node)

        self.edges_from_node[exe_node] = list(returns)

    @property
    def adjacency_matrix(self):
        graph = collections.OrderedDict(
            (node, []) for node in self.edges_from_node)

        for node, next_nodes in graph.items():
            for edge in self.edges_from_node[node]:

                if edge in self.nodes_from_edge:
                    for decendant in self.nodes_from_edge[edge]:

                        if decendant not in next_nodes:
                            next_nodes.append(decendant)
        return graph


    def __iter__(self):
        elements = []

        starts = []
        for ret_node in self.rets.values():
            if ret_node not in self.reqs:
                starts.append(ret_node)

        while starts:
            _, node, rets = starts.pop()
            elements.append(node)
            for ret in rets:
                requires, next_node, returns = self.rets[ret]
                # if not (set(requires) - set([ret])):
