import sys

import redis

import standard_logger
from json_config import JsonConfig


class BaseStore:
    """Base class for all store implementations"""

    def __init__(self, logger=None):
        self.logger = logger if logger else standard_logger.get_logger("Store")
        self.conf = JsonConfig.conf(logger=self.logger, package_name='prolix')
        self.conf.config_name = 'prolix_conf.json'
        self.conf_data = self.conf.get_data()
        self.default_expiration_seconds = self.conf_data['default_store_expiration_secs']
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

    def get_expiration_seconds(self):
        """
        Get the actual expiration seconds setting

        :return: expiration seconds
        :rtype: int
        """
        return self.expiration_seconds


class RedisStore(BaseStore):
    """Store implementation to access a Redis instance"""

    def __init__(self, host=None, port=None, password=None,logger=None):
        super(RedisStore, self).__init__(logger=logger)
        self.host = host if host else self.conf_data['redis_host']
        self.port = port if port else self.conf_data['redis_port']
        self.password = password if password \
            else self.conf_data['redis_password']

        try:
            self.redis = redis.StrictRedis(
                host=self.host,
                port=self.port,
                password=self.password
            )
        except Exception as e:
            self.logger.error("Error initializing Redis {0}".format(e))
            sys.exit(1)

    def store(self, key=None, item=None):
        """
        Store an item

        :param str key: Key under which to store the item
        :param obj item: Item to store. If not a string, must respond to str(obj)
        :return: {success, errors, expiration secs}
        :rtype: dict
        """
        return self.store_with_expiration(key=key, item=item, exp_seconds=self.expiration_seconds)

    def store_with_expiration(self, key=None, item=None, exp_seconds=None):
        """
        Store an item with the specified expiration

        :param str key: Key under which to store the item
        :param obj item: Item to store. If not a string, must respond to str(obj)
        :param int exp_seconds: Expiration in seconds
        :return: {success, errors, expiration secs}
        :rtype: dict
        """

        errors = []

        if not key:
            error_text = "RedisStore:store_with_expiration no key specified"
            self.logger.error(error_text)
            errors.append(error_text)
        if not item:
            error_text = "RedisStore:store_with_expiration no item specified"
            self.logger.error(error_text)
            errors.append(error_text)
        if not isinstance(item, str):
            try:
                item = str(item)
            except Exception as e:
                error_text = ("RedisStore:store_with_expiration error converting object {0}"
                                   + " to string {1}").format(key,e)
                self.logger.error(error_text)
                errors.append(error_text)

        self.expiration_seconds = exp_seconds if exp_seconds else self.default_expiration_seconds

        if not errors:
            try:
                self.redis.setex(key, self.expiration_seconds, item)
            except Exception as e:
                error_text = "RedisStore:store_with_expiration error storing object {0} {1}".format(key, e)
                self.logger.error(error_text)
                errors.append(error_text)

        result = {}
        if errors:
            result['success'] = False
            result['errors'] = errors
        else:
            result['success'] = True
            result['expiration_secs'] = self.expiration_seconds

        return result

    def get(self, key=None):
        """
        Get an item using the specified key. Item will be returned in its string representation - str(obj)

        :param str key: Key under which to store the item
        :return: {success, item, errors}
        :rtype: dict
        """
        errors = []
        if not key:
            error_text = "RedisStore:get no key specified"
            self.logger.error(error_text)
            errors.append(error_text)

        if not errors:
            try:
                if self.redis.exists(key):
                    item = self.redis.get(key).decode("UTF8")
                else:
                    error_text = "RedisStore:get key {0} does not exist".format(key)
                    self.logger.warning(error_text)
                    errors.append(error_text)
            except Exception as e:
                error_text = "RedisStore:get error getting object {0} {1}".format(key, e)
                self.logger.error(error_text)
                errors.append(error_text)

        result = {}
        if errors:
            result['success'] = False
            result['errors'] = errors
        else:
            result['success'] = True
            result['item'] = item

        return result

    def delete(self, key=None):
        """
        Delete an entry from the store

        :param str key: Key to delete
        :return: {success, errors}
        :rtype: dict
        """
        errors = []
        if not key:
            error_text = "RedisStore:delete no key specified"
            self.logger.error(error_text)
            errors.append(error_text)

        if not errors:
            try:
                if self.redis.exists(key):
                    self.redis.delete(key)
                else:
                    error_text = "RedisStore:delete key {0} does not exist".format(key)
                    self.logger.warning(error_text)
                    errors.append(error_text)
            except Exception as e:
                error_text = "RedisStore:delete error deleting object {0} {1}".format(key, e)
                self.logger.error(error_text)
                errors.append(error_text)

        result = {}
        if errors:
            result['success'] = False
            result['errors'] = errors
        else:
            result['success'] = True

        return result
