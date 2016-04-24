import unittest
import tempfile
import os
import configparser


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

    def test_prepare(self):
        indiana = Indiana(self.yax_dir, pipeline=self.arch_config_fp)
        with tempfile.NamedTemporaryFile(mode='w', dir=self.yax_dir,
                                         suffix='.ini') as fh:
            config = configparser.ConfigParser()
            config.read(get_data_path('test_run.ini'))
            config['module3']['input_file'] = self.arch_config_fp
            config['module4']['input_dir'] = self.yax_dir
            config.write(fh)
            fh.flush()
            indiana.prepare(fh.name[:-4])

if __name__ == "__main__":
    unittest.main()
