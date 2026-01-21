import re
from pathlib import Path
from urllib.parse import urlparse

import numpy as np

from core.services.classification.classifier.onnx_classifier import OnnxUrlClassifier


class XGBUrlClassifier(OnnxUrlClassifier):
    # Feature count must match the trained model
    _NUM_FEATURES = 13

    def _build_inputs(self, url: str) -> dict:
        features = {}
        parsed_url = urlparse(url)

        # 1. length-based features
        features["url_length"] = float(len(url))
        features["hostname_length"] = float(len(parsed_url.netloc))
        features["path_length"] = float(len(parsed_url.path))
        features["query_length"] = float(len(parsed_url.query))

        # 2. count-based features (common indicators)
        features["dot_count"] = float(url.count("."))
        features["hyphen_count"] = float(url.count("-"))
        features["at_count"] = float(url.count("@"))
        features["question_count"] = float(url.count("?"))
        features["equal_count"] = float(url.count("="))
        features["slash_count"] = float(url.count("/"))
        features["percent_count"] = float(url.count("%"))
        features["digits_count"] = float(sum(c.isdigit() for c in url))
        features["letters_count"] = float(sum(c.isalpha() for c in url))

        # 3. binary indicators
        ip_pattern = r"(([01]?\d\d?|2[0-4]\d|25[0-5])\.){3}([01]?\d\d?|2[0-4]\d|25[0-5])"
        features["contains_ip"] = 1.0 if re.search(ip_pattern, parsed_url.netloc) else 0.0

        # usage of shortening services
        shortening_services = (
            r"bit\.ly|goo\.gl|shorte\.st|go2l\.ink|x\.co|ow\.ly|t\.co|tinyurl|tr\.im|is\.gd|cli\.gs|"
            r"yfrog\.com|migre\.me|ff\.im|tiny\.cc|url4\.eu|twit\.ac|su\.pr|twurl\.nl|snipurl\.com|"
            r"short\.to|BudURL\.com|ping\.fm|post\.ly|Just\.as|bkite\.com|snipr\.com|fic\.kr|loopt\.us|"
            r"doiop\.com|short\.ie|kl\.am|wp\.me|rubyurl\.com|om\.ly|to\.ly|bit\.do|t\.co|lnkd\.in|"
            r"db\.tt|qr\.ae|adf\.ly|goo\.gl|bitly\.com|cur\.lv|tinyurl\.com|ow\.ly|bit\.ly|ity\.im|"
            r"q\.gs|is\.gd|po\.st|bc\.vc|twitthis\.com|u\.to|j\.mp|buzurl\.com|cutt\.us|u\.bb|yourls\.org|"
            r"x\.co|prettylinkpro\.com|scrnch\.me|filoops\.info|vzturl\.com|qr\.net|1url\.com|tweez\.me|v\.gd|"
            r"tr\.im|link\.zip\.net"
        )
        features["is_shortened"] = 1.0 if re.search(shortening_services, url) else 0.0

        # presence of https
        features["has_https"] = 1.0 if parsed_url.scheme == "https" else 0.0

        # 4. structural features
        features["path_depth"] = parsed_url.path.count("/")

        subdomains = parsed_url.netloc.split(".")
        if "www" in subdomains:
            subdomains.remove("www")
        features["num_subdomains"] = len(subdomains) - 1 if len(subdomains) > 1 else 0

        # 5. suspicious words (common in phishing/malicious URLs)
        suspicious_words = [
            "login",
            "verify",
            "update",
            "account",
            "bank",
            "secure",
            "ebayisapi",
            "webscr",
        ]
        features["suspicious_word_count"] = sum(
            1 for word in suspicious_words if word in url.lower()
        )

        return features

        """
        Extract features from URL and build ONNX input dictionary.

        Args:
            url: The URL string to classify.

        Returns:
            Dictionary with 'input' key containing feature array.
        """
        features = self._extract_features(url)
        # ONNX expects float32 array with shape (1, num_features)
        input_array = np.array([features], dtype=np.float32)
        return {"input": input_array}

    def _extract_features(self, url: str) -> list[float]:
        """
        Extract numerical features from a URL for classification.

        Args:
            url: The URL string to extract features from.

        Returns:
            List of float features matching the model's expected input.
        """
        try:
            parsed = urlparse(url)
        except Exception:
            # Return neutral features if parsing fails
            return [0.0] * self._NUM_FEATURES

        domain = parsed.netloc or ""
        path = parsed.path or ""
        query = parsed.query or ""

        # Feature 1: URL length
        url_length = float(len(url))

        # Feature 2: Domain length
        domain_length = float(len(domain))

        # Feature 3: Path length
        path_length = float(len(path))

        # Feature 4: Query string length
        query_length = float(len(query))

        # Feature 5: Number of dots in domain
        dot_count = float(domain.count("."))

        # Feature 6: Number of hyphens in domain
        hyphen_count = float(domain.count("-"))

        # Feature 7: Number of digits in URL
        digit_count = float(sum(c.isdigit() for c in url))

        # Feature 8: Has IP address as domain (simple heuristic)
        has_ip = float(self._is_ip_address(domain))

        # Feature 9: Uses HTTPS
        uses_https = float(parsed.scheme == "https")

        # Feature 10: Number of subdomains
        subdomain_count = float(max(0, domain.count(".") - 1))

        # Feature 11: Path depth (number of path segments)
        path_segments = [s for s in path.split("/") if s]
        path_depth = float(len(path_segments))

        # Feature 12: Has query parameters
        has_query = float(1 if query else 0)

        # Feature 13: Number of special characters
        special_chars = sum(1 for c in url if c in "@#$%^&*()+=[]{}|;:',<>?")
        special_count = float(special_chars)

        return [
            url_length,
            domain_length,
            path_length,
            query_length,
            dot_count,
            hyphen_count,
            digit_count,
            has_ip,
            uses_https,
            subdomain_count,
            path_depth,
            has_query,
            special_count,
        ]

    @staticmethod
    def _is_ip_address(domain: str) -> bool:
        """Check if domain looks like an IP address."""
        # Remove port if present
        host = domain.split(":")[0]
        parts = host.split(".")
        if len(parts) != 4:
            return False
        return all(part.isdigit() and 0 <= int(part) <= 255 for part in parts)


def create_xgb_classifier(
    model_path: Path,
    version: str = "1.0.0",
    threshold: float = 0.5,
) -> XGBUrlClassifier:
    """
    Factory function to create an XGBUrlClassifier instance.

    Args:
        model_path: Path to the ONNX model file.
        version: Classifier version string.
        threshold: Classification threshold (0.0-1.0). URLs with threat scores
                   at or above this threshold are marked as MALICIOUS.

    Returns:
        Configured XGBUrlClassifier instance.
    """
    return XGBUrlClassifier(
        model_path=model_path,
        version=version,
        threshold=threshold,
    )
