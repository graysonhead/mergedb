from mergedb.data_types.directory import Directory
from mergedb.merge_functions.merge_controller import DeepMergeController
from mergedb.errors import MdbLoadError
import yaml
import os


class Database(object):

    def __init__(self, database_root_path: str, default_settings: dict = None):
        self.root = None
        self.path = database_root_path
        self.files = os.listdir(database_root_path)
        self.declarations = {}
        self.declarations_to_build = []

        if 'mdb.yaml' in self.files:
            database_config_path = f"{database_root_path}/mdb.yaml"
        elif 'mdb.yml' in self.files:
            database_config_path = f"{database_root_path}/mdb.yml"
        else:
            raise MdbLoadError(msg=f"Could not find a mdb.yaml in {database_root_path}")
        with open(database_config_path) as file:
            try:
                config = yaml.safe_load(file.read())
                if config:
                    self.config = config
                else:
                    self.config = {}
            except Exception as e:
                raise MdbLoadError(msg=f"Failed to load {database_config_path}: {e}")
        # Merge any program specified default_settings in with the imported ones
        merger = DeepMergeController()
        if not default_settings:
            default_settings = {}
        self.config = merger.merge(self.config, default_settings)

    def build(self):
        self.load_database()
        result = {}
        for declaration in self.declarations_to_build:
            declaration.load_inherited_from_config()
            res = declaration.merge_inherited()
            result.update({declaration.get_name(): res})
        return result

    def load_database(self):
        self.root = Directory(self.path, database=self, inherited_config=self.config)

    def save_declaration(self, path, declaration):
        self.declarations.update({path: declaration})

    def add_to_build_list(self, declaration):
        self.declarations_to_build.append(declaration)

    def load_declaration(self, path):
        for key, value in self.declarations.items():
            if path in key:
                return value
        raise MdbLoadError(msg=f"Could not find declaration {path}")
