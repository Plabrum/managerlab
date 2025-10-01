"""Objects framework initialization.

This module auto-discovers all object classes to ensure they are registered
with the ObjectRegistry via BaseObject.__init_subclass__.

Object classes automatically register themselves when they are imported,
so we just need to ensure all object files are imported at startup.
"""

from app.utils.discovery import discover_and_import

# Auto-discover all object files to trigger registration
discover_and_import(["objects.py", "objects/**/*.py"], base_path="app")
