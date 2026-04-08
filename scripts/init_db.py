"""Create database tables for local MVP setup."""

from app.core.database import Base, engine
from app.models import AuditLog, Blacklist, EmailVerification, Member, Session, Team


def main() -> None:
    """Import models and create all configured tables."""
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    main()
