from flask import request, g
from conexia.core import STUNClient

# Safe Flask-Login import as Flask-Login (external auth library for Flask) may be used or not
try:
    from flask_login import current_user
    flask_login_enabled = True
except ImportError:
    flask_login_enabled = False


class STUNMiddleware:
    def __init__(self, app, cache_backend="file", ttl=900):
        """STUN Middleware providing network attributes for Flask's global object for request context"""
        self.app = app
        self.stun_client = STUNClient(cache_backend=cache_backend, ttl=ttl)
        app.before_request(self.before_request)

    def before_request(self):
        try:
            # Get user ID (Support Flask-Login, headers, or cookies)
            user_id = None
            if flask_login_enabled and hasattr(current_user, "is_authenticated") and current_user.is_authenticated:
                user_id = current_user.get_id()  # Flask-Login user ID
            elif "Authorization" in request.headers:  
                user_id = request.headers.get("Authorization")  # Token-based auth
            elif "user_id" in request.cookies:  
                user_id = request.cookies.get("user_id")  # Cookie-based auth

            # Get STUN info
            stun_info = self.stun_client.get_network_info(user_id=user_id)
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

        # Store network attributes in `g` (Flask's global object for request context)
        # Attach to request object
        g.ip = stun_info["data"]["ip"]
        g.port = stun_info["data"]["port"]
        g.city = stun_info["data"]["city"]
        g.region = stun_info["data"]["region"]
        g.country = stun_info["data"]["country"]
        g.continent = stun_info["data"]["continent"]
        g.timezone = stun_info["data"]["timezone"]
        g.nat_type = stun_info["data"]["nat_type"]
        g.user_id = user_id  # Store user ID too
