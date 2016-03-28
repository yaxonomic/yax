import unittest
import collections

from yax.state.exe import ExeGraph, ExeNode
from yax.state.type import Artifact

def function(working_dir, output) -> Artifact:
    pass

class TestAdjacencyMatrix(unittest.TestCase):

    def test_empty(self):
        graph = ExeGraph()
        self.assertEqual(collections.OrderedDict(), graph.adjacency_matrix)

    def test_single(self):
        graph = ExeGraph()
        n1 = ExeNode('foo', function)

        graph.add(n1, requires=(), returns=('a'))

        self.assertEqual(collections.OrderedDict([(n1, [])]),
                         graph.adjacency_matrix)

    def test_simple_chain(self):
        graph = ExeGraph()
        n1 = ExeNode('foo', function)
        n2 = ExeNode('foh', function)
        n3 = ExeNode('fum', function)

        expected = collections.OrderedDict([
            (n1, [n2]),
            (n2, [n3]),
            (n3, [])
        ])

        graph.add(n1, requires=(), returns=('a'))
        graph.add(n2, requires=('a'), returns=('b'))
        graph.add(n3, requires=('b'), returns=('c'))

        self.assertEqual(expected, graph.adjacency_matrix)

    def test_diamond(self):
        graph = ExeGraph()
        n1 = ExeNode('fee', function)
        n2 = ExeNode('fie', function)
        n3 = ExeNode('foh', function)
        n4 = ExeNode('fum', function)

        expected = collections.OrderedDict([
            (n1, [n2, n3]),
            (n2, [n4]),
            (n3, [n4]),
            (n4, [])
        ])

        graph.add(n1, requires=(), returns=('a', 'b'))
        graph.add(n2, requires=('a'), returns=('c'))
        graph.add(n3, requires=('b'), returns=('d'))
        graph.add(n4, requires=('c', 'd'), returns=('e'))

        self.assertEqual(expected, graph.adjacency_matrix)


if __name__ == '__main__':
    unittest.main()
