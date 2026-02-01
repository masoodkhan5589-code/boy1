from abc import ABC, abstractmethod
from typing import List, Dict, Any

from src.domain.dtos.setting_loader_data import SettingLoaderData


class IFbVerified(ABC):

    @abstractmethod
    def run_flow(self, flow_steps: List[str]) -> Dict[str, Any]:
        ...

    @property
    @abstractmethod
    def settings(self) -> SettingLoaderData:
        ...
