from typing import Optional
from dataclasses import dataclass

from src.domain.enums.contact_type import ContactType


@dataclass
class OTPServiceResponse:
    id: Optional[str] = None
    contact: Optional[str] = None
    additional_value: Optional[str] = None
    prefix: Optional[str] = None
    contact_type: Optional[str] = ContactType.EMAIL.value.key
