"""Create the first Founder account without loading demonstration data."""

import argparse
import getpass
import uuid

import app.models  # noqa: F401 - register SQLAlchemy mappings
from app.auth.jwt import hash_password
from app.database import SessionLocal
from app.models.users import User, UserRole


def main():
    parser = argparse.ArgumentParser(description="Create the initial FARM360 Founder account")
    parser.add_argument("--email", required=True)
    parser.add_argument("--name", required=True)
    parser.add_argument("--phone")
    args = parser.parse_args()

    password = getpass.getpass("Founder password (12-72 characters): ")
    confirm = getpass.getpass("Confirm password: ")
    if password != confirm:
        raise SystemExit("Passwords do not match")
    if not 12 <= len(password.encode("utf-8")) <= 72:
        raise SystemExit("Password must be between 12 and 72 UTF-8 bytes")

    with SessionLocal() as db:
        if db.query(User.id).filter(User.email == args.email).first():
            raise SystemExit("A user with this email already exists")
        founder = User(
            id=str(uuid.uuid4()), name=args.name.strip(), email=args.email.strip().casefold(),
            phone=args.phone, password_hash=hash_password(password), role=UserRole.founder,
        )
        db.add(founder)
        db.commit()
        print(f"Founder account created: {founder.email}")


if __name__ == "__main__":
    main()
