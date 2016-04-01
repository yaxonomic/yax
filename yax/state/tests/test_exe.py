import unittest
import collections

from yax.state.exe import ExeGraph, ExeNode
from yax.state.type import Artifact


def in0out1(w, o) -> Artifact:
    pass


def in0out2(w, o) -> (Artifact, Artifact):
    pass


def in1out1(w, o, x: Artifact) -> Artifact:
    pass


def in2out1(w, o, x: Artifact, y: Artifact) -> Artifact:
    pass


class TestAdjacencyMatrix(unittest.TestCase):
    def test_empty(self):
        graph = ExeGraph()
        self.assertEqual(collections.OrderedDict(), graph.adjacency_matrix)

    def test_single(self):
        graph = ExeGraph()
        n1 = ExeNode('foo', in0out1, output='a')

        graph.add(n1)

        self.assertEqual(collections.OrderedDict([(n1, [])]),
                         graph.adjacency_matrix)

    def test_simple_chain(self):
        graph = ExeGraph()
        n1 = ExeNode('foo', in0out1, output='a')
        n2 = ExeNode('foh', in1out1, input={'a': 'x'}, output='b')
        n3 = ExeNode('fum', in1out1, input={'b': 'x'}, output='c')

        expected = collections.OrderedDict([
            (n1, [n2]),
            (n2, [n3]),
            (n3, [])
        ])

        graph.add(n1)
        graph.add(n2)
        graph.add(n3)

        self.assertEqual(expected, graph.adjacency_matrix)

    def test_diamond(self):
        graph = ExeGraph()
        n1 = ExeNode('fee', in0out2, output=('a', 'b'))
        n2 = ExeNode('fie', in1out1, input={'a': 'x'}, output='c')
        n3 = ExeNode('foh', in1out1, input={'b': 'x'}, output='d')
        n4 = ExeNode('fum', in2out1, input={'c': 'x', 'd': 'y'}, output='e')

        expected = collections.OrderedDict([
            (n1, [n2, n3]),
            (n2, [n4]),
            (n3, [n4]),
            (n4, [])
        ])

        graph.add(n1)
        graph.add(n2)
        graph.add(n3)
        graph.add(n4)
        self.assertEqual(expected, graph.adjacency_matrix)


if __name__ == '__main__':
    unittest.main()
