import pytest

from core.services.hashing_service import HashingService


@pytest.mark.unit
class TestHashingService:
    @pytest.fixture(scope="class")
    def hashing_service(self):
        return HashingService()

    def test_init(self, hashing_service: HashingService):
        expected_alphabet = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
        assert isinstance(hashing_service, HashingService)
        assert hashing_service.ALPHABET == expected_alphabet
        assert hashing_service.CODE_LENGTH == 8
        assert hasattr(hashing_service, "generate_hash")
        assert hasattr(hashing_service, "validate_hash")

    def test_generate_hash(self, hashing_service: HashingService):
        url = "https://example.com"
        hash_code = hashing_service.generate_hash(url)

        assert hash_code is not None
        assert isinstance(hash_code, str)
        assert len(hash_code) == 8

    def test_validate_hash(self, hashing_service: HashingService):
        valid_code = "a1B2c3D4"
        invalid_code_empty = ""
        invalid_code_short = "abc123"
        invalid_code_long = "a1B2c3D4e5"
        invalid_code_chars = "a1B2c3D!"

        assert hashing_service.validate_hash(valid_code) is True
        assert hashing_service.validate_hash(invalid_code_empty) is False
        assert hashing_service.validate_hash(invalid_code_short) is False
        assert hashing_service.validate_hash(invalid_code_long) is False
        assert hashing_service.validate_hash(invalid_code_chars) is False

    def test_generate_and_validate_hash(self, hashing_service: HashingService):
        url = "https://example.com/test"
        hash_code = hashing_service.generate_hash(url)

        assert hashing_service.validate_hash(hash_code) is True

    def test_generate_hash_deterministic(self, hashing_service: HashingService):
        url = "https://example.com/test"
        hashes = [hashing_service.generate_hash(url) for _ in range(10)]

        assert len(set(hashes)) == 1

    def test_generate_hash_url_safe(self, hashing_service: HashingService):
        assert hashing_service.ALPHABET.isalnum()

    def test_generate_hash_indexable(self, hashing_service: HashingService):
        url = "https://example.com"
        hash_code = hashing_service.generate_hash(url)

        assert {hash_code: url}.get(hash_code) == url

    def test_generate_hash_case_sensitive(self, hashing_service: HashingService):
        letters = [c for c in hashing_service.ALPHABET if c.isalpha()]
        lcase = sorted([c for c in letters if c.islower()])
        ucase = sorted([c for c in letters if c.isupper()])

        assert "".join(lcase) != "".join(ucase)
        assert "".join(lcase) == "".join(ucase).lower()

        url1 = "https://example.com/CaseTest"
        url2 = "https://example.com/casetest"
        assert hashing_service.generate_hash(url1) != hashing_service.generate_hash(url2)

    def test_generate_hash_error_on_empty(self, hashing_service: HashingService):
        with pytest.raises(ValueError, match="URL cannot be empty"):
            hashing_service.generate_hash("")

        with pytest.raises(ValueError, match="URL cannot be empty"):
            hashing_service.generate_hash("   ")

    def test_generate_hash_url_normalization(self, hashing_service: HashingService):
        code1 = hashing_service.generate_hash("https://example.com")
        code2 = hashing_service.generate_hash("  https://example.com  ")

        assert code1 == code2
