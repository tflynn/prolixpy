import sys
import os
from os import path
import json
from collections import deque
import standard_logger

from prolix.paths import get_package_path


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
        self.use_default_sym_names = True
        self.default_sym_names = ['package', 'home', 'env']
        self.sym_names = []
        self.conf_data = {}
        self.env_conf_dir_name = "PROLIX_CONF_DIR"
        self.env_conf_name = "PROLIX_CONF"
        self.package_dir = get_package_path()
        self.loaded = False
        self.paths_expanded = False
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
        :rtype: bool
        """
        return self.loaded

    def are_paths_expanded(self):
        """
        Have the paths been expanded?

        :return: True if expanded, False otherwise
        :rtype: bool
        """
        return self.paths_expanded

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

    def set_conf_name(self, config_name):
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

    def add_sym_name(self, sym_name):
        """
        Add a symbolic name to the search path

        :param str sym_name: Symbolic name. See default_sym_names
        :return: Current config object
        :rtype: Config
        """
        self.search_paths.append(sym_name)
        return self

    def get_default_sym_names(self):
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

    def absolute_package_location(self, package_relative_path):
        """
        Find the absolute path for a package relative reference

        :param str package_relative_path: Package relative path e.g. prolix/prolix_conf.json
        :return: All matching paths that contain the file (in sys.path order)
        :rtype: list(str)
        """
        qualified_paths = []
        for sys_path in sys.path:
            if path.isabs(package_relative_path):
                qualified_path = package_relative_path
            else:
                qualified_path = path.normpath(path.join(
                    sys_path, package_relative_path
                ))
            if path.exists(qualified_path):
                if qualified_path not in qualified_paths:
                    qualified_paths.append(qualified_path)

        return qualified_paths

    def expand_search_paths(self):
        """
        Expand the search paths to fully qualified file paths.

        The default symbolic names are added to the end of the list if not already present

        :return: List of fully qualified search paths
        :rtype: list(str)
        """
        # Only load once
        if self.is_loaded():
            self.logger.debug("Config.expand_search_paths data is already loaded, so paths have already been expanded. Don't do it again")
            return self.full_search_paths

        # Only expand once
        if self.are_paths_expanded():
            self.logger.debug("Config.expand_search_paths have already been expanded, so don't do it again")
            return self.full_search_paths

        # Add in symbolic names
        if self.use_default_sym_names:
            # Append default symbolic names without duplicates
            for default_sym_name in self.get_default_sym_names():
                if default_sym_name not in self.search_paths:
                    self.search_paths.append(default_sym_name)

        self.search_paths.extend(self.sym_names)

        self.logger.debug("Config.expand_search_paths search paths {0}".format(self.search_paths))

        # Expand any unqualified paths and symbolic names - maintain order
        expanded_search_paths = []
        for search_path in self.search_paths:
            expanded_search_path = None
            if search_path == 'package':
                package_relative_name = path.join(self.package_dir, self.config_name)
                package_locations = self.absolute_package_location(package_relative_name)
                if package_locations:
                    expanded_search_path = package_locations[0]
                else:
                    expanded_search_path = self.package_dir
            elif search_path == 'home':
                expanded_search_path = os.environ['HOME']
            elif search_path == 'env':
                if self.env_conf_dir_name in os.environ:
                    expanded_search_path = os.environ[self.env_conf_dir_name]
            else:
                expanded_search_path = search_path

            # Qualify path with package directory if path is not absolute
            if expanded_search_path and self.package_dir and not path.isabs(expanded_search_path):
                expanded_search_path = path.join(self.package_dir, expanded_search_path)

            # Add config name to any path that doesn't already have it
            if expanded_search_path:
                config_name = self.get_conf_name()
                if not expanded_search_path.endswith(config_name):
                    expanded_search_path = path.join(expanded_search_path, config_name)

            # Normalize any path that's present
            if expanded_search_path:
                expanded_search_path = path.normpath(expanded_search_path)
                expanded_search_paths.append(expanded_search_path)

        self.full_search_paths = list(expanded_search_paths)
        self.logger.debug("Config.expand_search_paths full search paths {0}".format(self.full_search_paths))
        self.paths_expanded = True
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
