import time
import unittest

from prolix import rand
from prolix import store


class TestStore(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.redis_store = store.RedisStore()

    def test_001_test_redis_set_and_delete(self):
        rs = rand.RandomString()
        # Redis driver seems not to like legal UTF8 in a key
        key = rs.random_ascii_string()
        value = rs.random_utf8_string(len=20)
        self.redis_store.store(key=key, item=value)
        self.redis_store.delete(key=key)
        ret_val = self.redis_store.get(key=key)
        self.assertTrue(ret_val is None)

    def test_002_test_redis_set_and_get(self):
        rs = rand.RandomString()
        # Redis driver seems not to like legal UTF8 in a key
        key = rs.random_ascii_string()
        value = rs.random_utf8_string(len=20)
        self.redis_store.store(key=key, item=value)
        ret_val = self.redis_store.get(key=key)
        self.assertEqual(value, ret_val)
        self.redis_store.delete(key=key)

    def test_003_test_redis_set_expire_and_get(self):
        rs = rand.RandomString()
        # Redis driver seems not to like legal UTF8 in a key
        key = rs.random_ascii_string()
        value = rs.random_utf8_string(len=20)
        self.redis_store.store_with_expiration(key=key, item=value, exp_seconds=1)
        ret_val = self.redis_store.get(key=key)
        self.assertEqual(value, ret_val)
        time.sleep(2)
        # Check to verify item expires
        ret_val = self.redis_store.get(key=key)
        self.assertTrue(ret_val is None)

    def test_005_test_redis_set_invalid_key(self):
        rs = rand.RandomString()
        # Redis driver seems not to like legal UTF8 in a key
        key = rs.random_utf8_string()
        value = rs.random_utf8_string(len=20)
        ret_val = self.redis_store.store(key=key, item=value)
        self.assertFalse(ret_val)
