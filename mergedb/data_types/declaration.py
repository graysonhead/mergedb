import difflib
from colorama import Fore, Back, Style, init
import yaml
from mergedb.merge_functions.dict import deep_merge, simple_merge
from mergedb.merge_functions.merge_controller import DeepMergeController, KeyedArrayMergeRule
from mergedb.errors import MdbDeclarationError
init()


class Declaration(object):

    def __init__(self,
                 layer_path,
                 base_declaration,
                 inherited_declarations: list = None,
                 inherited_config: dict = None,
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
        if inherited_declarations:
            self.inherited = inherited_declarations
        else:
            self.inherited = []
        if inherited_config:
            self.inherited_config = inherited_config
        else:
            self.inherited_config = {}
        self.merge_history = []
        self.merge_rules = []
        self.config = self.set_config()
        self.load_merge_rules()
        self.merge_controller = self.load_merge_controller()

    def __repr__(self):
        return f"<Declaration: {self.short_name.split('.')[0]}>"

    def get_name(self):
        """
        Strips the extension off of the name and returns it.

        :return:
            Short name of the dictionary without file extension
        """
        return self.short_name.split('.')[0]

    def load_merge_controller(self):
        if 'knockout' in self.config:
            knockout = self.config['knockout']
        else:
            knockout = None
        return DeepMergeController(list_merge_rules=self.merge_rules, knockout=knockout)

    def load_merge_rules(self):
        if 'merge_rules' in self.config:
            if 'keyed_array' in self.config['merge_rules']:
                for rule_config in self.config['merge_rules']['keyed_array']:
                    if 'path' in rule_config:
                        path = rule_config['path']
                    else:
                        path=[]
                    if 'attribute' not in rule_config or 'key' not in rule_config:
                        raise MdbDeclarationError(msg=f"['path', 'attribute'] are required for keyed_array merge rules")
                    rule = KeyedArrayMergeRule(path, rule_config['attribute'], rule_config['key'])
                    self.merge_rules.append(rule)

    def load_inherited_from_config(self):
        if 'inherit' in self.config:
            for path in self.config['inherit']:
                try:
                    self.inherited.append(self.database.load_declaration(path))
                except MdbDeclarationError as e:
                    raise MdbDeclarationError(f"{self.layer_path} tried to load inherited layer {path}, but was unable: {e}")

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
        # Todo: Implement a callback system and get this merge_history appending BS out of this method
        current = {}
        if self.inherited:
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
                    current = self.merge_controller.merge(current, declaration.base)
                    post_lines = yaml.safe_dump(current).split('\n')
                    for line in difflib.ndiff(current_lines, post_lines):
                        self.merge_history.append(self._colorize_diff(line))
        self.merge_history.append(f"{Fore.BLUE}Merge Layer {self.layer_path}:{Fore.RESET}")
        self.merge_history.append("====================================")
        current_lines = yaml.safe_dump(current).split('\n')
        post = self.merge_controller.merge(current, self.base)
        post_lines = yaml.safe_dump(post).split('\n')
        for line in difflib.ndiff(current_lines, post_lines):
            self.merge_history.append(self._colorize_diff(line))
        self.merge_history.append("Final Result")
        self.merge_history.append("====================================")
        self.merge_history.append(yaml.safe_dump(post))
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