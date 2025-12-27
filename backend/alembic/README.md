# Alembic Migrations

## Overview

This directory contains database migrations managed by Alembic. Migrations track schema changes and allow you to upgrade/downgrade your database.

## Common Commands

```bash
# Create a new migration (auto-detect changes from models)
make db-migrate

# Apply pending migrations
make db-upgrade

# Show current migration version
make db-current

# Show migration history
alembic history
```

## Custom Types & Post-Write Hooks

### Problem: Qualified Type Names

When Alembic auto-generates migrations with custom SQLAlchemy types (like `SqidType` and `TextEnum`), it sometimes renders them with their full module path:

```python
sa.Column("id", app.utils.sqids.SqidType(), nullable=False)  # ❌ Breaks!
```

This causes `NameError: name 'app' is not defined` when running migrations because `app` isn't imported in the migration file.

### Solution: Post-Write Hook

We've implemented an automatic post-write hook (`fix_types_hook.py`) that runs after each migration is generated. It:

1. **Detects** qualified type names like `app.utils.sqids.SqidType()`
2. **Replaces** them with simple names like `SqidType()`
3. **Preserves** the correct imports (already added by `env.py`)

The hook is configured in `alembic.ini`:

```ini
[post_write_hooks]
hooks = fix_types
fix_types.type = exec
fix_types.executable = python
fix_types.options = alembic/fix_types_hook.py REVISION_SCRIPT_FILENAME
```

### Custom Type Renderers

In `env.py`, we register custom renderers for our types:

```python
@renderers.dispatch_for(SqidType)
def render_sqid_type(type_, object_, autogen_context):
    """Render SqidType with proper import in migration files."""
    autogen_context.imports.add("from app.utils.sqids import SqidType")
    return "SqidType()"
```

These renderers:
- Tell Alembic how to render the type (as `SqidType()` instead of full path)
- Automatically add the correct import statements
- Work together with the post-write hook as a safety net

## Adding New Custom Types

If you create a new custom SQLAlchemy type:

1. **Add a renderer in `env.py`:**
   ```python
   @renderers.dispatch_for(MyCustomType)
   def render_my_custom_type(type_, object_, autogen_context):
       autogen_context.imports.add("from app.path.to import MyCustomType")
       return "MyCustomType()"
   ```

2. **Add replacement in `fix_types_hook.py`:**
   ```python
   replacements = {
       "app.utils.sqids.SqidType()": "SqidType()",
       "app.state_machine.models.TextEnum()": "TextEnum()",
       "app.path.to.MyCustomType()": "MyCustomType()",  # Add this
   }
   ```

3. **Add import to `process_revision_directives` in `env.py`:**
   ```python
   def process_revision_directives(context, revision, directives):
       if directives[0].upgrade_ops:
           directives[0].imports.add("from app.path.to import MyCustomType")
   ```

## Row-Level Security (RLS)

Some migrations include RLS policies. When creating migrations that involve models with RLS:

```bash
REGISTER_RLS_POLICIES=true make db-migrate
```

This ensures RLS policies are properly registered and included in the migration.

## Troubleshooting

### "app is not defined" Error

If you get this error, the post-write hook didn't run or there's a new qualified type name:

1. **Manual fix:** Edit the migration file and replace `app.module.Type()` with `Type()`
2. **Check the import:** Ensure `from app.module import Type` is at the top
3. **Update the hook:** Add the new type to `fix_types_hook.py` replacements

### Hook Not Running

Verify the hook is configured:
```bash
grep -A 3 "\[post_write_hooks\]" alembic.ini
```

Test it manually:
```bash
python alembic/fix_types_hook.py alembic/versions/<migration_file>.py
```

### Migration Conflicts

If you have multiple branches creating migrations:
```bash
alembic merge heads -m "merge migrations"
```

## References

- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [SQLAlchemy 2.0 Documentation](https://docs.sqlalchemy.org/en/20/)
- [Root CLAUDE.md](/CLAUDE.md) - Project-wide patterns
- [Backend CLAUDE.md](/backend/CLAUDE.md) - Backend development guide
