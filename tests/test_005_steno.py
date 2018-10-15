import unittest

from tests.base_test_class import BaseTestClass

from prolix import steno


class TestSteno(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.logger = BaseTestClass.get_logger()
        cls.steno = steno.Steno(logger=cls.logger)

    def test_001_test_obfuscate_and_clarify(self):
        self.logger.debug("TestSteno: test_001_test_obfuscate_and_clarify")
        clear_text = "Mary had a little lamb"

        results = self.steno.obscure(text=clear_text, expiration_secs=30)
        if results['success']:
            self.logger.debug("TestSteno.test_001_test_obfuscate_and_clarify obscure succeeded")
            settings_key = results['key']
            obscured_text = results['obscured_text']

            results = self.steno.clarify(key=settings_key, text=obscured_text)
            if results['success']:
                self.logger.debug("TestSteno.test_001_test_obfuscate_and_clarify clarify succeeded")
                clarified_text = results['clarified_text']
                self.assertEqual(clear_text, clarified_text)
            else:
                self.logger.debug("TestSteno.test_001_test_obfuscate_and_clarify clarify failed")
                self.logger.error("TestSteno.test_001_test_obfuscate_and_clarify clarify errors {0)".format(results['errors']))
                self.assertEqual(results['success'], False)
        else:
            self.logger.error("TestSteno.test_001_test_obfuscate_and_clarify obscure failed")
            self.logger.error("TestSteno.test_001_test_obfuscate_and_clarify obscure errors {0)".format(results['errors']))
            self.assertEqual(results['success'], False)
