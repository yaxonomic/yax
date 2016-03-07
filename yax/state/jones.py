from yax.arch_config import pipeline
from yax.state.exe import ExeGraph, ExeNode


class Indiana:
    def __init__(self):
        self.graph = ExeGraph()
        for name, main in pipeline:
            node = ExeNode(name, main)
            self.graph.append(node)

    def __repr__(self):
        return '\n'.join([repr(node) for node in self.graph])
