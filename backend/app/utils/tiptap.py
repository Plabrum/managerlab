"""TipTap rich text utilities for creating formatted content."""

from typing import Any


def text(content: str) -> dict[str, Any]:
    """
    Create a plain text node.

    Args:
        content: The text content

    Returns:
        TipTap text node
    """
    return {"type": "text", "text": content}


def bold(content: str) -> dict[str, Any]:
    """
    Create a bold text node.

    Args:
        content: The text content to make bold

    Returns:
        TipTap text node with bold mark
    """
    return {"type": "text", "text": content, "marks": [{"type": "bold"}]}


def paragraph(*nodes: dict[str, Any]) -> dict[str, Any]:
    """
    Create a paragraph containing text nodes.

    Args:
        *nodes: Variable number of text nodes (from text() or bold())

    Returns:
        TipTap paragraph node
    """
    return {"type": "paragraph", "content": list(nodes)}


def doc(*paragraphs: dict[str, Any]) -> dict[str, Any]:
    """
    Create a TipTap document.

    Args:
        *paragraphs: Variable number of paragraph nodes

    Returns:
        Complete TipTap document structure
    """
    return {"type": "doc", "content": list(paragraphs)}


def text_to_tiptap(plain_text: str) -> dict[str, Any]:
    """
    Convert plain text to TipTap document format.

    Handles multi-line text by creating multiple paragraphs.

    Args:
        plain_text: Plain text string (may contain newlines)

    Returns:
        TipTap document
    """
    # Split by newlines and create a paragraph for each line
    lines = plain_text.split("\n")
    paragraphs = [paragraph(text(line)) for line in lines if line.strip()]

    # If no lines, create a single empty paragraph
    if not paragraphs:
        paragraphs = [paragraph(text(""))]

    return doc(*paragraphs)
