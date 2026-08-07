from enum import Enum


class CompanyStatus(str, Enum):
    PENDING = "PENDING"
    FOUND = "FOUND"
    NOT_FOUND = "NOT_FOUND"
    FAILED = "FAILED"


class OutreachStatus(str, Enum):
    DRAFT = "DRAFT"
    PENDING_APPROVAL = "PENDING_APPROVAL"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    SCHEDULED = "SCHEDULED"
    SENT = "SENT"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"

