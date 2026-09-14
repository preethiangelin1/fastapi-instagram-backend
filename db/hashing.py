from pwdlib import PasswordHash

password_hash = PasswordHash.recommended()


class Hash:
    @staticmethod
    def hash(password: str):
        return password_hash.hash(password)

    @staticmethod
    def verify(hashed_password, plain_password):
        return password_hash.verify(plain_password, hashed_password)