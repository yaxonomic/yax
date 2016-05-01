import unittest
import os
from yax.state.type.parameter import Int, Float, File, Directory, \
    Str


class TestParameters(unittest.TestCase):

    def test_int(self):
        self.assertEqual(Int().from_string("1"), 1)
        self.assertEqual(Int().from_string("-1"), -1)
        self.assertEqual(Int().from_string("0"), 0)
        self.assertEqual(Int().from_string("385038345"), 385038345)
        with self.assertRaises(ValueError):
            Int().from_string("395.98")
        with self.assertRaises(ValueError):
            Int().from_string("test")

    def test_float(self):
        self.assertEqual(Float().from_string("1.305329"), 1.305329)
        self.assertEqual(Float().from_string("-920.48205"), -920.48205)
        self.assertEqual(Float().from_string(".40285"), 0.40285)
        self.assertEqual(Float().from_string("39127"), 39127.0)
        with self.assertRaises(ValueError):
            Int().from_string("test")

    def test_file(self):
        fp = os.path.realpath(__file__)
        directory = os.path.dirname(fp)
        self.assertEqual(File().from_string(fp), fp)
        with self.assertRaises(ValueError):
            File().from_string("/test/none_existent_file.stuff")
        with self.assertRaises(ValueError):
            File().from_string(directory)
        with self.assertRaises(ValueError):
            File().from_string("test")
        with self.assertRaises(ValueError):
            File().from_string(492)
        with self.assertRaises(TypeError):
            File().from_string(0.4028)

    def test_directory(self):
        fp = os.path.realpath(__file__)
        directory = os.path.dirname(fp)
        self.assertEqual(Directory().from_string(directory), directory)
        with self.assertRaises(ValueError):
            Directory().from_string("/not/a/real/directory/")
        with self.assertRaises(ValueError):
            Directory().from_string(fp)
        with self.assertRaises(ValueError):
            Directory().from_string("test")
        with self.assertRaises(ValueError):
            Directory().from_string(2094)
        with self.assertRaises(TypeError):
            Directory().from_string(0.4724)

    def test_str(self):
        self.assertEqual(Str().from_string("test string"), "test string")

if __name__ == '__main__':
    unittest.main()
