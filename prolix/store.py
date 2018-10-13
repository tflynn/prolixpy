import sys

import redis

import standard_logger
from prolix import rand


class BaseStore:
    """Base class for all store implementations"""

    def __init__(self):
        self.logger = standard_logger.get_logger("store")
        self.default_expiration_seconds = 5 * 60
        self.expiration_seconds = self.default_expiration_seconds

    def store(self, key=None, item=None):
        """
        Store an item using key with the default expiration

        :param str key: Key under which to store the item
        :param obj item: Item to store. If not a string, must respond to str(obj)
        :return: No value returned
        """
        return self.store_with_expiration(item=item, exp_seconds=self.default_expiration_seconds)

    def store_with_expiration(self, key=None, item=None, exp_seconds=None):
        """
        Store an item with the specified expiration

        :param str key: Key under which to store the item
        :param obj item: Item to store. If not a string, must respond to str(obj)
        :param int exp_seconds: Expiration in seconds
        :return: No value returned
        """
        raise Exception("Not implemented")

    def get(self, key=None):
        """
        Get an item using the specified key. Item will be returned in its string representation - str(obj)

        :param str key: Key under which to store the item
        :return: item in string form or None if any error
        :rtype: str
        """
        raise Exception("Not implemented")

    def delete(self, key=None):
        """
        Delete an entry from the store

        :param str key: Key to delete
        :return: Nothing returned
        """
        raise Exception("Not implemented")


class RedisStore(BaseStore):
    """Store implementation to access a Redis instance"""

    def __init__(self, host=None, port=None, password=None):
        super(RedisStore, self).__init__()
        self.host = host if host else "127.0.0.1"
        self.port = port if port else 6379
        self.password = password
        try:
            self.redis = redis.StrictRedis(
                host = self.host,
                port = self.port,
                password = self.password
            )
        except Exception as e:
            self.logger.error("Error initializing Redis {0}".format(e))
            sys.exit(1)

    def check_key(self, key, exit_on_error=False):
        """
        Verify that the key is valid

        The current redis driver only accepts ASCII keys

        :param str key: Key to check
        :param bool exit_on_error: Exit on error - default False
        :return: True if valid (ASCII), False otherwise
        :rtype: bool
        """
        is_ascii = rand.RandomString().is_ascii(key)
        if not is_ascii:
            self.logger.error("Supplied key {0} is not ASCII as required.".format(key))
            if exit_on_error:
                sys.exit(1)

        return is_ascii

    def store(self, key=None, item=None):
        """
        Store an item

        :param str key: Key under which to store the item
        :param obj item: Item to store. If not a string, must respond to str(obj)
        :return: True if no error, False otherwise
        """
        errors = False
        if not key:
            self.logger.error("RedisStore:store_with_expiration no key specified")
            errors = True
        if key and not self.check_key(key):
            errors = True
        if not item:
            self.logger.error("RedisStore:store_with_expiration no item specified")
            errors = True
        if not isinstance(item, str):
            try:
                item = str(item)
            except Exception as e:
                self.logger.error(("RedisStore:store_with_expiration error converting object {0}"
                                   + " to string {1}").format(key,e))
                errors = True

        if not errors:
            try:
                self.redis.set(key, item)
            except Exception as e:
                self.logger.error("RedisStore:store error storing object {0} {1}".format(key, e))
                errors = True

        return not errors

    def store_with_expiration(self, key=None, item=None, exp_seconds=None):
        """
        Store an item with the specified expiration

        :param str key: Key under which to store the item
        :param obj item: Item to store. If not a string, must respond to str(obj)
        :param int exp_seconds: Expiration in seconds
        :return: True if no error, False otherwise
        """
        errors = False
        if not key:
            self.logger.error("RedisStore:store_with_expiration no key specified")
            errors = True
        if key and not self.check_key(key):
            errors = True
        if not item:
            self.logger.error("RedisStore:store_with_expiration no item specified")
            errors = True
        if not isinstance(item, str):
            try:
                item = str(item)
            except Exception as e:
                self.logger.error(("RedisStore:store_with_expiration error converting object {0}"
                                   + " to string {1}").format(key,e))
                errors = True

        self.expiration_seconds = exp_seconds if exp_seconds else self.default_expiration_seconds

        if not errors:
            try:
                self.redis.setex(key, exp_seconds, item)
            except Exception as e:
                self.logger.error("RedisStore:store_with_expiration error storing object {0} {1}".format(key, e))
                errors = True

        return not errors

    def get(self, key=None):
        """
        Get an item using the specified key. Item will be returned in its string representation - str(obj)

        :param str key: Key under which to store the item
        :return: item in string form or None if any error
        :rtype: str
        """
        errors = False
        if not key:
            self.logger.error("RedisStore:get no key specified")
            errors = True
        if key and not self.check_key(key):
            errors = True

        if not errors:
            try:
                if self.redis.exists(key):
                    value = self.redis.get(key).decode("UTF8")
                    return value
                else:
                    self.logger.warning("RedisStore:get key {0} does not exist".format(key))
            except Exception as e:
                self.logger.error("RedisStore:get error getting object {0} {1}".format(key, e))

        return None

    def delete(self, key=None):
        """
        Delete an entry from the store

        :param str key: Key to delete
        :return: True if success, False otherwise
        :rtype: bool
        """
        errors = False
        if not key:
            self.logger.error("RedisStore:delete no key specified")
            errors = True
        if key and not self.check_key(key):
            errors = True

        if not errors:
            try:
                if self.redis.exists(key):
                    self.redis.delete(key)
                else:
                    self.logger.warning("RedisStore:delete key {0} does not exist".format(key))
                    errors = True
            except Exception as e:
                self.logger.error("RedisStore:get error deleting object {0} {1}".format(key, e))
                errors = True

        return not errors
