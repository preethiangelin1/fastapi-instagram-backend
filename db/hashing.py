from pwdlib import PasswordHash
import hashlib
import secrets

password_hash = PasswordHash.recommended()


class Hash:
    @staticmethod
    def hash(password: str):
        return password_hash.hash(password)

    @staticmethod
    def verify(hashed_password, plain_password):
        return password_hash.verify(plain_password, hashed_password)

    @staticmethod
    def generate_reset_token():
        return secrets.token_urlsafe(32)

    @staticmethod
    def hash_reset_token(token: str):
        return hashlib.sha256(token.encode()).hexdigest()
    