import sys
import random
import standard_logger
import words


class CodePointRanges:
    """Legal code point ranges according to Unicode spec"""

    BIT_RANGES = [
        (7, 0x0000, 0x007F),
        (11, 0x0080, 0x0F77),
        (16, 0x0800, 0xFFFF),
        (21, 0x10000, 0x10FFF)
    ]

    # Problem in the BMP range (0xD000, 0xDFFF)
    BMP_RANGES = [
        (0x0000, 0xCFFF),
        (0xE000, 0xFFFF)
    ]

    SMP_RANGES = [
        (0x10000, 0x14FFF),
        (0x16000, 0x18FFF),
        (0x1B000, 0x1BFFF),
        (0x1D000, 0x1FFFF)
    ]

    # Limit ranges to BMP and SMP
    ALL_RANGES = BMP_RANGES + SMP_RANGES

    # @classmethod
    # def legal_cp_by_bit_size(cls, cp):
    #     """
    #     Check whether code point is legal based on bit size
    #
    #     :param int cp: Code point value
    #     :return: True if legal, False otherwise
    #     :rtype: bool
    #     """
    #     cp_bit_size = cp.bit_length()
    #     for bit_limits in cls.BIT_RANGES:
    #         max_bit_size = bit_limits[0]
    #         if cp_bit_size <= max_bit_size:
    #             min_cp = bit_limits[1]
    #             max_cp = bit_limits[2]
    #             if min_cp <= cp <= max_cp:
    #                 return True
    #
    #     return False

    @classmethod
    def legal_code_point(cls, possible_cp):
        for current_range in cls.ALL_RANGES:
            lower_limit = current_range[0]
            upper_limit = current_range[1]
            if lower_limit <= possible_cp <= upper_limit:
                return True

        return False


class RandomString:
    """Utility class for generating various random string values"""

    MIN_UTF8_CHAR_VALUE = 32
    # Limit to BMP + SMP - so max is '0x1FFFF'
    MAX_UTF8_CHAR_VALUE: int = 131071
    SECURE_RNG = random.SystemRandom()

    def __init__(self, logger=None):
        self.logger = logger if logger else standard_logger.get_logger("RandomString")

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
            lower = max(lower, self.MIN_UTF8_CHAR_VALUE) if lower else self.MIN_UTF8_CHAR_VALUE
            upper = min(upper, self.MAX_UTF8_CHAR_VALUE) if upper else self.MAX_UTF8_CHAR_VALUE
            while True:
                while True:
                    rand_int = self.secure_rng().randint(lower, upper)
                    if CodePointRanges.legal_code_point(rand_int):
                        break

                try:
                    rand_char = chr(rand_int)
                    rand_char.encode('UTF8')
                    break
                except UnicodeEncodeError:
                    self.logger.debug("random_utf8_char invalid code point {0} {1}".format(rand_int,hex(rand_int).upper()))
                    pass

            return rand_char

        except ValueError:
            return None

    def random_ascii_char(self):
        """
        Get a random ASCII char

        :return: String with single ASCII character or None if any error
        :rtype: str
        """
        return self.random_utf8_char(lower=33, upper=126)

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

    def random_ascii_string(self, len=10):
        """
        Get a random ASCII string
        :param int len: Length of string
        :return: ASCII string
        :rtype: str
        """
        return self.random_utf8_string(len=len, lower=33, upper=126)

    def is_ascii(self, s):
        """
        Test to see whether supplied string is ASCII
        :param str s: String to test
        :return: True if ASCII, False otherwise
        :rtype: bool
        """
        try:
            s.encode('ascii')
            return True
        except UnicodeEncodeError:
            return False


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
