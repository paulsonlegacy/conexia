from django.conf import settings
from conexia.core import STUNClient

class STUNMiddleware:
    def __init__(self, get_response):
        """STUN Middleware providing network attributes for Django request object"""
        self.get_response = get_response
        # Load settings from Django settings.py
        self.cache_backend = getattr(settings, "STUN_CACHE_BACKEND", "file")  # Default: "file"
        self.cache_ttl = getattr(settings, "STUN_CACHE_TTL", 900)  # Default: 900 seconds
        # Initialize the STUN client with the configured settings
        self.stun_client = STUNClient(cache_backend=self.cache_backend, ttl=self.cache_ttl)

    def __call__(self, request):
        try:
            # Fetch STUN info synchronously
            stun_info = self.stun_client.get_network_info(request=request)
        except Exception:
            # Placeholder for exceptions
            stun_info = {
                "data": {
                    "ip": None,
                    "port": None,
                    "city": None,
                    "region": None,
                    "country": None,
                    "continent": None,
                    "timezone": None,
                    "nat_type": None
                }
            }

        # Attach to request object
        request.ip = stun_info["data"]["ip"]
        request.port = stun_info["data"]["port"]
        request.city = stun_info["data"]["city"]
        request.region = stun_info["data"]["region"]
        request.country = stun_info["data"]["country"]
        request.continent = stun_info["data"]["continent"]
        request.timezone = stun_info["data"]["timezone"]
        request.nat_type = stun_info["data"]["nat_type"]

        response = self.get_response(request)
        return response