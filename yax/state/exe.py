import collections
import importlib.util

from yax.state.type import Artifact
from yax.state.type.parameter import Parameter


class ExeNode:
    def __init__(self, name, module):
        self.ancestors = []
        self.decendants = []
        self.name = name
        self.module = module
        self._annotations = self.module.__annotations__.copy()

    def __repr__(self):
        return "<ExeNode: %r at 0x%x>" % (self.name, id(self))

    def get_input_params(self):
        return {k: v for k, v in self._annotations.items()
                if k != 'return' and issubclass(v, Parameter)}

    def get_input_artifacts(self):
        return {k: v for k, v in self._annotations.items()
                if k != 'return' and  issubclass(v, Artifact)}

    def get_output_artifacts(self):
        return self._annotations['return']


class ExeGraph:
    @classmethod
    def from_config(cls, fp):
        # TODO: understand this better
        spec = importlib.util.spec_from_file_location("arch_config", fp)
        arch_config = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(arch_config)
        return arch_config.pipeline

    def __init__(self):
        self.output_from_node = collections.OrderedDict()
        self.nodes_from_input = collections.OrderedDict()
        self.start_nodes = []
        self.final_nodes = []

    def add(self, exe_node, requires=(), returns=()):
        if not requires:
            self.start_nodes.append(exe_node)
        for edge in requires:
            if edge not in self.nodes_from_input:
                self.nodes_from_input[edge] = []
            self.nodes_from_input[edge].append(exe_node)

        self.output_from_node[exe_node] = list(returns)

    @property
    def adjacency_matrix(self):
        graph = collections.OrderedDict(
            (node, []) for node in self.output_from_node)

        for node, next_nodes in graph.items():
            for edge in self.output_from_node[node]:

                if edge in self.nodes_from_input:
                    for decendant in self.nodes_from_input[edge]:

                        if decendant not in next_nodes:
                            next_nodes.append(decendant)
        return graph

    def __iter__(self):
        elements = []
        graph = self.adjacency_matrix

        starts = list(self.start_nodes)

        while starts:
            node_n = starts.pop()
            yield node_n

            edges = graph[node_n]
            while edges:
                node_m = edges.pop()
                should_insert = True
                for out_degree in graph.values():
                    if node_m in out_degree:
                        should_insert = False
                if should_insert:
                    starts.append(node_m)
