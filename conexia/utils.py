import os, uuid, pytz, requests

# Constants
CACHE_FILE = os.path.expanduser("~/.stun_resolver_config")
DEFAULT_STUN_SERVERS = [
    {"server":"stun.l.google.com", "port":19302},
    {"server":"stun1.l.google.com", "port":19302},
    {"server":"stun2.l.google.com", "port":19302},
    {"server":"stun3.l.google.com", "port":19302},
    {"server":"stun4.l.google.com", "port":19302},
    # {"server":"stun.stunprotocol.org", "port":3478},
    # {"server":"stun.voipstunt.com", "port":3478},
    # {"server":"stun.sipnet.net", "port":3478},
    # {"server":"stun.twilio.com:3478", "port":3478}
]
API_RESULT_TEMPLATE = {
    "ip": None, "city": None, "region": None,
    "country": None, "loc": None, "org": None,
    "timezone": None
}

# Functions
def get_machine_uuid() -> str:
    """Retrieve or create a persistent machine UUID."""
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            return f.read().strip()
    
    new_uuid = str(uuid.uuid4())  # Generate new unique ID
    with open(CACHE_FILE, "w") as f:
        f.write(new_uuid)
    
    return new_uuid


def get_user_id(request=None, user_id=None) -> str:
    """
    Determine whether to use passed in user ID, request user ID or machine-generated ID

    Supports:
    - Django (request.user)
    - Other frameworks that pass `user_id` directly
    - Standalone apps (fallback to machine UUID)

    Django Example:
    user_id = get_user_id(request)  

    Flask Example:
    from flask_login import current_user
    user_id = get_user_id(user_id=current_user.get_id()) 

    Stand-alone Application:
    user_id = get_user_id()  # Uses machine UUID  

    Manually Passing User ID:
    user_id = get_user_id(user_id="12345")  # Directly passing user ID
    """

    if user_id:  
        return str(user_id)  # Directly use user ID if provided

    if request and hasattr(request, "user") and getattr(request.user, "is_authenticated", False):
        return str(request.user.id)  # Use authenticated user ID

    return get_machine_uuid()  # Fallback for standalone apps or missing request


def get_continent_from_timezone(timezone: str) -> str | None:
    """
    Extracts the continent from a timezone string (e.g., "Africa/Lagos").

    Args:
        timezone (str): The timezone string.

    Returns:
        str | None: The continent name (e.g., "Africa") or None if the timezone is invalid.
    """
    try:
        pytz.timezone(timezone)  # Validate the timezone
        parts = timezone.split("/")  # Keep the original string for splitting
        if len(parts) >= 2:  # Ensure it has at least a continent/city structure
            return parts[0]
        return None
    except pytz.UnknownTimeZoneError:
        return None
    except Exception:
        return None


async def check_ip_info(ip: str) -> dict:
    """Fetch other network info using the ip address"""
    # IPinfo.io API free plan is limited to 50k requests/month
    api = f"https://ipinfo.io/{ip}?token=5b906ff5a22c80"

    try:
        # Fetching from API
        req = requests.get(api)

        if req.status_code == 200:
            data = req.json()
        else:
            data = API_RESULT_TEMPLATE
    except:
        data = API_RESULT_TEMPLATE
    return data