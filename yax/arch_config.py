from yax.state.exe import ExeGraph, ExeNode

from yax.modules.example.module import main as example_main

pipeline = ExeGraph()

pipeline.add(ExeNode('example', example_main),
             requires=(), returns=('a', 'b'))

pipeline.add(ExeNode('other', other_main),
             requires=('a'), returns=('x'))

 pipeline.add(ExeNode('foo', other_main),
              requires=('b', 'x'), returns=('z'))
