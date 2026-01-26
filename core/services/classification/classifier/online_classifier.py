import re
from urllib.parse import urlparse

import numpy as np

from core.services.classification.classifier.onnx_classifier import OnnxUrlClassifier


class OnlineClassifierV1(OnnxUrlClassifier):
    NUM_FEATURES = 19

    def build_inputs(self, url: str) -> dict:
        features = {}
        parsed_url = urlparse(url)

        # length-based features
        features["url_length"] = float(len(url))
        features["hostname_length"] = float(len(parsed_url.netloc))
        features["path_length"] = float(len(parsed_url.path))
        features["query_length"] = float(len(parsed_url.query))

        # count-based features (common indicators)
        features["dot_count"] = float(url.count("."))
        features["hyphen_count"] = float(url.count("-"))
        features["at_count"] = float(url.count("@"))
        features["question_count"] = float(url.count("?"))
        features["equal_count"] = float(url.count("="))
        features["slash_count"] = float(url.count("/"))
        features["percent_count"] = float(url.count("%"))
        features["digits_count"] = float(sum(c.isdigit() for c in url))
        features["letters_count"] = float(sum(c.isalpha() for c in url))

        # binary indicators
        ip_pattern = r"(([01]?\d\d?|2[0-4]\d|25[0-5])\.){3}([01]?\d\d?|2[0-4]\d|25[0-5])"
        features["contains_ip"] = 1.0 if re.search(ip_pattern, parsed_url.netloc) else 0.0

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
        features["has_https"] = 1.0 if parsed_url.scheme == "https" else 0.0

        # structural features
        features["path_depth"] = parsed_url.path.count("/")

        subdomains = parsed_url.netloc.split(".")
        if "www" in subdomains:
            subdomains.remove("www")
        features["num_subdomains"] = len(subdomains) - 1 if len(subdomains) > 1 else 0

        # suspicious words (common in phishing/malicious URLs)
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

        # structure as onnx input
        input_array = np.array([list(features.values())], dtype=np.float32)
        return {"input": input_array}
