import unittest

from prolix import rand


class TestRand(unittest.TestCase):

    def test_001_two_random_strings_not_equal(self):
        rs = rand.RandomString()
        str1 = rs.random_utf8_string(20)
        str2 = rs.random_utf8_string(20)
        self.assertNotEqual(str1, str2)

    def test_002_random_string_len(self):
        rs = rand.RandomString()
        str_len = 7
        str1 = rs.random_utf8_string(str_len)
        self.assertEqual(len(str1),str_len)

    def test_003_random_string_limits(self):
        rs = rand.RandomString()
        str1 = rs.random_utf8_string(lower=0, upper=int(0x110000))
        self.assertNotEqual(0, len(str1))

    def test_004_two_random_int_arrays_not_equal(self):
        random_ints = rand.RandomInts()
        array_len = 15
        ints1 = random_ints.random_ints(array_len)
        ints2 = random_ints.random_ints(array_len)
        for i in range(0, array_len):
            self.assertNotEqual(ints1[i], ints2[i])

    def test_005_random_ints_len(self):
        random_ints = rand.RandomInts()
        array_len = 7
        ints1 = random_ints.random_ints(array_len)
        self.assertEqual(len(ints1),array_len)

    def test_006_rand_values(self):
        random_values = rand.RandValues()
        min_val = 1
        max_val = 15
        key, val = random_values.random_kv(max_val_len=max_val, min_val_len=min_val)
        self.assertTrue(len(val) >= min_val)
        self.assertTrue(len(val) <= max_val)
        vals = random_values.random_vals(num=5)
        self.assertEqual(len(vals),5)
