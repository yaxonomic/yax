import configparser
import os
import shutil

from yax.state.exe import ExeGraph
from yax.state.artifact_map import ArtifactMap


class Indiana:
    DATA_DIR_NAME = '.yax'
    ARCH_CONFIG_NAME = 'arch_config.py'
    ARTIFACT_DATABASE_NAME = 'artifacts.db'

    @property
    def data_dir(self):
        return os.path.join(self.root_dir, self.DATA_DIR_NAME)

    @property
    def arch_path(self):
        return os.path.join(self.data_dir, self.ARCH_CONFIG_NAME)

    @property
    def artifact_db_path(self):
        return os.path.join(self.data_dir, self.ARTIFACT_DATABASE_NAME)

    def __init__(self, dir_, pipeline=None):
        self.root_dir = dir_
        if not os.path.isdir(self.data_dir):
            self._init_first_time(pipeline)
        elif pipeline is not None:
            raise ValueError("'pipeline' was provided to an already"
                             " initialized yax pipeline.")

        self.graph = ExeGraph.from_config(self.arch_path)
        self.map = ArtifactMap(self.artifact_db_path, self.graph)

    def _init_first_time(self, pipeline):
        if pipeline is None:
            pipeline = self._get_default_pipeline()
        else:
            pipeline = os.path.abspath(pipeline)
        try:
            os.mkdir(self.data_dir)
            os.mkdir(os.path.join(self.data_dir, 'artifacts'))
            os.mkdir(os.path.join(self.data_dir, 'working'))
            shutil.copyfile(pipeline, self.arch_path)
        except Exception:
            shutil.rmtree(self.data_dir)
            raise

    def _get_default_pipeline(self):
        root, _ = os.path.split(os.path.split(__file__)[0])
        # This is the arch_config module of YAX not ARCH_CONFIG_NAME
        # DRY does not apply here.
        return os.path.join(root, 'arch_config.py')

    def __repr__(self):
        return '\n'.join([repr(node) for node in self.graph])

    def init(self, run_key):
        self.write_config(run_key)

    def prepare(self, config):
        raise NotImplementedError("To be done.")

    def engage(self, config):
        self.prepare(self, config)
        raise NotImplementedError("To be done.")

    def read_config(self, fp):
        raise NotImplementedError("To be done.")

    def write_config(self, run_key):
        fp = os.path.join(self.root_dir, '%s.ini' % run_key)
        config = configparser.ConfigParser()

        config['GLOBAL'] = {
            'run_key': run_key
        }

        for node in self.graph:
            config[node.name] = {key: '' for key in node.get_input_params()}

        with open(fp, mode='w') as fh:
            config.write(fh)
