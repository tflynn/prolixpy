import standard_logger
from json_config import JsonConfig


class BaseTestClass():

    BASE_CLASS_INSTANCE = None
    TEST_LOGGER = None

    def __init__(self):
        if not BaseTestClass.TEST_LOGGER:
            BaseTestClass.TEST_LOGGER = standard_logger.get_logger('tests', level_str='DEBUG')
        self.logger = BaseTestClass.TEST_LOGGER
        self.conf = JsonConfig.conf(logger=self.logger, package_name='prolix')
        self.conf.config_name = 'prolix_conf.json'
        self.conf_data = self.conf.get_data()

    @classmethod
    def get_logger(cls):
        if not cls.BASE_CLASS_INSTANCE:
            BASE_CLASS_INSTANCE = BaseTestClass()

        return BASE_CLASS_INSTANCE.logger
