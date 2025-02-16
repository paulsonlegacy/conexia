import asyncio, stun, sqlite3, time, random
from conexia.cache import *
from conexia.exceptions import STUNResolutionError
from conexia.utils import get_user_id
from conexia.utils import DEFAULT_STUN_SERVERS


class AsyncSTUNClient:
    def __init__(self, stun_server=None, stun_port=None, cache_backend="file", ttl=300, **cache_kwargs): 
        """Initialize STUN client with caching support."""
        server_count = random.randint(0, len(DEFAULT_STUN_SERVERS) - 1)
        self.stun_server = stun_server or DEFAULT_STUN_SERVERS[server_count]["server"]
        self.stun_port = int(stun_port or DEFAULT_STUN_SERVERS[server_count]["port"])
        self.cache = IPResolverCache(backend=cache_backend, ttl=ttl, **cache_kwargs)

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

    async def get_stun_info(self, request=None, user_id=None):
        """Retrieve NAT type, external IP, and external port using configurable caching."""
        timestamp = time.time()  

        try:
            user_id = get_user_id(request, user_id)
            cached_ip = self._get_cached_ips()
            if cached_ip:
                stun_infos = self.cache.get_cached_info(user_id)
                if stun_infos:
                    return stun_infos
            
            loop = asyncio.get_running_loop()
            nat_type, ip, port = await loop.run_in_executor(
                None, stun.get_ip_info, "0.0.0.0", 54320, self.stun_server, self.stun_port
            )

            self.cache.cache_stun_info(user_id, ip, port, nat_type, timestamp)
            
            stun_infos = {
                "user_id": user_id,
                "data": {"ip": ip, "port": port, "nat_type": nat_type}, 
                "timestamp": timestamp
            }
            return stun_infos

        except Exception as e:
            raise STUNResolutionError(f"Failed to retrieve STUN Info: {e}")

    async def get_user_id(self, request=None, user_id=None):
        stun_info = await self.get_stun_info(request, user_id)
        return stun_info["user_id"]
    
    async def get_public_ip(self, request=None, user_id=None):
        stun_info = await self.get_stun_info(request, user_id)
        return stun_info["data"]["ip"]

    async def get_public_port(self, request=None, user_id=None):
        stun_info = await self.get_stun_info(request, user_id)
        return stun_info["data"]["port"]

    async def get_nat_type(self, request=None, user_id=None):
        stun_info = await self.get_stun_info(request, user_id)
        return stun_info["data"]["nat_type"]
    

class STUNClient(AsyncSTUNClient):
    def get_stun_info(self, request=None, user_id=None):
        """Synchronous wrapper for getting STUN info."""
        return asyncio.run(super().get_stun_info(request, user_id))

    def get_user_id(self, request=None, user_id=None):
        """Synchronous wrapper for getting user ID."""
        stun_info = self.get_stun_info(request, user_id)
        return stun_info["user_id"]

    def get_public_ip(self, request=None, user_id=None):
        """Synchronous wrapper for getting IP."""
        stun_info = self.get_stun_info(request, user_id)
        return stun_info["data"]["ip"]

    def get_public_port(self, request=None, user_id=None):
        """Synchronous wrapper for getting port."""
        stun_info = self.get_stun_info(request, user_id)
        return stun_info["data"]["port"]

    def get_nat_type(self, request=None, user_id=None):
        """Synchronous wrapper for getting NAT type."""
        stun_info = self.get_stun_info(request, user_id)
        return stun_info["data"]["nat_type"]
