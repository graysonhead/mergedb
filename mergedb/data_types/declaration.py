import difflib
from colorama import Fore, Back, Style, init
import yaml
from mergedb.merge_functions import deep_merge, simple_merge
from mergedb.errors import MdbLoadError
init()


class Declaration(object):

    def __init__(self,
                 layer_path,
                 base_declaration,
                 inherited_declarations: list=[],
                 inherited_config: dict={},
                 database=None):
        """
        A declaration instance contains a base_declaration (any declaration for which a build is specified), all of the
        layers it inherits, and any configuration that is inherited from a higher up object.

        :param layer_path:
            File path that the declaration was loaded from

        :param base_declaration:
            The declaration dict that the merge is performed on

        :param inherited_declarations:
            Any other layers that this declaration inherits

        :param inherited_config:
            If mergedb config options are specified on an inherited object, they are passed here (and will be overridden
            by what is found in the base_declaration, if present.)
        """
        self.database = database
        self.layer_path = layer_path
        self.short_name = layer_path.split("/")[-1]
        self.base = base_declaration
        self.inherited = inherited_declarations
        self.inherited_config = inherited_config
        self.merge_history = []
        self.config = self.set_config()

    def load_inherited_from_config(self):
        if 'inherit' in self.config:
            for path in self.config['inherit']:
                try:
                    self.inherited.append(self.database.load_declaration(path))
                except MdbLoadError as e:
                    raise MdbLoadError(f"{self.layer_path} tried to load inherited layer {path}, but was unable: {e}")

    def set_config(self):
        """
        This method deep merges the inherited config into the base config, if present

        :return:
            The merged config dict
        """
        base_config = {}
        if 'mergedb' in self.base:
            base_config = self.base['mergedb']
            # Remove the mergedb key from base if present
            del(self.base['mergedb'])
        return deep_merge(self.inherited_config, base_config)

    def merge_inherited(self):
        """
        This method performs a top-down merge from self.inherited down to self.base in the manner prescribed by the
        config.

        :return:
            The merged dict
        """
        # Clear the history in case someone is importing and calling this method more than once
        self.merge_history = []

        # What kind of merge are we doing?
        if getattr(self.config, 'merge_type', 'deep_merge') == 'deep_merge':
            merge_method = deep_merge
        elif getattr(self.config, 'merge_type', 'deep_merge') == 'simple_merge':
            merge_method = simple_merge

        # Is it going to support knockouts?
        if getattr(self.config, 'knockout', True):
            knockout = True
        else:
            knockout = False

        # Are we using an alternate knockout string?
        if getattr(self.config, 'knockout_string', None) and knockout:
            knockout_string = getattr(self.config, 'knockout_string')
        elif knockout and getattr(self.config, 'knockout_string', None) is None:
            knockout_string = '~'
        else:
            knockout_string = None

        # Sanity check(s)
        if knockout_string and merge_method == simple_merge:
            raise MdbLoadError(msg="Merge method is simple_merge but knockout is also True, which is not supported.")

        if self.inherited:
            current = {}
            for declaration in self.inherited:
                if not current:
                    self.merge_history.append(f"{Fore.BLUE}Initial Layer {declaration.layer_path}:{Fore.RESET}")
                    self.merge_history.append("====================================")
                    self.merge_history.append(yaml.dump(declaration.base))
                    current = declaration.base
                else:
                    self.merge_history.append(f"{Fore.BLUE}Merge Layer {declaration.layer_path}:{Fore.RESET}")
                    self.merge_history.append("====================================")
                    current_lines = yaml.safe_dump(current).split('\n')
                    current = merge_method(current, declaration.base, knockout=knockout_string)
                    post_lines = yaml.safe_dump(current).split('\n')
                    for line in difflib.ndiff(current_lines, post_lines):
                        self.merge_history.append(self._colorize_diff(line))
            self.merge_history.append(f"{Fore.BLUE}Merge Layer {self.layer_path}:{Fore.RESET}")
            self.merge_history.append("====================================")
            current_lines = yaml.safe_dump(current).split('\n')
            post = merge_method(current, self.base, knockout=knockout_string)
            post_lines = yaml.safe_dump(post).split('\n')
            for line in difflib.ndiff(current_lines, post_lines):
                self.merge_history.append(self._colorize_diff(line))
            return post

    @staticmethod
    def _colorize_diff(line):
        """
        Diff output is run through this method one line at a time in order to colorize it for context

        :param line:
            One line of diff output

        :return:
            One line of diff output, possibly wrapped in color
        """
        if line.startswith('+'):
            return Fore.GREEN + line + Fore.RESET
        elif line.startswith('-'):
            return Fore.RED + line + Fore.RESET
        elif line.startswith('^') or line.startswith('?'):
            return Fore.CYAN + line + Fore.RESET
        else:
            return line

    def print_history(self):
        """
        Prints self.merge_history to stdout
        """
        for line in self.merge_history:
            print(line)