import time
import json
import base64
import uuid
from typing import Optional
from Cryptodome.PublicKey import RSA
from Cryptodome.Cipher import AES, PKCS1_v1_5
from Cryptodome.Random import get_random_bytes

from src.common.utils import compress_to_gzip
from src.domain.dtos.encrypted_password_payload import EncryptPasswordPayload
from src.infrastructure.clients.request_custom import RequestCustom


class EncryptedPassword:

    def __init__(self, payload: EncryptPasswordPayload):
        self.payload = payload

    def password_encrypt(self, public_key_id: int, public_key: str) -> Optional[str]:
        session_key = get_random_bytes(32)
        iv = get_random_bytes(12)
        timestamp = str(int(time.time()))
        recipient_key = RSA.import_key(public_key)
        cipher_rsa = PKCS1_v1_5.new(recipient_key)
        rsa_encrypted = cipher_rsa.encrypt(session_key)
        cipher_aes = AES.new(session_key, AES.MODE_GCM, iv)
        cipher_aes.update(timestamp.encode())
        aes_encrypted, tag = cipher_aes.encrypt_and_digest(self.payload.password.encode("utf8"))
        size_buffer = len(rsa_encrypted).to_bytes(2, byteorder="little")
        payload = base64.b64encode(
            b"".join(
                [
                    b"\x01",
                    public_key_id.to_bytes(1, byteorder="big"),
                    iv,
                    size_buffer,
                    rsa_encrypted,
                    tag,
                    aes_encrypted,
                ]
            )
        )
        return f"#PWD_FB4A:2:{timestamp}:{payload.decode()}"

    def password_key_fetch(self) -> Optional[tuple[int, str]]:
        headers = {
            "Accept-Encoding": "gzip, deflate, br",
            "Content-Type": "application/x-www-form-urlencoded",
            "Content-Encoding": "gzip"
        }

        params = {
            "device_id": str(uuid.uuid4()),
            "version": "2",
            "flow": "CONTROLLER_INITIALIZATION",
            "locale": "vi_VN",
            "client_country_code": "VN",
            "method": "GET",
            "fb_api_req_friendly_name": "pwdKeyFetch",
            "fb_api_caller_class": "Fb4aAuthHandler",
            "access_token": "350685531728|62f8ce9f74b12f84c123cc23437a4a32"
        }

        resp = RequestCustom(
            url="https://b-graph.facebook.com/pwd_key_fetch",
            headers=headers,
            body=compress_to_gzip(params),
            proxy=self.payload.proxy,
            verify_ssl=False
        ).post()

        if not resp or not hasattr(resp, "body"):
            return None

        body_response_json = json.loads(resp.body)
        public_key_id = body_response_json.get("key_id")
        publickey = body_response_json.get("public_key")

        if public_key_id is None or publickey is None:
            return None

        return int(public_key_id), publickey
