from enum import Enum
from collections import namedtuple

ContactInfo = namedtuple('ContactInfo', ['key', 'label'])


class ContactType(Enum):
    EMAIL = ContactInfo('email', 'Mail')
    PHONE_NUMBER = ContactInfo('phone_number', 'Phone')
