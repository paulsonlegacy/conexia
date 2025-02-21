import unittest
from unittest.mock import patch, AsyncMock
from conexia.core import AsyncSTUNClient
from conexia.cache import IPResolverCache

class TestAsyncSTUNClient(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        """Setup test client with mock cache."""
        self.client = AsyncSTUNClient(cache_backend="memory", ttl=300)

    @patch("stun.get_ip_info", return_value=("Full-Cone NAT", "203.0.113.1", 45678))
    @patch("conexia.utils.check_ip_info", new_callable=AsyncMock)
    async def test_get_network_info(self, mock_geo_info, mock_stun):
        """Test that AsyncSTUNClient fetches and caches STUN info correctly."""
        
        # Mocking geo location API response
        mock_geo_info.return_value = {
            "city": "Mock City",
            "region": "Mock Region",
            "country": "Mock Country",
            "timezone": "UTC",
            "loc": "12.345,-67.890",
            "org": "Mock ISP"
        }

        result = await self.client.get_network_info(user_id="test_user")

        # Validate expected data in the result
        self.assertEqual(result["user_id"], "test_user")
        self.assertEqual(result["data"]["ip"], "203.0.113.1")
        self.assertEqual(result["data"]["port"], 45678)
        self.assertEqual(result["data"]["nat_type"], "Full-Cone NAT")
        self.assertEqual(result["data"]["city"], "Mock City")
        self.assertEqual(result["data"]["region"], "Mock Region")
        self.assertEqual(result["data"]["country"], "Mock Country")
        self.assertEqual(result["data"]["isp_info"], "Mock ISP")

    async def test_caching(self):
        """Test caching functionality (should return the same cached values)."""
        
        user_id = "cached_user"
        cached_data = {
            "user_id": user_id,
            "data": {
                "ip": "198.51.100.2",
                "port": 55555,
                "nat_type": "Full Cone",
                "city": "Cached City",
                "region": "Cached Region",
                "country": "Cached Country",
                "continent": "Cached Continent",
                "cord": "11.111,-22.222",
                "isp_info": "Cached ISP",
                "timezone": "UTC"
            },
            "timestamp": 1700000000
        }

        # Manually store data in cache
        self.client.cache.cache_stun_info(user_id, cached_data)

        # Fetch cached data
        cached_result = await self.client.get_network_info(user_id=user_id)

        # Ensure the cached data is correctly retrieved
        self.assertIsNotNone(cached_result)
        self.assertEqual(cached_result["data"]["ip"], "198.51.100.2")
        self.assertEqual(cached_result["data"]["port"], 55555)
        self.assertEqual(cached_result["data"]["nat_type"], "Full Cone")
        self.assertEqual(cached_result["data"]["city"], "Cached City")
        self.assertEqual(cached_result["data"]["isp_info"], "Cached ISP")

    @patch("stun.get_ip_info", side_effect=Exception("STUN server unreachable"))
    async def test_stun_resolution_error(self, mock_stun):
        """Test handling of STUN resolution failure."""
        with self.assertRaises(Exception) as context:
            await self.client.get_network_info(user_id="error_user")
        
        self.assertIn("STUN server unreachable", str(context.exception))


if __name__ == "__main__":
    unittest.main()
