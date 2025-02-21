import asyncio, stun, sqlite3, time, random
from conexia.cache import *
from conexia.exceptions import STUNResolutionError
from conexia.utils import *


# ================================
# Default cache expiry is 900s or 15min
# Cache backend options - memory, file, sqlite, redis
# ================================
class AsyncSTUNClient:
    def __init__(self, cache:bool = True, stun_server:str=None, stun_port:int=None, cache_backend:str="file", ttl:int=900, **cache_kwargs):
        """Initialize STUN client with caching support."""
        self.cache_toggle = cache # For toggling caching option
        self.cache_backend = cache_backend
        # Selecting server randomly from default STUN servers
        server_count = random.randint(0, len(DEFAULT_STUN_SERVERS) - 1)
        self.stun_server = stun_server or DEFAULT_STUN_SERVERS[server_count]["server"]
        self.stun_port = int(stun_port or DEFAULT_STUN_SERVERS[server_count]["port"])
        # Initializing cache engine
        self.cache = IPResolverCache(backend=cache_backend, ttl=abs(ttl), **cache_kwargs)

    def _get_cached_ips(self):
        """Retrieve all cached IPs based on backend type."""
        if isinstance(self.cache.cache, InMemoryCache):
            return list(self.cache.cache.cache.keys())  

        elif isinstance(self.cache.cache, FileCache):
            cache_data = self.cache.cache._load_cache()  
            return list(cache_data.keys())  

        elif isinstance(self.cache.cache, SQLiteCache):
            with sqlite3.connect(self.cache.cache.db_path) as conn:
                cursor = conn.execute("SELECT ip FROM stun_cache")
                return [row[0] for row in cursor.fetchall()]  

        elif isinstance(self.cache.cache, RedisCache):
            return self.cache.cache.redis.keys("*")  

        return []

    async def get_stun_info(self, stun_server="stun.l.google.com", stun_port=19302):
        """Fetches STUN server details (NAT type, IP, and port)."""
        loop = asyncio.get_running_loop()
        nat_type, ip, port = await loop.run_in_executor(
            None, stun.get_ip_info, "0.0.0.0", 54320, stun_server, stun_port
        )
        return nat_type, ip, port

    async def get_network_info(self, request=None, user_id=None):
        """Retrieve NAT type, external IP, and external port using configurable caching."""
        timestamp = time.time()  

        try:
            # If cache option is toggled
            if self.cache_toggle:
                #print("Trying to fetch data from cache")
                user_id = get_user_id(request, user_id)
                cached_ip = self._get_cached_ips()
                if cached_ip:
                    stun_info = self.cache.get_cached_info(user_id)
                    if stun_info:
                        #print(f"Found data in {self.cache_backend} cache")
                        return stun_info
            
            #print("Cache empty.. Fetching new STUN info")
            nat_type, ip, port = await self.get_stun_info(self.stun_server, self.stun_port)
            # Fetching other network parameters via API
            geo_info = await check_ip_info(ip)
            # Compressing all information
            stun_data = {
                "user_id": user_id, 
                "data": {
                    "ip": ip, "port": port, "nat_type": nat_type, "city": geo_info["city"], 
                    "region": geo_info["region"], "country": geo_info["country"], "continent": get_continent_from_timezone(geo_info["timezone"]),
                    "cord": geo_info["loc"], "isp_info": geo_info["org"], "timezone": geo_info["timezone"]
                },
                "timestamp": timestamp
            }
            # Cache data
            self.cache.cache_stun_info(user_id, stun_data)
            # Return STUN result
            return stun_data

        except Exception as e:
            raise STUNResolutionError(f"Failed to retrieve STUN Info: {e}")

    async def get_user_id(self, request=None, user_id=None):
        """Get user ID"""
        stun_info = await self.get_network_info(request, user_id)
        return stun_info["user_id"]
    
    async def get_public_ip(self, request=None, user_id=None):
        """Get public IP."""
        stun_info = await self.get_network_info(request, user_id)
        return stun_info["data"]["ip"]

    async def get_public_port(self, request=None, user_id=None):
        """Get public port"""
        stun_info = await self.get_network_info(request, user_id)
        return stun_info["data"]["port"]
    
    async def get_city(self, request=None, user_id=None):
        """Get city"""
        stun_info = await self.get_network_info(request, user_id)
        return stun_info["data"]["city"]
    
    async def get_region(self, request=None, user_id=None):
        """Get region"""
        stun_info = await self.get_network_info(request, user_id)
        return stun_info["data"]["region"]
    
    async def get_country(self, request=None, user_id=None):
        """Get country"""
        stun_info = await self.get_network_info(request, user_id)
        return stun_info["data"]["country"]
    
    async def get_continent(self, request=None, user_id=None):
        """Get continent"""
        stun_info = await self.get_network_info(request, user_id)
        return stun_info["data"]["continent"]
    
    async def get_cordinate(self, request=None, user_id=None):
        """Get location cordinate."""
        stun_info = await self.get_network_info(request, user_id)
        return stun_info["data"]["cord"]
    
    async def get_timezone(self, request=None, user_id=None):
        """Get timezone"""
        stun_info = await self.get_network_info(request, user_id)
        return stun_info["data"]["timezone"]
    
    async def get_isp_info(self, request=None, user_id=None):
        """Get ISP info."""
        stun_info = await self.get_network_info(request, user_id)
        return stun_info["data"]["isp_info"]

    async def get_nat_type(self, request=None, user_id=None):
        """Get NAT type."""
        stun_info = await self.get_network_info(request, user_id)
        return stun_info["data"]["nat_type"]
    

