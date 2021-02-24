
from collections import defaultdict
from typing import List, Dict, Callable

from .sources import BaseSource

def _validate_response_data_keys(response_data:Dict) -> None:
    if set(response_data.keys()) != set(BaseSource.STANDARDIZED_KEYS):
        raise ValueError(
            f"Invalid response key, expected {BaseSource.STANDARDIZED_KEYS}, got {response_data.keys()}")


def _stack_response_data(standardized_responses:List[Dict]) -> Dict:
    stacked_response_data = defaultdict(list)

    for response_data in standardized_responses:
        _validate_response_data_keys(response_data)
        for k, v in response_data.items():
            stacked_response_data[k].append(v)

    return stacked_response_data


class UnknownStrategyError(Exception):
    pass

# # # Strategies # # #

def average_strategy(standardized_responses:List[Dict]) -> Dict:
    if len(standardized_responses) == 0:
        raise ValueError("standardized_responses list cannot be empty")

    stacked_response_data = _stack_response_data(standardized_responses)
    averages = {k:sum(v) / len(v) for k, v in stacked_response_data.items()}

    return averages


def max_strategy(standardized_responses:List[Dict]) -> Dict:
    if len(standardized_responses) == 0:
        raise ValueError("standardized_responses list cannot be empty")

    stacked_response_data = _stack_response_data(standardized_responses)
    maxes = {k:max(v) for k, v in stacked_response_data.items()}

    return maxes

# # #

DEFAULT_STRATEGY = 'average_strategy'

def get_coalesce_stragety(strategy:str) -> Callable:
    if strategy == 'average_strategy':
        return average_strategy
    elif  strategy == 'max_strategy':
        return max_strategy
    else:
        raise UnknownStrategyError()

