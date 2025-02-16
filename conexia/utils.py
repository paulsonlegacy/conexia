import os, uuid

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

# Functions
def get_machine_uuid():
    """Retrieve or create a persistent machine UUID."""
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            return f.read().strip()
    
    new_uuid = str(uuid.uuid4())  # Generate new unique ID
    with open(CACHE_FILE, "w") as f:
        f.write(new_uuid)
    
    return new_uuid


def get_user_id(request=None, user_id=None):
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