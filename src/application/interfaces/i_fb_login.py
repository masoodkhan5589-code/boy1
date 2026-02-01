from abc import ABC, abstractmethod
from typing import List, Dict, Any


class IFbLogin(ABC):

    @abstractmethod
    def run_flow(self, flow_steps: List[str]) -> Dict[str, Any]:
        ...
