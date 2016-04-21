from yax.state.exe import ExeGraph, ExeNode
from yax.state.type import Str, Int, Float

from yax.state.tests.test_pipeline.modules.module_1 import main as main_1
from yax.state.tests.test_pipeline.modules.module_2 import main as main_2
from yax.state.tests.test_pipeline.modules.module_3 import main as main_3
from yax.state.tests.test_pipeline.modules.module_4 import main as main_4

pipeline = ExeGraph()

pipeline.set_details({
    'some_detail': (Str, "foo"),
    'other_detail': Int,
    'too_much_detail': (Float, float('inf'))
})

pipeline.add(ExeNode('module1', main_1,
                     output=('a', 'b')))

pipeline.add(ExeNode('module2', main_2,
                     output=('c', 'x')))

pipeline.add(ExeNode('module3', main_3,
                     input={'b': 'art_b',
                            'c': 'art_c'},
                     output='d'))

pipeline.add(ExeNode('module4', main_4,
                     input={'a': 'art_a',
                            'd': 'art_d'},
                     output='y'))
