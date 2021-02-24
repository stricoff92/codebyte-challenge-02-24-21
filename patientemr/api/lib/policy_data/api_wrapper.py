
import json
from typing import List, Dict

from django.core.cache import cache
from rest_framework import status
import requests

from .sources import BaseSource


def fetch_data(sources:List[BaseSource]) -> List[Dict]:
    timeout_seconds = 6
    standardized_response_data = []

    for source in sources:
        url = source.get_url()

        # TODO: Add error handling/ retry logic
        response = requests.get(url, timeout=timeout_seconds)
        response.raise_for_status()

        standardized_data = source.standardize_response_data(response.json())
        standardized_response_data.append(standardized_data)

    return standardized_response_data


def _get_cache_key(member_id:int, strategy:str) -> str:
    return f"policydata_member{member_id}_{strategy}"

def check_for_cached_response(member_id:int, strategy:str) -> Dict:
    cache_key = _get_cache_key(member_id, strategy)
    cached_response = cache.get(cache_key)
    return cached_response if cached_response is None else json.loads(cached_response)

def set_cached_response(member_id:int, strategy:str, data:Dict, ttl_seconds=20*60) -> None:
    cache_key = _get_cache_key(member_id, strategy)
    data_to_cache = json.dumps(data)
    cache.set(cache_key, data_to_cache, ttl_seconds)
