import json
import random
import re
import socket
import string
import gzip
import time
import unicodedata
import urllib.parse
import uuid
from datetime import datetime
from typing import Optional, Union


def generate_random_password(by_name: str = None, min_length=8, max_length=16):
    """
    Tạo mật khẩu ngẫu nhiên.
    Nếu by_name được cung cấp, mật khẩu sẽ có độ dài 12-16 ký tự và chứa một ký tự đặc biệt,
    ít nhất 1 chữ hoa, và 1-2 chữ số.
    Ngược lại, mật khẩu sẽ có độ dài 8-16 ký tự chỉ gồm chữ cái và chữ số.
    """
    # Nếu không có tên được cung cấp, sử dụng logic ban đầu
    if by_name is None:
        characters = string.ascii_letters + string.digits
        password_length = random.randint(min_length, max_length)
        password = ''.join(random.choice(characters) for _ in range(password_length))
        return f"NEW_{password}"
    else:
        # Logic tạo mật khẩu khi có tên được truyền vào
        # Mật khẩu có độ dài từ 12 đến 16 ký tự
        password_length = random.randint(16, 18)

        # --- Tạo các ký tự bắt buộc ---
        # Chọn một ký tự đặc biệt ngẫu nhiên
        special_characters = "!@#"
        special_char = random.choice(special_characters)

        # Chọn một ký tự in hoa ngẫu nhiên
        upper_char = random.choice(string.ascii_uppercase)

        # Chọn 1 hoặc 2 chữ số ngẫu nhiên
        num_digits = random.randint(1, 2)
        digit_chars = [random.choice(string.digits) for _ in range(num_digits)]

        # Tạo danh sách các ký tự bắt buộc
        password_list = [special_char, upper_char] + digit_chars

        # --- Tạo phần còn lại của mật khẩu ---
        # Tạo chuỗi ký tự bao gồm chữ cái (cả in hoa và thường) và chữ số
        characters = string.ascii_letters + string.digits

        # Tính toán số ký tự còn lại cần tạo
        remaining_length = password_length - len(password_list)

        # Thêm các ký tự ngẫu nhiên vào phần còn lại của mật khẩu
        password_list.extend(random.choice(characters) for _ in range(remaining_length))

        # --- Xáo trộn và trả về mật khẩu ---
        # Xáo trộn danh sách để các ký tự bắt buộc không ở cùng một vị trí
        random.shuffle(password_list)

        # Nối danh sách các ký tự thành chuỗi mật khẩu hoàn chỉnh
        password = ''.join(password_list)

        return password


def compress_to_gzip(body: dict) -> bytes:
    body_str = urllib.parse.urlencode(body)
    gzip_body = gzip.compress(body_str.encode("utf-8"))
    return gzip_body


def remove_accents(text: str) -> str:
    # Normalize to NFD form and remove diacritical marks
    text = unicodedata.normalize('NFD', text)
    text = re.sub(r'[\u0300-\u036f]', '', text)
    return text


def generate_username(first_name: str, last_name: str) -> str:
    """
    Generate a username using first name and last name (no accents).
    - Converts to lowercase
    - Removes accents (dấu tiếng Việt)
    - Joins names with or without a dot
    - Appends 5-digit timestamp-based suffix
    """
    first_name = remove_accents(first_name.lower().strip().replace(' ', ''))
    last_name = remove_accents(last_name.lower().strip().replace(' ', ''))

    base_username = f"{last_name}{first_name}"
    timestamp_suffix = str(int(time.time() * 1000))[-5:]

    return f"{base_username}.{timestamp_suffix}".replace(' ', '')


def generate_local_addrs() -> str:
    """
    Giả lập địa chỉ IP cục bộ giống thiết bị Android thật (WiFi/Mobile).
    Trả về dạng phù hợp với header X-Fb-Network-Properties
    """
    # Một số dải local IP phổ biến trên Android (WiFi, LTE)
    ip_ranges = [
        "192.168.1.",  # Common with Android tethering
    ]

    prefix = random.choice(ip_ranges)
    suffix = random.randint(2, 254)

    return f"{prefix}{suffix}"


def generate_fb_conn_uuid_client() -> str:
    """
    Tạo chuỗi UUID dạng không dấu gạch, giống X-Fb-Conn-Uuid-Client từ app Katana.
    """
    return uuid.uuid4().hex  # Chuỗi 32 ký tự hexa, không có gạch ngang


def generate_machine_id(length=24):
    chars = string.ascii_letters + string.digits  # a-zA-Z0-9
    return ''.join(random.choices(chars, k=length))


def mask_email(email: str) -> str:
    local, domain = email.split("@")
    if len(local) < 3:
        masked_local = local[0] + "*" * (len(local) - 1)
    else:
        masked_local = local[0] + "*" * (len(local) - 2) + local[-1]
    return f"{masked_local}@{domain}"


def generate_birth_date(age: int) -> str:
    today = datetime.today()
    birth_year = today.year - int(age)
    birth_month = random.randint(1, 12)
    birth_day = random.randint(1, 28)
    birth_date = datetime(birth_year, birth_month, birth_day)
    return birth_date.strftime("%d-%m-%Y")


def resolve_hostname(hostname: str) -> Optional[str]:
    ip_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
    if re.match(ip_pattern, hostname):
        return hostname
    try:
        return socket.gethostbyname(hostname)
    except socket.gaierror:
        return None


def load_config(config_path: str) -> Optional[dict]:
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def extract_ds_user_id_from_cookie(instagram_cookie: str = None) -> Union[str, None]:
    if not instagram_cookie:
        return None

    ds_user_id = re.search(r'ds_user_id=([^;]+)(?:;|$)', instagram_cookie)
    if ds_user_id:
        return ds_user_id.group(1)

    return None


def extract_rur_from_cookie(instagram_cookie: str = None) -> Optional[str]:
    if not instagram_cookie:
        return None

    match = re.search(r'rur=([^;]+)(?:;|$)', instagram_cookie)
    return match.group(1) if match else None


def extract_machine_id_from_cookie(instagram_cookie: str = None) -> Optional[str]:
    if not instagram_cookie:
        return None

    match = re.search(r'mid=([^;]+)(?:;|$)', instagram_cookie)

    if not match:
        return None

    return match.group(1) if match else None


def generate_custom_android_id() -> str:
    random_android_id = random.choices(string.ascii_letters + string.digits, k=16)
    return f"android-{''.join(random_android_id)}".encode('utf-8').decode('utf-8')


def generate_instagram_machine_id() -> str:
    part1 = ''.join(random.choices(string.ascii_letters + string.digits, k=11))
    dash = '-'
    part2 = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
    return f"{part1}{dash}{part2}".encode('utf-8').decode('utf-8')


def random_non_empty_line(path: str):
    try:
        with open(path, 'r', encoding='utf-8') as file:
            lines = [line.strip() for line in file.readlines() if line.strip()]
        return random.choice(lines) if lines else None
    except FileNotFoundError:
        return None
