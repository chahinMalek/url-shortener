import re
from urllib.parse import urlparse


class UrlValidator:
    def __init__(self):
        # strict url characters check (RFC 3986)
        # allowed: alnum, hyphen, period, underscore, tilde and reserved characters
        self._valid_url_chars = r"A-Za-z0-9\-._~:/?#\[\]@!$&'()*+,;=%"

    def is_valid(self, url: str) -> bool:
        if not isinstance(url, str):
            return False

        if not url.isascii():
            return False

        if "." not in url:
            return False

        if re.search(f"[^{self._valid_url_chars}]", url):
            return False

        if urlparse(url).scheme not in ["http", "https"]:
            return False

        return True
