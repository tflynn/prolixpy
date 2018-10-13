import unittest

from prolix import rand
from prolix import index


class TestIndex(unittest.TestCase):

    def test_001_test_index_entry_serialization(self):
        rs = rand.RandomString()
        ris = rand.RandomInts()
        ide = index.IndexEntry()
        ide.storage_key = rs.random_utf8_string(len=20)
        ide.steno_text = rs.random_utf8_string(len=100)
        ide.steno_seq = ris.random_ints(len=100)
        ide.mapping = ris.random_ints(len=200)

        json_str = ide.to_json_str()
        new_ide = index.IndexEntry.from_json_str(json_str)

        # Check fields explicitly set
        self.assertEqual(ide.storage_key, new_ide.storage_key)
        self.assertEqual(ide.steno_text, new_ide.steno_text)
        self.assertEqual(ide.steno_seq, new_ide.steno_seq)
        self.assertEqual(ide.mapping, new_ide.mapping)
        # Check fields not set
        self.assertEqual(ide.ttl_seconds, new_ide.ttl_seconds)
