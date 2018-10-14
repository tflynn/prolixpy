import sys
import os
from os import path
import json
from collections import deque
import standard_logger

PACKAGE_DIR = path.dirname(__file__)


class Config:
    """Find and load JSON configuration files"""

    COMMON_CONFIG = None

    @classmethod
    def conf(cls, logger=None):
        """
        Get the common configuration object

        :return: common Config object
        :rtype: Config
        """
        if not cls.COMMON_CONFIG:
            cls.COMMON_CONFIG = Config(logger=logger)
        return cls.COMMON_CONFIG

    @classmethod
    def new_conf(cls, logger=None):
        """
        Get a new config object

        :return: new Config object
        :rtype: Config
        """
        return Config(logger=logger)

    def __init__(self, logger=None):
        self.search_paths = []
        self.full_search_paths = []
        self.loaded_search_paths = []
        self.config_name = 'prolix_conf.json'
        self.default_sym_names = ['package', 'home', 'env']
        self.sym_names = []
        self.conf_data = {}
        self.env_conf_dir_name = "PROLIX_CONF_DIR"
        self.env_conf_name = "PROLIX_CONF"
        self.package_dir = PACKAGE_DIR
        self.loaded = False
        self.logger = logger if logger else standard_logger.get_logger('Config', level_str="DEBUG")

    def get_data(self):
        """
        Get the configured data. Will load the data if needed.

        :return:  Loaded data
        :rtype: dict
        """
        if self.is_loaded():
            self.logger.debug("Config.get_data data is already loaded")
        else:
            self.logger.debug("Config.get_data data is not yet loaded so load it")
            self.load_all_data()

        return self.conf_data

    def is_loaded(self):
        """
        Have the configurations been loaded?

        :return: True if loaded, False otherwise
        :rtype: boolean
        """
        return self.loaded

    def set_package_dir(self, package_dir):
        """
        Set the (relative) path to be used to satisfy symbolic 'package' path references

        'package dir' is typically generated at the top of a file
        using something similar to 'PACKAGE_DIR = path.dirname(__file__)'

        :param str package_dir: Fully qualified package dir
        :return: Current config object
        :rtype: Config
        """
        self.package_dir = package_dir
        return self

    def add_search_path(self, dir_or_path):
        """
        Add a fully-qualified directory or a fully-qualified path to the search path

        :param str dir_or_path: Fully-qualified directory or path
        :return: Current config object
        :rtype: Config
        """
        self.search_paths.append(dir_or_path)
        return self

    def get_search_paths(self):
        """
        Get search paths

        :return: Search paths
        :rtype: list(str)
        """
        return self.search_paths

    def get_full_search_paths(self):
        """
        Get fully qualified search paths

        :return: Fully qualified search paths
        :rtype: list(str)
        """
        return self.full_search_paths

    def get_loaded_search_paths(self):
        """
        Get the search paths that were actually loaded

        :return: Loaded search paths
        :rtype: list(str)
        """
        return self.loaded_search_paths

    def conf_name(self, config_name):
        """
        Set the name of the configuration file.

        :param str config_name: Configuration file name. Defaults to 'config.json'
        :return: Current config object
        :rtype: Config
        """
        self.config_name = config_name
        return self

    def get_conf_name(self):
        """
        Get the effective configuration file name. Allow for environment override.

        :return: Configuration file name
        :rtype: str
        """
        if self.env_conf_name in os.environ:
            self.config_name = os.environ[self.env_conf_name]

        self.config_name = path.normpath(self.config_name)
        return self.config_name

    def sym_name(self, sym_name):
        """
        Add a symbolic name to the search path

        :param str sym_name: Symbolic name. See default_sym_names
        :return: Current config object
        :rtype: Config
        """
        self.search_paths.append(sym_name)
        return self

    def default_sym_names(self):
        """
        Get default symbolic names

        :return: List of default symbolic names
        :rtype: list(str)
        """
        return self.default_sym_names

    def set_env_conf_dir_name(self, env_var_name):
        """
        Set the name of the environment variable that contains an additional directory to search

        :param str env_var_name: Environment variable name
        :return: Current config object
        :rtype: Config
        """
        self.env_conf_dir_name = env_var_name
        return self

    def expand_search_paths(self):
        """
        Expand the search paths to fully qualified file paths.

        The default symbolic names are added to the end of the list if not already present

        :return: List of fully qualified search paths
        :rtype: list(str)
        """
        # Only load once
        if self.is_loaded():
            self.logger("Config.expand_search_paths have already been expanded, so don't do it again")
            return self.full_search_paths

        # Append default symbolic names without duplicates
        for default_sym_name in self.default_sym_names:
            if default_sym_name not in self.search_paths:
                self.search_paths.append(default_sym_name)

        self.logger.debug("Config.expand_search_paths search paths {0}".format(self.search_paths))

        # Expand any unqualified paths and symbolic names - maintain order
        expanded_search_paths = deque()
        for search_path in self.search_paths:
            expanded_search_path = None
            if search_path in self.default_sym_names:
                if search_path == 'package':
                    expanded_search_path = self.package_dir
                elif search_path == 'home':
                    expanded_search_path = os.environ['HOME']
                elif search_path == 'env':
                    if self.env_conf_dir_name in os.environ:
                        expanded_search_path = os.environ[self.env_conf_dir_name]
                    else:
                        expanded_search_path = None
                else:
                    pass
            elif self.package_dir and not search_path.startswith('/'):
                expanded_search_path = path.join(self.package_dir, search_path)
            else:
                pass

            if expanded_search_path:
                # Add config name to any path that doesn't already have it
                config_name = self.get_conf_name()
                if not expanded_search_path.endswith(config_name):
                    expanded_search_path = path.join(expanded_search_path, config_name)

                expanded_search_paths.append(path.normpath(expanded_search_path))

        self.full_search_paths = list(expanded_search_paths)
        self.logger.debug("Config.expand_search_paths full search paths {0}".format(self.full_search_paths))
        return self.full_search_paths

    def load_all_data(self):
        """
        Load all the config files in order. Duplicate settings in latest file wins.

        :return: Loaded data
        :rtype: dict
        """

        # Only load once
        if self.is_loaded():
            self.logger.debug("Config.load_all_data data has been loaded, so don't do it again")
            return self.conf_data

        # Generate proper search paths
        self.expand_search_paths()

        for full_search_path in self.full_search_paths:
            if path.exists(full_search_path):
                with open(full_search_path) as cf:
                    conf_json_str = cf.read()
                    conf_json = json.loads(conf_json_str)
                    self.conf_data.update(conf_json)
                    self.loaded_search_paths.append(full_search_path)

        self.loaded = True
        self.logger.debug("Config.load_all_data loaded search paths {0}".format(self.loaded_search_paths))
        self.logger.debug("Config.load_all_data data has been loaded {0}".format(self.conf_data))
        return self.conf_data


if __name__ == '__main__':
    conf = Config.conf()
    print(conf.get_data())
    print(conf.get_data())

