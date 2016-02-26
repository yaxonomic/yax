import unittest

from yax.state.module import Module


class TestModule(unittest.TestCase):

    def test_subclass_fails_without_call(self):
        class MyModule(Module):
            pass

        with self.assertRaises(TypeError):
            MyModule()
