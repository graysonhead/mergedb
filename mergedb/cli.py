import argparse
import mergedb
from mergedb.data_types.database import Database
import pprint
import sys
import json
import yaml

dump_noalias = yaml.dumper.SafeDumper
dump_noalias.ignore_aliases = lambda self, data: True

pp = pprint.PrettyPrinter(indent=4)


class Cli:

    def __init__(self):
        parser = self.get_args()
        self.config = parser.parse_args()
        if self.config.version:
            self.print_version()

        if self.config.database_path:
            self.database = Database(self.config.database_path)
            if self.config.function == 'build':
                if not self.config.target:
                    print(self.format_dict(self.database.build()))
                else:
                    print(self.format_dict(self.database.build(target=self.config.target)))
            if self.config.function == 'detail':
                self.database.build()
                if not self.config.target:
                    print("Detail function requires a target")
                else:
                    if self.config.target:
                        target = list(filter(lambda x: x.short_name == self.config.target, self.database.declarations_to_build))
                        if target.__len__() < 1:
                            print(f"Could not find built declaration '{self.config.target}'")
                            sys.exit(1)
                        target[0].print_history()
            if self.config.function == 'config':
                self.database.build()
                print(self.format_dict(self.database.config))
        elif not self.config.version:
            parser.print_help()

    def format_dict(self, output: dict):
        if self.config.output == 'yaml':
            return yaml.dump(output, default_flow_style=False, Dumper=dump_noalias)
        elif self.config.output == 'json':
            return json.dumps(output)
        elif self.config.output == 'pprint':
            return pprint.pprint(output)

    @staticmethod
    def get_args():
        parser = argparse.ArgumentParser(
            description="MergeDB is a yaml hierarchical database that allows for customizable merging and inheritance "
                        "patterns."
        )
        parser.add_argument(
            'database_path',
            type=str,
            default=None,
            nargs='?',
            help="Location of the database, root directory must contain an 'mdb.yaml' file."
        )
        parser.add_argument(
            'function',
            type=str,
            default=None,
            nargs='?',
            help="What action you want to perform. Options: [ build, merge_detail ]"
        )
        parser.add_argument(
            'target',
            type=str,
            default=None,
            nargs='?',
            help="Allows you to target a build reference when performing an action. Must be included with "
                 "[ merge_detail ]"
        )
        parser.add_argument(
            '--output',
            type=str,
            default='yaml',
            help="Select the output type, defaults to 'yaml'"
                 "[ yaml, json, pprint ]"
        )
        parser.add_argument('--version', action='store_true')
        return parser

    @staticmethod
    def print_version():
        print(mergedb.__version__)
