import os
import time
import json
import unittest
import sqlite3
import redis
from conexia.cache import InMemoryCache, FileCache, SQLiteCache, RedisCache

# Sample test data
USER_ID = "test_user"
STUN_DATA = {
    "data": {
        "ip": "192.168.1.100",
        "port": 5000,
        "city": "New York",
        "region": "NY",
        "country": "USA",
        "continent": "NA",
        "timezone": "EST",
        "cord": "40.7128,-74.0060",
        "isp_info": "ISP Inc.",
        "nat_type": "Symmetric NAT",
    },
    "timestamp": time.time(),
}

# ================================
# 1️⃣ In-Memory Cache Tests
# ================================
class TestInMemoryCache(unittest.TestCase):
    def setUp(self):
        self.cache = InMemoryCache(ttl=2)  # Short TTL for testing expiry

    def test_cache_retrieval(self):
        self.cache.cache_stun_info(USER_ID, STUN_DATA)
        self.assertEqual(self.cache.get_cached_info(USER_ID), STUN_DATA)

    def test_cache_expiration(self):
        self.cache.cache_stun_info(USER_ID, STUN_DATA)
        time.sleep(2.1)
        self.assertIsNone(self.cache.get_cached_info(USER_ID))

    def test_cache_clear(self):
        self.cache.cache_stun_info(USER_ID, STUN_DATA)
        self.cache.clear_cache(USER_ID)
        self.assertIsNone(self.cache.get_cached_info(USER_ID))


# ================================
# 2️⃣ File-Based Cache Tests
# ================================
class TestFileCache(unittest.TestCase):
    def setUp(self):
        self.temp_file = "test_cache.json"
        self.cache = FileCache(file_path=self.temp_file, ttl=2)

    def tearDown(self):
        if os.path.exists(self.temp_file):
            os.remove(self.temp_file)

    def test_cache_retrieval(self):
        self.cache.cache_stun_info(USER_ID, STUN_DATA)
        self.assertEqual(self.cache.get_cached_info(USER_ID), STUN_DATA)

    def test_cache_expiration(self):
        self.cache.cache_stun_info(USER_ID, STUN_DATA)
        time.sleep(2.1)
        self.assertIsNone(self.cache.get_cached_info(USER_ID))

    def test_cache_clear(self):
        self.cache.cache_stun_info(USER_ID, STUN_DATA)
        self.cache.clear_cache(USER_ID)
        self.assertIsNone(self.cache.get_cached_info(USER_ID))


# ================================
# 3️⃣ SQLite Cache Tests
# ================================
class TestSQLiteCache(unittest.TestCase):
    def setUp(self):
        self.temp_db = "test_cache.sqlite"
        self.cache = SQLiteCache(db_path=self.temp_db, ttl=2)

    def tearDown(self):
        if os.path.exists(self.temp_db):
            os.remove(self.temp_db)

    def test_cache_retrieval(self):
        self.cache.cache_stun_info(USER_ID, STUN_DATA)
        self.assertEqual(self.cache.get_cached_info(USER_ID), STUN_DATA)

    def test_cache_expiration(self):
        self.cache.cache_stun_info(USER_ID, STUN_DATA)
        time.sleep(2.1)
        self.assertIsNone(self.cache.get_cached_info(USER_ID))

    def test_cache_clear(self):
        self.cache.cache_stun_info(USER_ID, STUN_DATA)
        self.cache.clear_cache(USER_ID)
        self.assertIsNone(self.cache.get_cached_info(USER_ID))


# ================================
# 4️⃣ Redis Cache Tests
# ================================
class TestRedisCache(unittest.TestCase):
    def setUp(self):
        self.cache = RedisCache(ttl=2)

    def test_cache_retrieval(self):
        self.cache.cache_stun_info(USER_ID, STUN_DATA)
        self.assertEqual(self.cache.get_cached_info(USER_ID), STUN_DATA)

    def test_cache_expiration(self):
        self.cache.cache_stun_info(USER_ID, STUN_DATA)
        time.sleep(2.1)
        self.assertIsNone(self.cache.get_cached_info(USER_ID))

    def test_cache_clear(self):
        self.cache.cache_stun_info(USER_ID, STUN_DATA)
        self.cache.clear_cache(USER_ID)
        self.assertIsNone(self.cache.get_cached_info(USER_ID))


# Run the tests
if __name__ == "__main__":
    unittest.main()
