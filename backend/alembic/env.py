from logging.config import fileConfig

from alembic_utils.replaceable_entity import register_entities
from sqlalchemy import create_engine
from sqlalchemy.engine import Connection

from alembic import context
from alembic.autogenerate import comparators
from app.base.models import BaseDBModel
from app.base.rls_comparator import compare_rls
from app.base.rls_operations import (
    DisableRLSOp,
    EnableRLSOp,
)  # noqa: F401 - needed for renderer registration
from app.base.scope_mixins import RLS_POLICY_REGISTRY
from app.utils.configure import config as app_config

# Import your models and config
from app.utils.discovery import discover_and_import
from app.utils.sqids import SqidType

discover_and_import(["models.py", "models/**/*.py"], base_path="app")


# Register RLS policies for auto-diffing, but only for tables that already exist
# This prevents simulation errors when adding new tables with RLS policies
def get_existing_policies():
    """Filter RLS_POLICY_REGISTRY to only include policies for existing tables."""
    from sqlalchemy import create_engine, inspect

    # Get list of existing tables from database
    try:
        engine = create_engine(app_config.ADMIN_DB_URL)
        inspector = inspect(engine)
        existing_tables = set(inspector.get_table_names())
        engine.dispose()
    except Exception:
        # If we can't connect to DB (e.g., offline mode), register all policies
        return RLS_POLICY_REGISTRY

    # Only register policies for tables that exist
    filtered_policies = [policy for policy in RLS_POLICY_REGISTRY if policy.on_entity.split(".")[-1] in existing_tables]
    return filtered_policies


register_entities(get_existing_policies())

# Register RLS comparator for automatic RLS enablement detection
# This comparator checks metadata.info["rls"] (populated by RLSMixin) vs database state
# and generates op.enable_rls() / op.disable_rls() operations as needed
comparators.dispatch_for("table")(compare_rls)


# Custom renderers for custom types
from alembic.autogenerate import renderers
from app.state_machine.models import TextEnum


@renderers.dispatch_for(SqidType)
def render_sqid_type(type_, object_, autogen_context):
    """Render SqidType with proper import in migration files."""
    autogen_context.imports.add("from app.utils.sqids import SqidType")
    return "SqidType()"


@renderers.dispatch_for(TextEnum)
def render_text_enum(type_, object_, autogen_context):
    """Render TextEnum with proper import in migration files."""
    autogen_context.imports.add("from app.state_machine.models import TextEnum")
    return "TextEnum()"


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
database_url = app_config.ADMIN_DB_URL

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
    Also excludes PGGrantTable objects for SAQ tables (alembic_utils doesn't use
    include_object for its own entities, so we filter by type_ and table attribute).
    """
    if type_ == "table" and name.startswith("saq_"):
        return False
    # Filter out alembic_utils PGGrantTable objects for saq_* tables
    if type_ == "grant_table" and hasattr(object, "table") and object.table.startswith("saq_"):
        return False
    return True


def process_revision_directives(context, revision, directives):
    """Post-process generated migrations to add required imports."""
    if directives[0].upgrade_ops:
        # Add imports for custom types
        directives[0].imports.add("from app.utils.sqids import SqidType")
        directives[0].imports.add("from app.state_machine.models import TextEnum")


def custom_writer(path, content):
    """Custom writer to fix qualified type names in generated migrations."""
    # Replace qualified type names with simple names (since we import them)
    content = content.replace("app.utils.sqids.SqidType()", "SqidType()")
    content = content.replace("app.state_machine.models.TextEnum()", "TextEnum()")

    # Write the modified content
    with open(path, "w") as f:
        f.write(content)
    return path


def do_run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        include_object=include_object,
        process_revision_directives=process_revision_directives,
        template_args={"script_py_writer": custom_writer},
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
