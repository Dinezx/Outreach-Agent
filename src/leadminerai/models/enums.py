from enum import Enum


class CompanyStatus(str, Enum):
    PENDING = "PENDING"
    FOUND = "FOUND"
    NOT_FOUND = "NOT_FOUND"
    FAILED = "FAILED"
