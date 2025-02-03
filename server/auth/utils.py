import hashlib
import base64


def hash_password(login: str, password: str) -> str:
    login_bytes = login.encode('utf-8')
    password_bytes = password.encode('utf-8')
    data = login_bytes + password_bytes
    hash_bytes = hashlib.sha256(data).digest()
    return base64.b64encode(hash_bytes).decode('utf-8')