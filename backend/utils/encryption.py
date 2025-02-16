from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import base64

def generate_key_from_password(password: str, salt: bytes = None) -> tuple[bytes, bytes]:
    if salt is None:
        salt = Fernet.generate_key()[:16]
    
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    return key, salt

def encrypt_text(text: str, key: bytes) -> str:
    f = Fernet(key)
    encrypted_data = f.encrypt(text.encode())
    return base64.urlsafe_b64encode(encrypted_data).decode()

def decrypt_text(encrypted_text: str, key: bytes) -> str:
    f = Fernet(key)
    decrypted_data = f.decrypt(base64.urlsafe_b64decode(encrypted_text))
    return decrypted_data.decode() 