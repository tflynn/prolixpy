import sys
import os
from os import path
import random
from collections import deque
import json

import standard_logger
import words

from pyutils import paths


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

    @classmethod
    def is_alpha_char_ascii(cls, char):
        """
        Check to see whether this character is ASCII alpha

        :param str char: Character (string) to check
        :return: True if character is ASCII alpha, False otherwise
        :rtype: bool
        """
        ord_val = ord(char)
        return (ord('A') <= ord_val <= ord('Z')) or (ord('a') <= ord_val <= ord('z'))



class RandomInts:
    """Utility class for generating sets of random int values"""

    MAX_INT = sys.maxsize - 1
    MIN_INT = - MAX_INT
    SECURE_RNG = random.SystemRandom()

    def __init__(self, logger=None):
        self.logger = logger if logger else standard_logger.get_logger("RandomInts")

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

    def __init__(self,logger=None):
        self.logger = logger if logger else standard_logger.get_logger("RandValues")
        self.word_dict = words.load_data(dataset='5000words', logger=self.logger)
        self.word_count = len(self.word_dict)
        self.rng = RandomInts(self.logger)

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


class RandomAsciiStringByFrequency:
    """Transform text using letter frequency data"""

    def __init__(self, *args, **kwargs):

        self.all_args = list(args)
        self.args = self.all_args

        self.cli = True if 'cli' in kwargs and kwargs['cli'] else False

        # Should be from config file
        self.frequency_file_name = 'frequencies-1.json'
        self.minimum_input_text_length = 4
        self.letter_randomizer_file_name = "letter_randomizer_ascii.json"
        self.min_padding_size = 8
        self.max_padding_size = 64

        self.logger = kwargs['logger'] if 'logger' in kwargs \
            else standard_logger.get_logger('randascii', level_str='DEBUG', console=True)

        # Define properties
        self.input_file_name = None
        self.input_data = None
        self.input_data_length = None
        self.frequency_data = None
        self.letters_by_frequency = None
        self.normalized_frequency_data = None
        self.lookup_letter_data = None
        self.lookup_letter_data_len = None
        self.secure_rng = random.SystemRandom()

    def dispatch(self):

        result = self.process_arguments()
        if not result['success']:
            return {"success": False, "error": result['error']}

        if not self.lookup_data_present():

            result = self.load_letter_frequencies()
            if not result['success']:
                return {"success": False, "error": result['error']}

            result = self.generate_lookup_data()
            if not result['success']:
                return {"success": False, "error": result['error']}

        result = self.load_lookup_data()
        if not result['success']:
            return {"success": False, "error": result['error']}

        result = self.load_input_file()
        if not result['success']:
            return {"success": False, "error": result['error']}

        return self

    def process_arguments(self):
        base_file_name = path.basename(__file__)
        if len(self.all_args) > 0:
            if self.all_args[0].endswith(base_file_name):
                self.args = self.all_args[1:]

        if self.cli:
            if len(self.args) < 1:
                error_text = "Usage: {0} <input file>".format(base_file_name)
                self.logger.error(error_text)
                return {"success": False, "error": error_text}
            else:
                self.input_file_name = self.args[0]
                return {"success": True}
        else:
            return {"success": True}

    def load_letter_frequencies(self):
        file_path = paths.get_data_path(file_name=self.frequency_file_name, package_name='prolix')
        with open(file_path, 'r') as f:
            self.frequency_data = json.loads(f.read().strip())

        self.letters_by_frequency = self.frequency_data["by_frequency"]
        return {"success": True}

    def load_input_file(self):

        if self.input_file_name:
            with open(self.input_file_name,'r') as f:
                self.input_data = f.read()

            self.input_data_length = len(self.input_data)
            if self.input_data_length < self.minimum_input_text_length:
                error_text = "Text too short. Must be at least {0} chars".format(
                    self.minimum_input_text_length)
                self.logger.error(error_text)
                return {"success": False, "error": error_text}

            # # For testing
            # self.input_data = "Twas brillig and the slithy toves"
            # self.input_data_length = len(self.input_data)

        return {"success": True}

    def lookup_data_present(self):
        file_path = paths.get_data_path(file_name=self.letter_randomizer_file_name, package_name='prolix')
        return path.exists(file_path)

    def load_lookup_data(self):
        file_path = paths.get_data_path(file_name=self.letter_randomizer_file_name, package_name='prolix')
        with open(file_path, 'r') as f:
            json_str = f.read()
        json_data = json.loads(json_str)
        self.lookup_letter_data = json_data['data']
        self.lookup_letter_data_len = len(self.lookup_letter_data)
        return {'success': True}

    def generate_lookup_data(self):
        # Generate modified frequency table
        normalized_frequency_data = []
        total_normalized_frequencies = 0
        for item in self.frequency_data["by_frequency"]:
            letter = item[0]
            original_frequency = item[1]
            normalized_frequency = round(float(original_frequency),3) * 1000
            if normalized_frequency < 1:
                normalized_frequency = 1
            normalized_frequency = int(normalized_frequency)
            total_normalized_frequencies += normalized_frequency
            normalized_frequency_data.append([letter,normalized_frequency])

        self.normalized_frequency_data = normalized_frequency_data

        letter_strings = deque()
        for item in normalized_frequency_data:
            letter = item[0]
            frequency = item[1]
            letter_string = letter * frequency
            letter_strings.append(letter_string)

        self.lookup_letter_data = "".join(letter_strings)
        lookup_letter_data_json = {
            'data': self.lookup_letter_data
        }
        with open(self.letter_randomizer_file_name,'w') as f:
            f.write(json.dumps(lookup_letter_data_json))

        return {"success": True}

    def random_char_by_freq(self):
        rand_offset = self.secure_rng.randint(0, self.lookup_letter_data_len - 1)
        return self.lookup_letter_data[rand_offset]

    def random_ascii_string_by_freq(self, len=20):
        random_string_q = deque()
        for i in range(0,len):
            random_string_q.append(self.random_char_by_freq())
        random_string = "".join(random_string_q)
        return random_string

    def obscure(self):
        obscured_text_q = deque()
        obscure_seq_q = deque()

        for i in range(0, self.input_data_length):
            current_char = self.input_data[i]
            if current_char == ' ':
                # If padding is of length 1, previous char was a space
                current_char = self.random_char_by_freq()
                padding_size = 1
                padding = self.random_char_by_freq()
            elif  current_char == "\n":
                # If padding is of length 2, previous char was a space
                current_char = self.random_char_by_freq()
                padding_size = 2
                padding = self.random_char_by_freq() + self.random_char_by_freq()
            else:
                padding_size = self.secure_rng.randint(self.min_padding_size, self.max_padding_size)
                padding = self.random_ascii_string_by_freq(padding_size)

            obscured_text_q.append(current_char)
            obscure_seq_q.append(padding_size)
            obscured_text_q.append(padding)

        return {
            'success': True,
            'obscured_text': "".join(obscured_text_q),
            'obscuration_seq': list(obscure_seq_q)
        }

    def clarify(self, obscured_text=None, key=None, obscured_seq=None):
        clarified_text_q = deque()
        current_text_pos = 0
        current_seq_pos = 1 # for debuging
        for current_seq in obscured_seq:
            if current_seq == 1:
                current_char = ' '
                current_text_pos += 2
            elif current_seq == 2:
                current_char = "\n"
                current_text_pos += 3
            else:
                current_char = obscured_text[current_text_pos]
                current_text_pos += 1 + current_seq

            clarified_text_q.append(current_char)
            current_seq_pos += 1

        clarified_text = "".join(clarified_text_q)
        return {"success": True, "clarified_text": clarified_text}
