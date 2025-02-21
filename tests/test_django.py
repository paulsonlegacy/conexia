import unittest
from unittest.mock import patch, MagicMock
from django.test import RequestFactory
from django.http import HttpResponse
from django.conf import settings
from conexia.middleware.django import STUNMiddleware  # Adjust path if necessary
from conexia.core import STUNClient

if not settings.configured:
    settings.configure(
        DEFAULT_CHARSET="utf-8",
        INSTALLED_APPS=["django.contrib.contenttypes"],
        DATABASES={
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": ":memory:",
            }
        }
    )

class TestSTUNDjangoMiddleware(unittest.TestCase):
    def setUp(self):
        """Set up a mock request and middleware instance"""
        self.factory = RequestFactory()
        self.mock_response = MagicMock(return_value=HttpResponse("OK"))
        self.middleware = STUNMiddleware(get_response=self.mock_response)

    @patch.object(STUNClient, 'get_network_info', return_value={"data": {
        "ip": "192.168.1.1", "port": 54321, "city": "Lagos", "region": "LA", "country": "Nigeria",
        "continent": "Africa", "timezone": "Africa/Lagos", "nat_type": "Full Cone"
    }})
    def test_middleware_attaches_stun_info(self, mock_stun):
        """Test if middleware correctly attaches STUN info to request"""
        request = self.factory.get("/")
        response = self.middleware(request)

        self.assertEqual(request.ip, "192.168.1.1")
        self.assertEqual(request.city, "Lagos")
        self.assertEqual(request.nat_type, "Full Cone")
        self.assertEqual(response.status_code, 200)

    @patch.object(STUNClient, 'get_network_info', side_effect=Exception("Mocked Error"))
    def test_middleware_handles_exceptions_gracefully(self, mock_stun):
        """Test if middleware assigns None to request attributes when an error occurs"""
        request = self.factory.get("/")
        response = self.middleware(request)

        self.assertIsNone(request.ip)
        self.assertIsNone(request.city)
        self.assertIsNone(request.nat_type)
        self.assertEqual(response.status_code, 200)

if __name__ == "__main__":
    unittest.main()
