import configparser
import os
import shutil
import tempfile

from yax.state.exe import ExeGraph
from yax.state.artifact_map import ArtifactMap
from yax.state.type import Artifact


class Indiana:
    DATA_DIR_NAME = '.yax'
    ARCH_CONFIG_NAME = 'arch_config.py'
    ARTIFACT_DATABASE_NAME = 'artifacts.db'

    @property
    def data_dir(self):
        return os.path.join(self.root_dir, self.DATA_DIR_NAME)

    @property
    def artifacts_dir(self):
        return os.path.join(self.data_dir, 'artifacts')

    @property
    def working_dir(self):
        return os.path.join(self.data_dir, 'working')

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
        self.map = ArtifactMap(self.artifacts_dir, self.artifact_db_path,
                               self.graph)

    def _init_first_time(self, pipeline):
        if pipeline is None:
            pipeline = self._get_default_pipeline()
        else:
            pipeline = os.path.abspath(pipeline)
        try:
            os.mkdir(self.data_dir)
            os.mkdir(self.artifacts_dir)
            os.mkdir(self.working_dir)
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

    def prepare(self, run_key):
        """Prepare a run

        Looks for a file in the root directory which matches `run_key`.ini
        The config will be validated and then any corresponding aritfacts
        will be associated or declared with a run.

        Paramters
        ---------
        run_key : str
            The run key to use

        Returns
        -------
        None

        """
        config = os.path.join(self.root_dir, run_key + '.ini')
        if not os.path.isfile(config):
            raise ValueError("File `%s.ini` does not exist." % run_key)

        config = self.read_config(config)
        run_id, existing_run_key = self.map.create_run(config)
        self.map.declare_artifacts(config, run_id)
        return existing_run_key

    def engage(self, run_key):
        run_id = self.map.resolve_run_key(run_key)
        art_fps = self.map.get_artifact_paths(run_id)

        for node in self.graph:
            if all([Artifact.declare(art_fps[o], None)
                    for o in node.output_map]):
                continue
            self._affect_module_call(node, run_id, art_fps)

        for name, art_fp in art_fps.items():
            artifact = Artifact.declare(art_fp, None)
            if artifact.is_final_output():
                shutil.copytree(artifact.data_dir,
                                os.path.join(self.root_dir, run_key, name))

    def _affect_module_call(self, node, run_id, art_fps):
        details = self.map.get_details(run_id)

        outputs = []
        for key, cls in zip(node.output_map, node.get_output_artifacts()):
            outputs.append(cls.declare(art_fps[key], node.name))
        outputs = tuple(outputs)

        param_to_class = node.get_input_artifacts()
        input_artifacts = {}
        for key, param in node.input_map.items():
            input_artifacts[param] = \
                param_to_class[param].declare(art_fps[key], node.name)

        input_params = self.map.get_params(run_id, node)

        with tempfile.TemporaryDirectory(dir=self.working_dir) as working_dir:
            node(working_dir, outputs, details, input_artifacts, input_params)

    def read_config(self, config_fp):
        config = configparser.ConfigParser()
        config.read(config_fp)
        # Verify all sections are preset
        config_sections_list = config.sections()
        config_sections = set(config_sections_list)
        if len(config_sections) != len(config_sections_list):
            raise ValueError("Duplicate sections %r found."
                             % set(x for x in config_sections_list
                                   if config_sections_list.count(x) > 1))
        exp_sections = set(n.name for n in self.graph) | set(['details'])
        if exp_sections != config_sections:
            if exp_sections - config_sections:
                raise ValueError("Missing sections %r in config."
                                 % (exp_sections - config_sections))
            elif config_sections - exp_sections:
                raise ValueError("Unused sections %r in config."
                                 % (config_sections - exp_sections))

        config_ = {'details': {'run_key': config['details']['run_key']}}
        for key, value in self.graph.details.items():
            type_ = value
            if type(value) is tuple:
                type_, _ = value
            self._copy_converted_config_value(type_, config['details'],
                                              config_['details'], key)

        for node in self.graph:
            config_[node.name] = self._validate_section(config[node.name],
                                                        node)
        return config_

    def _validate_section(self, section_config, node):
        # Verify all parameters are present
        config_params = set(section_config)
        if len(config_params) != len(section_config):
            raise ValueError("Duplicate paramters %r found in section %r."
                             % (set(x for x in section_config
                                    if section_config.count(x) > 1),
                                node.name))
        exp_params = set(node.get_input_params())
        if exp_params != config_params:
            if exp_params - config_params:
                raise ValueError("Missing paramters %r in section %r."
                                 % (exp_params - config_params, node.name))
            elif config_params - exp_params:
                raise ValueError("Missing paramters %r in section %r."
                                 % (config_params - exp_params, node.name))

        section = {}
        for key, type_ in node.get_input_params().items():
            self._copy_converted_config_value(type_, section_config, section,
                                              key)
        return section

    def write_config(self, run_key):
        fp = os.path.join(self.root_dir, '%s.ini' % run_key)
        config = configparser.ConfigParser()

        config['details'] = {}
        for key, value in self.graph.details.items():
            default = ''
            if type(value) is tuple:
                _, default = value
            config['details'][key] = str(default)
        config['details']['run_key'] = run_key
        for node in self.graph:
            section = {}
            for key in node.get_input_params():
                default = ''
                if key in node.defaults:
                    default = node.defaults[key]
                section[key] = default
            config[node.name] = section

        with open(fp, mode='w') as fh:
            config.write(fh)

    def _copy_converted_config_value(self, type_, from_, into, key):
        try:
            into[key] = type_().from_string(from_[key])
        except ValueError:
            raise ValueError("Field %r must be %s."
                             % (key, type_.__name__.lower()))
