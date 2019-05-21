import difflib
from colorama import Fore, Back, Style, init
init()

import yaml
from mergedb.merge_functions import deep_merge, simple_merge
from mergedb.errors import MdbLoadError





class Declaration(object):

    def __init__(self, layer_name, base_declaration, inherited_declarations: list=[], inherited_config: dict={}):
        """
        A declaration instance contains a base_declaration (any declaration for which a build is specified), all of the
        layers it inherits, and any configuration that is inherited from a higher up object.

        :param layer_name:
            Usually the file name that the declaration was loaded from

        :param base_declaration:
            The declaration dict that the merge is performed on

        :param inherited_declarations:
            Any other layers that this declaration inherits

        :param inherited_config:
            If mergedb config options are specified on an inherited object, they are passed here (and will be overridden
            by what is found in the base_declaration, if present.)
        """
        self.layer_name = layer_name
        self.base = base_declaration
        self.inherited = inherited_declarations
        self.inherited_config = inherited_config
        self.merge_history = []
        self.config = self.set_config()

    def set_config(self):
        base_config = {}
        if 'mergedb' in self.base:
            base_config = self.base['mergedb']
        return deep_merge(base_config, self.inherited_config)

    def merge_inherited(self):
        # Clear the history in case someone is importing and calling this method more than once
        self.merge_history = []

        if getattr(self.config, 'merge_type', 'deep_merge') == 'deep_merge':
            merge_method = deep_merge
        elif getattr(self.config, 'merge_type', 'deep_merge') == 'simple_merge':
            merge_method = simple_merge

        if getattr(self.config, 'knockout', True):
            knockout = True
        else:
            knockout = False

        if getattr(self.config, 'knockout_string', None) and knockout:
            knockout_string = getattr(self.config, 'knockout_string')
        elif knockout and getattr(self.config, 'knockout_string', None) is None:
            knockout_string = '~'
        else:
            knockout_string = None

        if knockout_string and merge_method == simple_merge:
            raise MdbLoadError(msg="Merge method is simple_merge but knockout is also True, which is not supported.")

        if self.inherited:
            current = {}
            for declaration in self.inherited:
                if not current:
                    self.merge_history.append(f"{Fore.BLUE}Initial Layer {declaration.layer_name}:{Fore.RESET}")
                    self.merge_history.append(yaml.dump(declaration.base))
                    current = declaration.base
                else:
                    self.merge_history.append(f"{Fore.BLUE}Merge Layer {declaration.layer_name}:{Fore.RESET}")
                    current_lines = yaml.safe_dump(current).split('\n')
                    current = merge_method(current, declaration.base)
                    post_lines = yaml.safe_dump(current).split('\n')
                    for line in difflib.ndiff(current_lines, post_lines):
                        self.merge_history.append(self._colorize_diff(line))
            self.merge_history.append(f"{Fore.BLUE}Merge Layer {self.layer_name}:{Fore.RESET}")
            current_lines = yaml.safe_dump(current).split('\n')
            post = merge_method(self.base, current)
            post_lines = yaml.safe_dump(post).split('\n')
            for line in difflib.ndiff(current_lines, post_lines):
                self.merge_history.append(self._colorize_diff(line))
            return post

    def _colorize_diff(self, line):
        if line.startswith('+'):
            return Fore.GREEN + line + Fore.RESET
        elif line.startswith('-'):
            return Fore.RED + line + Fore.RESET
        elif line.startswith('^') or line.startswith('?'):
            return Fore.CYAN + line + Fore.RESET
        else:
            return line

    def print_history(self):
        for line in self.merge_history:
            print(line)