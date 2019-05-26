import argparse
import mergedb
from mergedb.data_types.database import Database
import pprint

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
                pp.pprint(self.database.build())
        elif not self.config.version:
            parser.print_help()


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
        parser.add_argument('--version', action='store_true')
        return parser

    @staticmethod
    def print_version():
        print(mergedb.__version__)
