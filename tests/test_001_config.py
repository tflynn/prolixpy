import unittest

import os
from os import path
import json

import standard_logger
from prolix.config import Config
from tests.base_test_class import BaseTestClass


class TestConfig(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Do this manually to avoid instancing Conf by instancing BaseTestClass
        if not BaseTestClass.TEST_LOGGER:
            BaseTestClass.TEST_LOGGER = standard_logger.get_logger('tests', level_str='DEBUG', console=True)
        cls.logger = BaseTestClass.TEST_LOGGER

    def write_file(self, file_path, contents):
        if path.exists(file_path):
            os.remove(file_path)
        with open(file_path, 'w') as f:
            f.write(contents)

    def find_temp_dir(self):
        temp_dir = None
        if 'TMP' in os.environ:
            if path.exists(os.environ['TMP']):
                temp_dir = os.environ['TMP']
        if not temp_dir and 'TEMP' in os.environ:
            if path.exists(os.environ['TEMP']):
                temp_dir = os.environ['TEMP']
        if not temp_dir:
            tmp_dir_home = "{0}/tmp".format(os.environ['HOME'])
            if not path.exists(tmp_dir_home):
                os.mkdir(tmp_dir_home)
            temp_dir = tmp_dir_home

        return temp_dir

    def write_file_to_tmp_dir(self, file_name, contents):
        temp_dir = self.find_temp_dir()
        file_path = path.normpath(path.join(temp_dir, file_name))
        self.write_file(file_path, contents)
        return file_path

    def test_001_load_single_config_file(self):
        self.logger.debug("TestConfig: test_001_load_single_config_file")
        # Always use an explicit new conf object
        conf = Config.new_conf(logger=self.logger)

        test_conf_file_name = "test_config.json"
        test_data = { "key1":"value1" }
        test_config_file_contents = json.dumps(test_data)
        test_conf_file_path = self.write_file_to_tmp_dir(test_conf_file_name, test_config_file_contents)

        # Set up conf object
        conf.use_default_sym_names = False
        conf.set_conf_name(test_conf_file_name)
        conf.add_search_path(test_conf_file_path)
        conf.expand_search_paths()

        full_search_paths = conf.full_search_paths
        # Only search path should be the one we added
        self.assertEqual(test_conf_file_path,full_search_paths[0])

        loaded_data = conf.get_data()
        # Clean up
        os.remove(test_conf_file_path)
        self.assertEqual(loaded_data, test_data)

    def test_002_load_multiple_config_files(self):
        self.logger.debug("TestConfig: test_002_load_multiple_config_files")
        # Always use an explicit new conf object
        conf = Config.new_conf(logger=self.logger)

        test_conf_file_name = "prolix_conf.json"
        test_data = { "key1":"value1" }
        test_config_file_contents = json.dumps(test_data)
        test_conf_file_path = self.write_file_to_tmp_dir(test_conf_file_name, test_config_file_contents)

        # Set up conf object - search paths are ordered
        conf.use_default_sym_names = False
        conf.add_sym_name('package')
        conf.add_sym_name('unknown_sym_name')
        conf.add_search_path(test_conf_file_path)
        conf.expand_search_paths()

        full_search_paths = conf.full_search_paths
        self.assertEqual(len(full_search_paths),3)
        # Only search path that can be tested here is the test_conf_file_path
        self.assertEqual(test_conf_file_path,full_search_paths[2])

        loaded_data = conf.get_data()
        # Clean up
        os.remove(test_conf_file_path)
        self.assertEqual(loaded_data["key1"], "value1")
        self.assertTrue("default_store_expiration_secs" in loaded_data)

    def test_003_load_config_file_from_env(self):
        self.logger.debug("TestConfig: test_003_load_config_file_from_env")
        # Always use an explicit new conf object
        conf = Config.new_conf(logger=self.logger)

        test_conf_file_name = "test_config.json"
        test_data = { "key1":"value1" }
        test_config_file_contents = json.dumps(test_data)
        test_conf_file_path = self.write_file_to_tmp_dir(test_conf_file_name, test_config_file_contents)

        # Set up conf object - search paths are ordered
        conf.use_default_sym_names = False
        os.environ['PROLIX_CONF_DIR'] = path.dirname(test_conf_file_path)
        os.environ['PROLIX_CONF'] = test_conf_file_name
        conf.add_sym_name('env')
        conf.expand_search_paths()

        full_search_paths = conf.full_search_paths
        self.assertEqual(len(full_search_paths),1)
        # Only search path that can be tested here is the test_conf_file_path
        self.assertEqual(test_conf_file_path,full_search_paths[0])

        loaded_data = conf.get_data()
        # Clean up
        del os.environ['PROLIX_CONF_DIR']
        del os.environ['PROLIX_CONF']
        os.remove(test_conf_file_path)
        self.assertEqual(loaded_data["key1"], "value1")
