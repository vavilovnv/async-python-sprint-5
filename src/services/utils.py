import random

from hashlib import pbkdf2_hmac
from string import ascii_letters


APP_ITERS = 100_000
STR_LENGTH = 12
DEFAULT_FOLDER = 'user_files'


def hash_password(password: str, hash_salt: str = None):
    if hash_salt is None:
        hash_salt = "".join(random.choice(ascii_letters) for _ in range(STR_LENGTH))
    derived_key = pbkdf2_hmac(
        'sha256',
        password.encode(),
        hash_salt.encode(),
        APP_ITERS
    )
    return f"{hash_salt}${derived_key.hex()}"
