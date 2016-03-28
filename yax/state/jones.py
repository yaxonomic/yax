import configparser
import os

from yax.arch_config import pipeline
from yax.state.exe import ExeGraph, ExeNode


class Indiana:
    data_dir = '.yax'

    @classmethod
    def get_data_path(cls, dir_):
        return os.path.join(dir_, cls._data_dir)

    @classmethod
    def prepare(cls, dir_, pipeline=pipeline):
        if not os.path.isdir():
            os.mkdir(self.data_path)

    def __init__(self, dir_):
        self.graph = ExeGraph()
        for name, main in pipeline:
            node = ExeNode(name, main)
            self.graph.append(node)

    def __repr__(self):
        return '\n'.join([repr(node) for node in self.graph])

    @property
    def is_initialized(self):
        return os.path.isdir(self.data_path)


    def init(self, fp):
        init_config(self, os.path.join(self.dir_, 'config_%s.ini' % run_name),
                    run)

    def prepare(self, fp):
        pass

    def engage(self, fp):
        self.prepare(self, fp)

    def init_config(self, fp, run_name):
        config = configparser.ConfigParser()

        config['GLOBAL'] = {
            'project_name': self.run_name
        }

        for node in self.graph:
            config[node.name] = {key: '' for key in node.get_input_params()}

        with open(fp, mode='w') as fh:
            config.write(fh)

    def read_config(self, fp):
        pass
