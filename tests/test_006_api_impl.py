import unittest

from pyxutils import paths

from tests.base_test_class import BaseTestClass
from prolix import api_impl

class TestApiImpl(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.logger = BaseTestClass.get_logger()
        cls.api = api_impl.ApiImpl(logger=cls.logger)

        with open(paths.get_data_path(file_name='gettysburg.txt', package_name='prolix')) as f:
            cls.test_data = f.read()

    def test_001_test_obfuscate_and_clarify(self):
        self.logger.debug("TestApiImpl: test_001_test_obfuscate_and_clarify")
        clear_text = self.test_data

        results = self.api.obscure(text=clear_text, expiration_secs=30)
        if results['success']:
            self.logger.debug("TestApiImpl.test_001_test_obfuscate_and_clarify obscure succeeded")
            settings_key = results['key']
            obscured_text = results['obscured_text']

            #self.logger.debug("TestApiImpl.test_001_test_obfuscate_and_clarify obscured text")
            #self.logger.debug(obscured_text)

            results = self.api.clarify(key=settings_key, text=obscured_text)
            if results['success']:
                self.logger.debug("TestApiImpl.test_001_test_obfuscate_and_clarify clarify succeeded")
                clarified_text = results['clarified_text']
                #self.logger.debug("TestApiImpl.test_001_test_obfuscate_and_clarify clarified text")
                #self.logger.debug(clarified_text)
                self.assertEqual(clear_text, clarified_text)
            else:
                self.logger.debug("TestApiImpl.test_001_test_obfuscate_and_clarify clarify failed")
                self.logger.error("TestApiImpl.test_001_test_obfuscate_and_clarify clarify errors {0)".format(results['errors']))
                self.assertEqual(results['success'], False)
        else:
            self.logger.error("TestApiImpl.test_001_test_obfuscate_and_clarify obscure failed")
            self.logger.error("TestApiImpl.test_001_test_obfuscate_and_clarify obscure errors {0)".format(results['errors']))
            self.assertEqual(results['success'], False)
