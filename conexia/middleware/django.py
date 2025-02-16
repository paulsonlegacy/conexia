from django.conf import settings
from conexia.core import STUNClient

class STUNMiddleware:
    def __init__(self, get_response):
        """STUN Middleware providing network attributes for Django request object"""
        self.get_response = get_response
        # Load settings from Django settings.py
        self.cache_backend = getattr(settings, "STUN_CACHE_BACKEND", "file")  # Default: "file"
        self.cache_ttl = getattr(settings, "STUN_CACHE_TTL", 300)  # Default: 300 seconds
        # Initialize the STUN client with the configured settings
        self.stun_client = STUNClient(cache_backend=self.cache_backend, ttl=self.cache_ttl)

    def __call__(self, request):
        try:
            # Fetch STUN info synchronously
            stun_info = self.stun_client.get_stun_info(request=request)
            ip = stun_info["data"]["ip"]
            port = stun_info["data"]["port"]
            nat_type = stun_info["data"]["nat_type"]
        except Exception:
            ip, port, nat_type = None, None, None

        # Attach to request object
        request.ip = ip
        request.port = port
        request.nat_type = nat_type

        response = self.get_response(request)
        return response