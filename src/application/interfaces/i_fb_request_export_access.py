from abc import ABC, abstractmethod


class IFbRequestExportAccess(ABC):

    @abstractmethod
    def export(self, data: str) -> tuple:
        ...
