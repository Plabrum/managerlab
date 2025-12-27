#!/usr/bin/env python3
"""Post-write hook to fix qualified type names in generated migrations.

This hook runs after Alembic generates a migration file and replaces
fully-qualified type names with their simple imported forms.

Usage: python fix_types_hook.py <migration_file_path>
"""

import sys


def main():
    """Fix qualified type names in the generated migration file."""
    if len(sys.argv) < 2:
        print("Error: Migration file path required", file=sys.stderr)
        sys.exit(1)

    filename = sys.argv[1]

    # Read the generated migration file
    with open(filename) as f:
        content = f.read()

    # Replace fully qualified type names with simple names
    # (the imports are already added by process_revision_directives in env.py)
    replacements = {
        "app.utils.sqids.SqidType()": "SqidType()",
        "app.state_machine.models.TextEnum()": "TextEnum()",
    }

    modified = False
    for qualified_name, simple_name in replacements.items():
        if qualified_name in content:
            content = content.replace(qualified_name, simple_name)
            modified = True
            print(f"✓ Replaced {qualified_name} with {simple_name}", file=sys.stderr)

    # Write back the modified content if changes were made
    if modified:
        with open(filename, "w") as f:
            f.write(content)
        print(f"✓ Fixed qualified type names in {filename}", file=sys.stderr)
    else:
        print(f"✓ No qualified type names to fix in {filename}", file=sys.stderr)


if __name__ == "__main__":
    main()
