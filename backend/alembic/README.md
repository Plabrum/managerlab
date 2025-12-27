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

## Custom Types & Type Renderers

### Problem: Qualified Type Names

When Alembic auto-generates migrations with custom SQLAlchemy types (like `SqidType` and `TextEnum`), it can render them with their full module path:

```python
sa.Column("id", app.utils.sqids.SqidType(), nullable=False)  # ❌ Breaks!
```

This causes `NameError: name 'app' is not defined` when running migrations because `app` isn't imported in the migration file.

### Solution: Custom Type Renderers

In `env.py`, we've implemented a `render_item` callback that handles our custom types:

```python
def render_item(type_, obj, autogen_context):
    if type_ == "type" and isinstance(obj, TypeDecorator):
        class_name = obj.__class__.__name__

        if class_name == "SqidType":
            autogen_context.imports.add("from app.utils.sqids import SqidType")
            return "SqidType()"

        elif class_name == "TextEnum":
            autogen_context.imports.add("from app.state_machine.models import TextEnum")
            return "TextEnum()"

    return False  # Let Alembic handle everything else
```

This renderer:
- Detects custom TypeDecorator subclasses during migration generation
- Returns the simple type name (e.g., `SqidType()`)
- Automatically adds the correct import statement
- Prevents qualified type names from appearing in migrations

## Adding New Custom Types

If you create a new custom SQLAlchemy TypeDecorator:

1. **Add a case to `render_item` in `env.py`:**
   ```python
   def render_item(type_, obj, autogen_context):
       if type_ == "type" and isinstance(obj, TypeDecorator):
           class_name = obj.__class__.__name__

           # Add your new type here
           if class_name == "MyCustomType":
               autogen_context.imports.add("from app.path.to import MyCustomType")
               return "MyCustomType()"

           # ... existing types ...

       return False
   ```

That's it! The type will now render correctly in migrations with proper imports.

## Row-Level Security (RLS)

Some migrations include RLS policies. RLS policies are automatically registered when creating migrations for models with RLS support (those inheriting from `TeamScopedBase` or `CampaignScopedBase`). Simply use the standard migration command:

```bash
make db-migrate
```

## Troubleshooting

### "app is not defined" Error

If you get this error, a custom type wasn't handled by `render_item`:

1. **Manual fix:** Edit the migration file and replace `app.module.Type()` with `Type()`
2. **Check the import:** Ensure `from app.module import Type` is at the top
3. **Update `render_item`:** Add the new type to the `render_item` function in `env.py`

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
