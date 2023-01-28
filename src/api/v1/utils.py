from services.utils import hash_password


def validate_password(hashed_password: str, password: str):
    hash_salt = hashed_password.split("$")[0]
    return hashed_password == hash_password(password, hash_salt)
