"""Utility functions for the actions platform."""

import re


def class_name_to_action_key(class_name: str) -> str:
    """
    Convert a CamelCase class name to snake_case action key.

    Examples:
        RegenerateThumbnail -> regenerate_thumbnail
        DownloadCSV -> download_csv
        PublishPost -> publish_post

    Args:
        class_name: The action class name in CamelCase

    Returns:
        Action key in snake_case
    """
    # Insert underscore before uppercase letters (except at start)
    s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", class_name)
    # Insert underscore before uppercase letters followed by lowercase
    s2 = re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1)
    # Convert to lowercase
    return s2.lower()
