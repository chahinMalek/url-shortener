import hashlib


class HashingService:
    """
    Simple and efficient hashing algorithm. Uses md5 hash and base62 encoding.
    """

    # base62 alphabet
    ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    BASE = len(ALPHABET)

    # Length of the generated hash code
    CODE_LENGTH = 8

    # Number of bytes from MD5 hash to use
    HASH_BYTES = 8

    def generate_hash(self, url: str) -> str:
        if not url or not url.strip():
            raise ValueError("URL cannot be empty")
        url = url.strip()
        hash_digest = hashlib.md5(url.encode("utf-8")).digest()
        hash_int = int.from_bytes(hash_digest[: self.HASH_BYTES], byteorder="big")
        code = self._encode_base62(hash_int)
        return code

    def _encode_base62(self, number: int) -> str:
        if number == 0:
            return self.ALPHABET[0] * self.CODE_LENGTH

        result = []
        while number > 0 and len(result) < self.CODE_LENGTH:
            remainder = number % self.BASE
            result.append(self.ALPHABET[remainder])
            number //= self.BASE
        # padding the remainder
        while len(result) < self.CODE_LENGTH:
            result.append(self.ALPHABET[0])
        # reverse to get the correct order
        return "".join(reversed(result[: self.CODE_LENGTH]))

    def validate_hash(self, hash_code: str) -> bool:
        if not hash_code or len(hash_code) != self.CODE_LENGTH:
            return False
        return all(char in self.ALPHABET for char in hash_code)
