import os
import random
from typing import Tuple

from src.common import config
from src.infrastructure.files.file_reader import FileReader


def get_full_name() -> Tuple[str, str]:
    # Path to the file containing first names
    first_name_path = os.path.join(config.data_dir, 'firstname.txt')

    # Reading first names into a list and removing any newlines or empty spaces
    first_name_list = [
        str(firstname).strip().replace('\n', '')
        for firstname in FileReader(first_name_path).read_lines() if firstname.strip() != ""
    ]

    # Path to the file containing last names
    last_name_path = os.path.join(config.data_dir, 'lastname.txt')

    # Reading last names into a list and removing any newlines or empty spaces
    last_name_list = [
        str(lastname).strip().replace('\n', '')
        for lastname in FileReader(last_name_path).read_lines() if lastname.strip() != ""
    ]

    # Randomly select one first name and one last name
    first_name = random.choice(first_name_list) if first_name_list else ''
    last_name = random.choice(last_name_list) if last_name_list else ''

    return first_name, last_name
