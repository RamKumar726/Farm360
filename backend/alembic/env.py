from logging.config import fileConfig
from sqlalchemy import create_engine, pool
from alembic import context
import os
from dotenv import load_dotenv

# Load .env so DATABASE_URL is available
load_dotenv()

# Import all models so Alembic can detect them
import app.models  # noqa: F401
from app.database import Base

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

# Read DATABASE_URL directly from environment — bypasses configparser
# which crashes on % characters in URL-encoded passwords (e.g. %40 for @)
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/farm360")
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)


def run_migrations_offline() -> None:
    context.configure(
        url=DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    # Create engine directly — never goes through configparser
    connectable = create_engine(DATABASE_URL, poolclass=pool.NullPool)
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

