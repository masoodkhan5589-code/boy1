from dataclasses import dataclass


@dataclass
class FbForgotPasswordPayload:
    id_source: str
    contact: str
