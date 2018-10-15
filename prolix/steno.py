import random
import standard_logger
from prolix.config import Config
from prolix import index
from prolix import rand
from prolix import store

from collections import deque


class Steno:
    """Class that provides stenography support"""

    def __init__(self, logger=None):
        self.logger = logger if logger else standard_logger.get_logger("Store")
        self.conf_data = Config.conf(logger=self.logger).get_data()
        self.default_expiration_seconds = self.conf_data['default_store_expiration_secs']
        self.redis_store = store.RedisStore(logger=self.logger)

    def obscure_chars(self, num=None, min_chars=5,  max_chars=50):
        secure_rng = random.SystemRandom()

        obfuscation_chars = " !\u0027,.0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz\u0022"
        obfuscation_chars_len = len(obfuscation_chars)

        paddings = []

        for i in range(0, num):
            padding = deque()
            num_chars = secure_rng.randint(min_chars, max_chars)
            for j in range(1,num_chars):
                rand_pos = secure_rng.randint(0,obfuscation_chars_len-1)
                rand_char = obfuscation_chars[rand_pos]
                padding.append(rand_char)

            paddings.append("".join(list(padding)))

        return paddings

    def obscure(self, text=None, expiration_secs=None):
        """
        Obscure text

        :param str text: Text to obscured
        :param int expiration_secs: How long text should be valid for - default 300 secs (5 mins)
        :return: {key, expiration_secs, obscured text, errors}
        :rtype: dict
        """

        # Initialize various things
        idx = index.IndexEntry(logger=self.logger)
        rs = rand.RandomString(logger=self.logger)
        random_ints = rand.RandomInts(logger=self.logger)
        expiration_secs = expiration_secs if expiration_secs else self.default_expiration_seconds

        # Generate limits for random characters
        min_ord, max_ord = self.get_ord_range(text)
        # Generate list of interpolation counts
        text_len = len(text)
        interpolation_counts = random_ints.random_ints(len=text_len, lower=8, upper=64)
        #interpolation_counts = []

        # Obscure the text
        obscured_text_dq = deque()
        for i in range(0, text_len):
            # Get the current character
            current_char = text[i]

            # Get the number of random characters to add
            interpolation_count = interpolation_counts[i]
            # Get a random string of len(interpolation_count) with characters in the correct range
            interpolation_chars = rs.random_utf8_string(len=interpolation_count, lower=min_ord, upper=max_ord)
            # Save the current character, then the interpolated characters
            obscured_text_dq.append(current_char)
            obscured_text_dq.append(interpolation_chars)

            # # Get a random string of len(interpolation_count) with characters in the correct range
            # interpolation_chars = self.obscure_chars(num=1)[0]
            # interpolation_count = len(interpolation_chars)
            # interpolation_counts.append(interpolation_count)
            # # Save the current character, then the interpolated characters
            # obscured_text_dq.append(current_char)
            # obscured_text_dq.append(interpolation_chars)

        obscured_text = "".join(list(obscured_text_dq))

        # Generate storage key and save Index instance
        random_values = rand.RandValues(logger=self.logger)
        key = random_values.random_password()
        idx.storage_key = key
        idx.steno_seq = interpolation_counts
        idx.ttl_seconds = expiration_secs
        idx_json_str = idx.to_json_str()

        result = self.redis_store.store_with_expiration(
            key=key,
            item=idx_json_str,
            exp_seconds=expiration_secs)

        results = {}
        if result['success']:
            results['success'] = True
            results['key'] = key
            results['expiration_seconds'] = result['expiration_secs']
            results['obscured_text'] = obscured_text
        else:
            results['success'] = False
            results['errors'] = result['errors']

        return results

    def clarify(self, key=None, text=None):
        """
        Clarify text previously obscured

        :param str key: Key returned from obscure process
        :param str text: Text returned from  obscure process
        :return: {clarified text, error}
        :rtype: dict
        """
        results = {}

        result = self.redis_store.get(key=key)
        if result['success']:
            obscured_text = text
            clarified_text = deque()

            idx_json = result['item']
            idx = index.IndexEntry.from_json_str(idx_json, logger=self.logger)
            interpolation_counts = idx.steno_seq

            obscured_text_pos = 0
            for ic_pos in range(0, len(interpolation_counts)):
                interpolation_count = interpolation_counts[ic_pos]
                # First character is real
                current_char = obscured_text[obscured_text_pos]
                # Save off current char
                clarified_text.append(current_char)
                # Skip the current character and padding
                obscured_text_pos = 1 + obscured_text_pos + interpolation_count

            results['success'] = True
            results['clarified_text'] = "".join(list(clarified_text))
        else:
            results['success'] = False
            results['errors'] = result['errors']

        return results

    def get_ord_range(self, text):
        """
        Get the minimum and maximum ordinal values in a string

        :param str text: text to evaluate
        :return: (min ord, max ord)
        :rtype: tuple(int, int)
        """
        min_ord = 32
        max_ord = 0

        for ch in text:
            ord_val = ord(ch)
            if ord_val < min_ord:
                min_ord = ord_val
            if ord_val > max_ord:
                max_ord = ord_val

        return (min_ord, max_ord)