class STUNClient(AsyncSTUNClient):
    def get_network_info(self, request=None, user_id=None):
        """Synchronous wrapper for getting STUN info."""
        return asyncio.run(super().get_network_info(request, user_id))

    def get_user_id(self, request=None, user_id=None):
        """Synchronous wrapper for getting user ID."""
        stun_info = self.get_network_info(request, user_id)
        return stun_info["user_id"]

    def get_public_ip(self, request=None, user_id=None):
        """Synchronous wrapper for getting IP."""
        stun_info = self.get_network_info(request, user_id)
        return stun_info["data"]["ip"]

    def get_public_port(self, request=None, user_id=None):
        """Synchronous wrapper for getting port."""
        stun_info = self.get_network_info(request, user_id)
        return stun_info["data"]["port"]
    
    def get_city(self, request=None, user_id=None):
        """Synchronous wrapper for getting city."""
        stun_info = self.get_network_info(request, user_id)
        return stun_info["data"]["city"]
    
    def get_region(self, request=None, user_id=None):
        """Synchronous wrapper for getting region."""
        stun_info = self.get_network_info(request, user_id)
        return stun_info["data"]["region"]
    
    def get_country(self, request=None, user_id=None):
        """Synchronous wrapper for getting country."""
        stun_info = self.get_network_info(request, user_id)
        return stun_info["data"]["country"]
    
    def get_continent(self, request=None, user_id=None):
        """Synchronous wrapper for getting continent."""
        stun_info = self.get_network_info(request, user_id)
        return stun_info["data"]["continent"]
    
    def get_timezone(self, request=None, user_id=None):
        """Synchronous wrapper for getting timezone."""
        stun_info = self.get_network_info(request, user_id)
        return stun_info["data"]["timezone"]

    def get_cordinate(self, request=None, user_id=None):
        """Synchronous wrapper for getting cordinate."""
        stun_info = self.get_network_info(request, user_id)
        return stun_info["data"]["cord"]
    
    def get_isp_info(self, request=None, user_id=None):
        """Synchronous wrapper for getting ISP info."""
        stun_info = self.get_network_info(request, user_id)
        return stun_info["data"]["isp_info"]

    def get_nat_type(self, request=None, user_id=None):
        """Synchronous wrapper for getting NAT type."""
        stun_info = self.get_network_info(request, user_id)
        return stun_info["data"]["nat_type"]
