from dataclasses import dataclass


@dataclass
class BaseFbAccountInformationData:
    first_name: str
    last_name: str
    age: int
    gender: int
    password: str
