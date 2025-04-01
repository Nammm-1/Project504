from functools import wraps
import time
from flask import g, request, current_app

# Simple in-memory cache
_cache = {}

def timed_lru_cache(timeout=300):
    """
    Simple time-based cache decorator. 
    Use this for functions that don't change often.
    
    Args:
        timeout: Cache timeout in seconds (default: 5 minutes)
    """
    def decorator(func):
        cache = {}
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            key = str(args) + str(kwargs)
            curr_time = time.time()
            
            # Check if cached and not expired
            if key in cache:
                result, timestamp = cache[key]
                if curr_time - timestamp < timeout:
                    return result
            
            # Call the function and cache result
            result = func(*args, **kwargs)
            cache[key] = (result, curr_time)
            return result
            
        return wrapper
    return decorator

def cache_key_prefix():
    """Generate a cache key prefix based on the request."""
    return f"{request.path}_{request.args.get('page', '1')}_{request.args.get('query', '')}"

def get_cached_data(key, default=None):
    """Get data from the app cache with automatic key generation."""
    prefix = cache_key_prefix()
    full_key = f"{prefix}_{key}"
    return _cache.get(full_key, default)

def set_cached_data(key, data, timeout=300):
    """Store data in the app cache with automatic key generation."""
    prefix = cache_key_prefix()
    full_key = f"{prefix}_{key}"
    expiry = time.time() + timeout
    _cache[full_key] = (data, expiry)
    
    # Cleanup expired items occasionally
    if len(_cache) > 100 and time.time() % 10 < 0.1:  # ~10% chance of cleanup
        cleanup_cache()
    
    return data

def clear_cache():
    """Clear all cached data."""
    _cache.clear()
    
def clear_specific_cache(key):
    """Clear a specific cache key."""
    prefix = cache_key_prefix()
    full_key = f"{prefix}_{key}"
    
    # If the exact key exists, remove it
    if full_key in _cache:
        _cache.pop(full_key, None)
        return True
        
    # If not, try to find partial matches
    deleted = False
    keys_to_delete = []
    for k in _cache.keys():
        if key in k:
            keys_to_delete.append(k)
            deleted = True
            
    for k in keys_to_delete:
        _cache.pop(k, None)
        
    return deleted
    
def cleanup_cache():
    """Remove expired items from cache."""
    now = time.time()
    expired_keys = [k for k, (_, exp) in _cache.items() if exp < now]
    for k in expired_keys:
        _cache.pop(k, None)
        
def clear_dashboard_caches():
    """
    Clear all dashboard-related caches.
    Call this whenever inventory is updated to ensure dashboards show fresh data.
    """
    # Clear all admin/staff dashboard caches
    keys_to_delete = [k for k in _cache.keys() if 'admin_dashboard_' in k]
    # Clear cache for expiring items and low stock items
    keys_to_delete.extend([k for k in _cache.keys() if 'expiring_items_' in k or 'low_stock_items_' in k])
    
    for k in keys_to_delete:
        _cache.pop(k, None)
    
    return len(keys_to_delete)