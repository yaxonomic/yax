import unittest
import tempfile
import os

from yax.util import get_data_path
from yax.state.jones import Indiana


class TestIndiana(unittest.TestCase):
    def setUp(self):
        self._yax_dir = tempfile.TemporaryDirectory()
        self.yax_dir = self._yax_dir.name
        self.arch_config_fp = get_data_path('arch_config.py',
                                            subfolder='test_pipeline')

    def tearDown(self):
        self._yax_dir.cleanup()

    def test_init(self):
        indiana = Indiana(self.yax_dir, pipeline=self.arch_config_fp)
        yax = os.path.join(self.yax_dir, '.yax')

        self.assertTrue(os.path.exists(yax))
        with open(self.arch_config_fp) as fh1:
            with open(os.path.join(yax, 'arch_config.py')) as fh2:
                self.assertEqual(fh1.read(), fh2.read())

        with self.assertRaises(ValueError):
            Indiana(self.yax_dir, pipeline=self.arch_config_fp)

        indiana.init('test_run')

        self.assertTrue(os.path.exists(os.path.join(self.yax_dir,
                                                    'test_run.ini')))


if __name__ == "__main__":
    unittest.main()
