import enum


class UserRole(str, enum.Enum):
    STUDENT = "STUDENT"
    EVENT_COORDINATOR = "EVENT_COORDINATOR"
    JUDGE = "JUDGE"
    ADMIN = "ADMIN"
    SPONSOR = "SPONSOR"


class EventStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    PUBLISHED = "PUBLISHED"
    REGISTRATION_CLOSED = "REGISTRATION_CLOSED"
    ONGOING = "ONGOING"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class TeamStatus(str, enum.Enum):
    FORMING = "FORMING"
    COMPLETE = "COMPLETE"
    DISBANDED = "DISBANDED"


class TeamMemberRole(str, enum.Enum):
    LEADER = "LEADER"
    MEMBER = "MEMBER"


class RegistrationStatus(str, enum.Enum):
    PENDING_PAYMENT = "PENDING_PAYMENT"
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"
    ATTENDED = "ATTENDED"


class PaymentStatus(str, enum.Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    REFUNDED = "REFUNDED"


class AttendanceStatus(str, enum.Enum):
    VALID = "VALID"
    DUPLICATE_ATTEMPT = "DUPLICATE_ATTEMPT"
    INVALID = "INVALID"


class JudgeAssignmentStatus(str, enum.Enum):
    ASSIGNED = "ASSIGNED"
    COMPLETED = "COMPLETED"


class NotificationType(str, enum.Enum):
    INFO = "INFO"
    ALERT = "ALERT"
    SUCCESS = "SUCCESS"
    WARNING = "WARNING"


class SponsorshipTier(str, enum.Enum):
    TITLE = "TITLE"
    PLATINUM = "PLATINUM"
    GOLD = "GOLD"
    SILVER = "SILVER"
    BRONZE = "BRONZE"


class SponsorshipStatus(str, enum.Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    ACTIVE = "ACTIVE"
    EXPIRED = "EXPIRED"


class PromotionSlotType(str, enum.Enum):
    BANNER = "BANNER"
    STALL = "STALL"
    STAGE_MENTION = "STAGE_MENTION"
    SOCIAL_MEDIA = "SOCIAL_MEDIA"
    APP_HIGHLIGHT = "APP_HIGHLIGHT"


class AnnouncementTarget(str, enum.Enum):
    ALL = "ALL"
    STUDENTS = "STUDENTS"
    COORDINATORS = "COORDINATORS"
    JUDGES = "JUDGES"
    SPONSORS = "SPONSORS"


class ApplicationStatus(str, enum.Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class InvitationStatus(str, enum.Enum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    EXPIRED = "EXPIRED"
    REVOKED = "REVOKED"

