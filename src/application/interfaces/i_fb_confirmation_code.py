from abc import ABC, abstractmethod
from typing import Tuple


class IFbConfirmationCode(ABC):
    @abstractmethod
    def execute(self, confirmation_code: str | int, is_basic_mode: bool = False) -> Tuple[bool, bool]:
        ...
