import yaml
import os
from mergedb.data_types.declaration import Declaration
from mergedb.merge_functions.dict import deep_merge
from mergedb.errors import *
from jinja2 import Template


class Directory(object):

    def __init__(self, directory_path: str, inherited_config: dict = None, database=None):
        self.path = directory_path
        if inherited_config:
            self.inherited_config = inherited_config
        else:
            self.inherited_config = {}
        self.files = os.listdir(self.path)
        self.dir_config = self.get_dir_config()
        self.config = self.set_config()
        self.directories = {}
        self.declarations = {}
        self.database = database
        if self.database:
            self.load_directories()
            self.load_declarations()

    def load_directories(self):
        for file in self.files:
            path = f"{self.path}/{file}"
            if os.path.isdir(path):
                # try:
                    self.directories.update({file: Directory(path,
                                                             inherited_config=self.config,
                                                             database=self.database)})
                # except MdbLoadError as e:
                #     print(f"Skipped loading {path}: {e}")

    def load_declarations(self):
        for file in self.files:
            path = f"{self.path}/{file}"
            if os.path.isfile(path):
                if '.yml' in file or '.yaml' in file:
                    if 'mdb.' not in file and 'dir.' not in file:
                        base_config = self.load_declaration_file(path)
                        declaration = Declaration(path,
                                                  base_config,
                                                  inherited_config=self.config,
                                                  database=self.database)
                        self.declarations.update({file: declaration})
                        self.database.save_declaration(path, declaration)
                        if 'build' in self.config:
                            if file in self.config['build']:
                                self.database.add_to_build_list(declaration)

    @staticmethod
    def load_declaration_file(path):
        with open(path) as file:
            try:
                raw_text = file.read()
                templated = Template(raw_text).render()
                declaration_yaml = yaml.safe_load(templated)
                return declaration_yaml
            except Exception as e:
                raise MdbLoadError(msg=f"Could not load {path}: {e}")

    def set_config(self):
        return deep_merge(self.dir_config, self.inherited_config)

    def get_dir_config(self):
        if 'dir.yaml' in self.files:
            filename = 'dir.yaml'
        elif 'dir.yml' in self.files:
            filename = 'dir.yml'
        elif 'mdb.yml' in self.files or 'mdb.yaml' in self.files:
            return {}
        else:
            raise MdbLoadError(msg=f"Tried to load directory {self.path}, but it lacks a dir.yaml file")
        with open(self.path + '/' + filename) as file:
            try:
                data = yaml.safe_load(file.read())
                if data is not None:
                    return data
                else:
                    return {}
            except Exception as e:
                raise MdbLoadError(msg=f"Could not load directory {self.path}: {e}")