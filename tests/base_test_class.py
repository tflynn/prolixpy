import standard_logger
from prolix.config import Config

class BaseTestClass():

    BASE_CLASS_INSTANCE = None
    TEST_LOGGER = None

    def __init__(self):
        if not BaseTestClass.TEST_LOGGER:
            BaseTestClass.TEST_LOGGER = standard_logger.get_logger('tests', level_str='DEBUG')
        self.logger = BaseTestClass.TEST_LOGGER
        self.conf = Config.conf(logger=self.logger)

    @classmethod
    def get_logger(cls):
        if not cls.BASE_CLASS_INSTANCE:
            BASE_CLASS_INSTANCE = BaseTestClass()

        return BASE_CLASS_INSTANCE.logger
