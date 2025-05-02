import os
import pickle
import hashlib
from functools import wraps


def file_cache(cache_dir='cache'):
    os.makedirs(cache_dir, exist_ok=True)

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create a unique key based on function name and arguments
            key = f"{func.__name__}_{hashlib.md5(pickle.dumps((args, kwargs))).hexdigest()}"
            cache_file = os.path.join(cache_dir, f"{key}.pkl")

            # Return cached result if exists
            if os.path.exists(cache_file):
                with open(cache_file, 'rb') as f:
                    data = pickle.load(f)
                    if not data:
                        raise ValueError('Empty/Invalid cache file found')
                    return data

            # Compute and cache the result
            try:
                result = func(*args, **kwargs)
            except Exception:
                result = {}
            with open(cache_file, 'wb') as f:
                pickle.dump(result, f)
            return result
        return wrapper
    return decorator
