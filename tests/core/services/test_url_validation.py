import pytest

from core.services.url_validation import UrlValidator


class TestUrlValidator:
    @pytest.fixture
    def validator(self):
        return UrlValidator()

    def test_valid_http_url(self, validator):
        url = "http://example.com/page"
        assert validator.is_valid(url) is True

    def test_valid_https_url(self, validator):
        url = "https://example.com/page"
        assert validator.is_valid(url) is True

    def test_valid_url_with_subdomain(self, validator):
        url = "https://subdomain.example.com/path"
        assert validator.is_valid(url) is True

    def test_valid_url_with_query_params(self, validator):
        url = "https://example.com/page?key=value&foo=bar"
        assert validator.is_valid(url) is True

    def test_valid_url_with_fragment(self, validator):
        url = "https://example.com/page#section"
        assert validator.is_valid(url) is True

    def test_valid_url_with_port(self, validator):
        url = "https://example.com:8080/page"
        assert validator.is_valid(url) is True

    def test_valid_url_with_allowed_characters(self, validator):
        url = "https://example.com/path-with_special~chars"
        assert validator.is_valid(url) is True

    def test_invalid_non_string_input(self, validator):
        assert validator.is_valid(123) is False
        assert validator.is_valid(None) is False
        assert validator.is_valid([]) is False

    def test_invalid_non_ascii_url(self, validator):
        url = "https://example.com/café"
        assert validator.is_valid(url) is False

    def test_invalid_url_without_dot(self, validator):
        url = "http://localhost"
        assert validator.is_valid(url) is False

    def test_invalid_url_with_invalid_characters(self, validator):
        url = "https://example.com/<script>"
        assert validator.is_valid(url) is False

    def test_invalid_url_with_spaces(self, validator):
        url = "https://example.com/path with spaces"
        assert validator.is_valid(url) is False

    def test_invalid_ftp_scheme(self, validator):
        url = "ftp://example.com/file"
        assert validator.is_valid(url) is False

    def test_invalid_no_scheme(self, validator):
        url = "example.com/page"
        assert validator.is_valid(url) is False

    def test_invalid_empty_string(self, validator):
        url = ""
        assert validator.is_valid(url) is False
