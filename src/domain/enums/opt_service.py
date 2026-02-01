from enum import Enum
from collections import namedtuple

# The key must contain ‘mail’ if the verification type is MAIL
OtpServiceInfo = namedtuple('OtpServiceInfo', ['key', 'label'])


class OtpServices(Enum):
    KIMTAI_SITE_EMAIL = OtpServiceInfo('email_kimtai_site', 'Kimtai.site')
    GMAIL_66_ONLY_FACEBOOK = OtpServiceInfo('email_gmail_66_only_facebook', 'Gmail66.shop')
    CONTACT_FILE_TXT = OtpServiceInfo('email_contact_file_txt', 'Contact File (.txt)')
    IVASMS = OtpServiceInfo('email_ivasms', 'Ivasms.com')
