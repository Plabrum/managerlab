from logging.config import fileConfig

from sqlalchemy import create_engine
from sqlalchemy.engine import Connection

from alembic import context
from alembic_utils.replaceable_entity import register_entities

# Import your models and config
from app import load_all_models
from app.base.models import BaseDBModel
from app.base.scope_mixins import RLS_POLICY_REGISTRY
from app.utils.configure import config as app_config

load_all_models()

# Register RLS policies for auto-diffing
register_entities(RLS_POLICY_REGISTRY)

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = BaseDBModel.metadata

# Use the sync database URL for alembic
database_url = app_config.DATABASE_URL

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    context.configure(
        url=database_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def include_object(object, name, type_, reflected, compare_to):
    """
    Exclude SAQ tables from autogenerate migrations.

    SAQ (Simple Async Queue) manages its own tables (saq_jobs, saq_stats, saq_versions).
    """
    if type_ == "table" and name.startswith("saq_"):
        return False
    return True


def do_run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        include_object=include_object,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = create_engine(database_url)

    with connectable.connect() as connection:
        do_run_migrations(connection)


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
