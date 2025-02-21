import unittest
from unittest.mock import patch, MagicMock
from flask import Flask, g
from conexia.middleware.flask import STUNMiddleware  # Adjust path if necessary
from conexia.core import STUNClient

class TestSTUNFlaskMiddleware(unittest.TestCase):
    def setUp(self):
        """Set up Flask app with middleware"""
        self.app = Flask(__name__)
        self.middleware = STUNMiddleware(self.app)

        @self.app.route("/test")
        def test_route():
            return {
                "ip": g.ip, "city": g.city, "nat_type": g.nat_type
            }, 200

    @patch.object(STUNClient, 'get_network_info', return_value={"data": {
        "ip": "203.0.113.1", "port": 54321, "city": "New York", "region": "NY", "country": "USA",
        "continent": "North America", "timezone": "America/New_York", "nat_type": "Symmetric NAT"
    }})
    def test_middleware_attaches_stun_info(self, mock_stun):
        """Test if middleware correctly attaches STUN info to Flask g object"""
        with self.app.test_client() as client:
            response = client.get("/test")
            data = response.get_json()

            self.assertEqual(data["ip"], "203.0.113.1")
            self.assertEqual(data["city"], "New York")
            self.assertEqual(data["nat_type"], "Symmetric NAT")

    @patch.object(STUNClient, 'get_network_info', side_effect=Exception("Mocked Error"))
    def test_middleware_handles_exceptions_gracefully(self, mock_stun):
        """Test if middleware assigns None when STUN fetch fails"""
        with self.app.test_client() as client:
            response = client.get("/test")
            data = response.get_json()

            self.assertIsNone(data["ip"])
            self.assertIsNone(data["city"])
            self.assertIsNone(data["nat_type"])

if __name__ == "__main__":
    unittest.main()