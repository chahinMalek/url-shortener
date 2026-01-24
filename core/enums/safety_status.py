from enum import Enum


class SafetyStatus(str, Enum):
    PENDING = "pending"
    SAFE = "safe"
    MALICIOUS = "malicious"
    SUSPICIOUS = "suspicious"
