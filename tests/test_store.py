import time
import unittest

import standard_logger

from prolix import rand
from prolix import store
from prolix import index


class TestStore(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.redis_store = store.RedisStore()
        cls.logger = standard_logger.get_logger('TestStore', console=True)

    def test_001_test_redis_set_and_delete(self):
        rs = rand.RandomString()
        key = rs.random_utf8_string(len=10)
        value = rs.random_utf8_string(len=20)
        self.redis_store.store(key=key, item=value)
        self.redis_store.delete(key=key)
        ret_val = self.redis_store.get(key=key)
        self.assertTrue(ret_val is None)

    def test_002_test_redis_set_no_expiration_and_get(self):
        rs = rand.RandomString()
        key = rs.random_utf8_string(len=10)
        value = rs.random_utf8_string(len=20)
        self.redis_store.store(key=key, item=value)
        ret_val = self.redis_store.get(key=key)
        self.assertEqual(value, ret_val)
        self.redis_store.delete(key=key)

    def test_003_test_redis_set_expire_and_get(self):
        rs = rand.RandomString()
        key = rs.random_utf8_string(len=10)
        value = rs.random_utf8_string(len=20)
        self.redis_store.store_with_expiration(key=key, item=value, exp_seconds=1)
        ret_val = self.redis_store.get(key=key)
        self.assertEqual(value, ret_val)
        time.sleep(2)
        # Check to verify item expires
        ret_val = self.redis_store.get(key=key)
        self.assertTrue(ret_val is None)

    def test_004_test_store_and_get_index_instance(self):
        rs = rand.RandomString()
        rv = rand.RandValues()
        ris = rand.RandomInts()
        key = rv.random_password()
        idx = index.IndexEntry()
        idx.storage_key = key
        idx.steno_text = rs.random_utf8_string(len=100)
        idx.steno_seq = ris.random_ints(len=100)
        idx.mapping = ris.random_ints(len=200)
        json_idx = idx.to_json_str()
        self.redis_store.store_with_expiration(key=key, item=json_idx)
        ret_idx_json = self.redis_store.get(key=key)
        # Cleanup
        self.redis_store.delete(key=key)
        self.assertEqual(json_idx, ret_idx_json)
        new_idx = index.IndexEntry.from_json_str(ret_idx_json)
        self.assertEqual(idx, new_idx)

