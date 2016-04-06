from yax.state.exe import ExeGraph, ExeNode

from yax.modules.example.module import main as example_main

pipeline = ExeGraph()

pipeline.add(ExeNode('example', example_main,
             output=('a', 'b')))
