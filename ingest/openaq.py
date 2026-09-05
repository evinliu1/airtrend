import os
import time

import httpx
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("OPENAQ_BASE_URL", "https://api.openaq.org/v3")
API_KEY = os.getenv("OPENAQ_API_KEY")

# Free tier gives me 60 rpm.
MIN_SECONDS_BETWEEN_REQS = 1.1
PAGE_SIZE = 1000
MAX_RETRIES = 5

_last_request_at = 0.0

class OpenAQError(RuntimeError):
    pass

def _throttle():
    """
        Sleep so we never fire two reqs closer than limit allows.
    """
    global _last_request_at
    wait = MIN_SECONDS_BETWEEN_REQS - (time.monotonic() - _last_request_at)
    if wait > 0:
        time.sleep(wait)
    _last_request_at = time.monotonic()

def get(path, params=None):
    """
        One GET, with throttling + retries. Returns parsed JSON body
    """
    if not API_KEY:
        raise OpenAQError("OPENAQ_API_KEY not set in .env")
    
    url = f"{BASE_URL}{path}"
    headers = {"X-API-KEY": API_KEY}

    for attempt in range(MAX_RETRIES):
        _throttle()
        try:
            response = httpx.get(url, params=params, headers=headers, timeout=30.0)
        except httpx.RequestError as exc:
            wait = 2**attempt
            print(f"network error ({exc.__class__.__name__}), retry in {wait}s")
            time.sleep(wait)
            continue

        if response.status_code == 429:
            wait = int(response.headers.get("x-ratelimit-reset", 2**attempt))
            print(f"rate limited, sleeping {wait}s")
            time.sleep(wait)
            continue

        if response.status_code >= 500:
            wait = 2**attempt
            print(f"server error {response.status_code}, retry in {wait}s")
            time.sleep(wait)
            continue

        if response.status_code != 200:
            raise OpenAQError(f"{response.status_code} from {url}: {response.text[:200]}")

        return response.json()
    
    raise OpenAQError(f"Gave up on {url} after {MAX_RETRIES} attempts.")

def paginate(path, params=None):
    """
        Yield every result across every page, one item at a time.
    """
    params = dict(params or {})
    params["limit"] = PAGE_SIZE
    page = 1

    while True:
        params["page"] = page
        body = get(path, params)
        results = body.get("results", [])
        if not results:
            return
        
        for item in results:
            yield item
        
        found = body.get("meta", {}).get("found")
        print(f"page {page}: {len(results)} results (found={found})")

        # Short page = reached end
        if len(results) < PAGE_SIZE:
            return
        page += 1