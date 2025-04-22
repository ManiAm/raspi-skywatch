
# Author: Mani Amoozadeh
# Email: mani.amoozadeh2@gmail.com
# Description: model for interacting with Redis

import redis
import json
import re
import inspect
import logging

logging.basicConfig(level=logging.INFO)

r = redis.Redis(host='localhost', port=6379, db=0)

def sanitize_key(key_str):

    key_str = key_str.replace(" ", "_")  # Replace spaces
    key_str = re.sub(r"[^\w:\-\.]", "_", key_str)  # Keep alphanumerics, :, -, _
    return key_str


def get_key(frame):

    method_name = frame.f_code.co_name

    args_info = inspect.getargvalues(frame)

    params = {arg: args_info.locals[arg] for arg in args_info.args if arg != 'self'}

    # Include *args and **kwargs if they exist
    if args_info.varargs and args_info.locals.get(args_info.varargs):
        params[f"*{args_info.varargs}"] = args_info.locals[args_info.varargs]
    if args_info.keywords and args_info.locals.get(args_info.keywords):
        params[f"**{args_info.keywords}"] = args_info.locals[args_info.keywords]

    # Convert params to a readable string
    param_str = ",".join(f"{k}={v}" for k, v in params.items())

    key_str = f"{method_name}:{param_str}"

    return sanitize_key(key_str)


def get_from_cache(frame):

    key = get_key(frame)
    val = r.get(key)
    if val:
        return json.loads(val)
    return None


def set_to_cache(frame, data, ttl=None):

    try:
        key = get_key(frame)
        value = json.dumps(data)
        r.set(key, value, ex=ttl)
    except redis.RedisError as e:
        logging.error(f"Redis error: {e}")
    except (TypeError, ValueError) as e:
        logging.error(f"Serialization error: {e}")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
