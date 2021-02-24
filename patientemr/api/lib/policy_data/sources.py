
from typing import Dict

class BaseSource:

    STANDARDIZED_KEYS = ["deductible", "stop_loss", "oop_max"]

    def __init__(self, member_id:int):
        self.member_id = int(member_id)

    def get_url(self, *args, **kwargs) -> str:
        """ This method must be implemented on child class.
        """
        raise NotImplementedError()

    def standardize_response_data(self, data:Dict) -> Dict:
        return data


class SourceAPI1(BaseSource):
    def get_url(self) -> str:
        return f"https://api1.com?member_id={self.member_id}"

class SourceAPI2(BaseSource):
    def get_url(self) -> str:
        return f"https://api1.com?member_id={self.member_id}"


class SourceAPI3(BaseSource):
    def get_url(self) -> str:
        return f"https://api1.com?member_id={self.member_id}"

