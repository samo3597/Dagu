import os
import json

def get_env(key: str, default=None):

    value = os.environ.get(key)
    
    if value is None:
        if default is None:
            raise RuntimeError(f"❌ Սխալ: Միջավայրի պարտադիր փոփոխականը '{key}' սահմանված չէ:")
        else:
            return default
    
    value_stripped = value.strip()
    
    if value_stripped.lower() in ("true", "yes", "on", "1"):
        return True
    if value_stripped.lower() in ("false", "no", "off", "0"):
        return False
        
    try:
        if "." in value_stripped:
            return float(value_stripped)
        return int(value_stripped)
    except ValueError:
        pass

    if (value_stripped.startswith("[") and value_stripped.endswith("]")) or \
       (value_stripped.startswith("{") and value_stripped.endswith("}")):
        try:
            return json.loads(value_stripped)
        except json.JSONDecodeError:
            pass

    return value_stripped

if __name__ == "__main__":
    os.environ["DEBUG_MODE"] = "True"
    os.environ["MAX_RETRIES"] = "5"
    os.environ["TIMEOUT_SEC"] = "12.5"
    os.environ["ALLOWED_IPS"] = '["192.168.1.1", "10.0.0.1"]'
    os.environ["API_KEY"] = "secret_abc_123"

    debug = get_env("DEBUG_MODE")
    retries = get_env("MAX_RETRIES")
    timeout = get_env("TIMEOUT_SEC")
    ips = get_env("ALLOWED_IPS")
    api_key = get_env("API_KEY")
    missing_var = get_env("NON_EXISTENT", default="default_val")

    print(f"DEBUG_MODE: {debug} -> տիպը՝ {type(debug)}")
    print(f"MAX_RETRIES: {retries} -> տիպը՝ {type(retries)}")
    print(f"TIMEOUT_SEC: {timeout} -> տիպը՝ {type(timeout)}")
    print(f"ALLOWED_IPS: {ips} -> տիպը՝ {type(ips)} (առաջին տարրը՝ {ips[0]})")
    print(f"API_KEY: {api_key} -> տիպը՝ {type(api_key)}")
    print(f"NON_EXISTENT: {missing_var} -> տիպը՝ {type(missing_var)}")
