import sys
import random

import words


class RandomString:
    """Utility class for generating various random string values"""

    MIN_UTF8_CHAR_VALUE = 32
    MAX_UTF8_CHAR_VALUE = int(0x110000) - 1
    SECURE_RNG = random.SystemRandom()

    def secure_rng(self):
        """
        Get a secure RNG
        :return: Secure RNG instance
        :rtype: random.SystemRandom
        """
        return RandomString.SECURE_RNG

    def random_utf8_char(self, lower=None, upper=None):
        """
        Get a random UTF8 character

        :param int lower: (optional) lower limit for UTF8 character
        :param int upper: (optional) upper limit for UTF8 character
        :return: String with single UTF8 character or None if any error
        :rtype: str
        """
        try:
            lower = max(lower, RandomString.MIN_UTF8_CHAR_VALUE) if lower else RandomString.MIN_UTF8_CHAR_VALUE
            upper = min(upper, RandomString.MAX_UTF8_CHAR_VALUE) if upper else RandomString.MAX_UTF8_CHAR_VALUE
            return chr(self.secure_rng().randint(lower, upper))
        except Exception:
            return None

    def random_utf8_string(self, len=10, lower=None, upper=None):
        """
        Generate a UTF8 string of the specified length with random characters
        :param int len: (Optional) Length of the string defaults to 10
        :param int lower: (optional) lower limit for UTF8 character
        :param int upper: (optional) upper limit for UTF8 character
        :return: Random UTF8 string
        :rtype: str
        """
        rs = ""
        for i in range(1, len + 1):
            rc = self.random_utf8_char(lower=lower, upper=upper)
            if rc:
                rs = rs + rc

        return rs


class RandomInts:
    """Utility class for generating sets of random int values"""

    MAX_INT = sys.maxsize - 1
    MIN_INT = - MAX_INT
    SECURE_RNG = random.SystemRandom()

    def secure_rng(self):
        """
        Get a secure RNG
        :return: Secure RNG instance
        :rtype: random.SystemRandom
        """
        return RandomInts.SECURE_RNG

    def random_int(self, lower=None, upper=None):
        """
        Get a random int in the specified range

        :param int lower: Range lower bound
        :param int upper: Range upper bound
        :return: random int or None if any error
        :rtype: int
        """
        try:
            lower = max(lower, RandomInts.MIN_INT) if lower else RandomInts.MIN_INT
            upper = min(upper, RandomInts.MAX_INT) if upper else RandomInts.MAX_INT
            return self.secure_rng().randint(lower, upper)
        except Exception:
            return None

    def random_ints(self, len=10, lower=None, upper=None):
        """
        Get an array of random ints in the specified range

        :param int len: Number of ints in array
        :param int lower: Range lower bound
        :param int upper: Range upper bound
        :return: Array of random ints
        :rtype: [int]
        """
        rints = []
        for i in range(1, len + 1):
            rint = self.random_int(lower=lower, upper=upper)
            if rint:
                rints.append(rint)

        return rints


class RandValues:

    def __init__(self):

        self.word_dict = words.load_data(dataset='5000words')
        self.word_count = len(self.word_dict)
        self.rng = RandomInts()

    def random_kv(self, max_val_len=10, min_val_len=5):
        random_key = str(self.rng.random_int(lower=1, upper=self.word_count))
        random_word = self.word_dict[random_key]
        if len(random_word) > max_val_len or len(random_word) < min_val_len:
            random_key, random_word = self.random_kv(
                max_val_len=max_val_len, min_val_len=min_val_len)

        return random_key, random_word

    def random_vals(self, num=3, max_val_len=10, min_val_len=5):
        vals_list = []
        for i in range(0, num):
            kv = self.random_kv(max_val_len=max_val_len, min_val_len=min_val_len)
            vals_list.append(kv[1])

        return vals_list

    def random_password(self):
        elements = self.random_vals(num=3)
        num_element = '0000' + str(self.rng.random_int(lower=1, upper=9999))
        password = "{0}-{1}#-{2}-{3}".format(
            elements[0], num_element[-4:], elements[1], elements[2]
        )
        return password
