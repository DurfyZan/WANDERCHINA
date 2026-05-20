from typing import Optional
from datetime import datetime, timedelta
from app.core.config import get_settings

settings = get_settings()


class RateLimiter:
    def __init__(self):
        self.requests = {}
        self.window = 60
    
    def is_allowed(self, key: str, limit: int = 60) -> bool:
        now = datetime.utcnow()
        
        if key not in self.requests:
            self.requests[key] = []
        
        self.requests[key] = [
            req_time for req_time in self.requests[key]
            if now - req_time < timedelta(seconds=self.window)
        ]
        
        if len(self.requests[key]) >= limit:
            return False
        
        self.requests[key].append(now)
        return True
    
    def reset(self, key: str):
        if key in self.requests:
            del self.requests[key]


rate_limiter = RateLimiter()


class CacheManager:
    def __init__(self):
        self.cache = {}
        self.expiry = {}
    
    def get(self, key: str) -> Optional[any]:
        if key in self.cache:
            if key in self.expiry and datetime.utcnow() > self.expiry[key]:
                del self.cache[key]
                del self.expiry[key]
                return None
            return self.cache[key]
        return None
    
    def set(self, key: str, value: any, ttl: int = 300):
        self.cache[key] = value
        self.expiry[key] = datetime.utcnow() + timedelta(seconds=ttl)
    
    def delete(self, key: str):
        if key in self.cache:
            del self.cache[key]
        if key in self.expiry:
            del self.expiry[key]
    
    def clear(self):
        self.cache.clear()
        self.expiry.clear()


cache_manager = CacheManager()
