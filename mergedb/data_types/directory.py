import yaml
import os
from mergedb.data_types.declaration import Declaration
from mergedb.merge_functions.deep_merge import deep_merge
from mergedb.errors import *


class Directory(object):

    def __init__(self, directory_path: str, inherited_config: dict = {}):
        self.path = directory_path
        self.inherited_config = inherited_config
        self.files = os.listdir(self.path)
        self.dir_config = self.get_dir_config()
        self.config = self.set_config()
        self.directories = {}
        self.declarations = {}
        self.load_directories()
        self.load_declarations()

    def load_directories(self):
        for file in self.files:
            path = f"{self.path}/{file}"
            if os.path.isdir(path):
                self.directories.update({file: Directory(path)})

    def load_declarations(self):
        for file in self.files:
            path = f"{self.path}/{file}"
            if os.path.isfile(path):
                if '.yml' in file or '.yaml' in file:
                    self.declarations.update({file: Declaration(file,
                                                                path,
                                                                inherited_config=self.config)})

    def set_config(self):
        base_config = {}
        if 'mergedb' in self.dir_config:
            base_config = self.dir_config['mergedb']
        return deep_merge(base_config, self.inherited_config)

    def get_dir_config(self):
        if 'dir.yaml' in self.files:
            filename = 'dir.yaml'
        elif 'dir.yml' in self.files:
            filename = 'dir.yml'
        else:
            raise MdbLoadError(f"Tried to load directory {self.path}, but it lacks a dir.yaml file")
        with open(self.path + '/' + filename) as file:
            try:
                return yaml.safe_load(file.read())
            except Exception as e:
                raise MdbLoadError(f"Could not load directory {self.path}: {e}")
