"""WebSocket message schemas for thread real-time communication.

This module defines all WebSocket message types using msgspec for strict typing
and efficient serialization. Messages use a discriminated union pattern with
a 'type' field to identify the message variant.
"""

from enum import StrEnum

import msgspec
from msgspec import Struct

from app.utils.sqids import Sqid


class MessageUpdateType(StrEnum):
    """Type of message update."""

    CREATED = "created"
    UPDATED = "updated"
    DELETED = "deleted"


# Viewer presence information
class ViewerInfo(Struct, frozen=True):
    """Information about a user viewing a thread."""

    user_id: int
    name: str
    is_typing: bool


# ============================================================================
# Client → Server Messages
# ============================================================================


class TypingMessage(Struct, frozen=True, tag="typing"):
    """Client typing indicator update."""

    is_typing: bool


class MarkReadMessage(Struct, frozen=True, tag="mark_read"):
    """Client request to mark thread as read."""

    pass


# Union of all client message types
ClientMessage = TypingMessage | MarkReadMessage


# ============================================================================
# Server → Client Messages
# ============================================================================


class UserJoinedMessage(Struct, frozen=True, tag="user_joined"):
    """Server notification that a user joined the thread."""

    user_id: int
    viewers: list[ViewerInfo]


class UserLeftMessage(Struct, frozen=True, tag="user_left"):
    """Server notification that a user left the thread."""

    user_id: int
    viewers: list[ViewerInfo]


class TypingUpdateMessage(Struct, frozen=True, tag="typing_update"):
    """Server notification that a user's typing status changed."""

    user_id: int
    is_typing: bool
    viewers: list[ViewerInfo]


class MessageUpdateMessage(Struct, frozen=True, tag="message_update"):
    """Server notification that a message was created, updated, or deleted."""

    update_type: MessageUpdateType
    message_id: Sqid
    thread_id: Sqid
    user_id: Sqid  # Sqid(0) for system messages
    viewers: list[ViewerInfo] = []  # Default empty, will be populated by notify_thread


class MarkedReadMessage(Struct, frozen=True, tag="marked_read"):
    """Server confirmation that thread was marked as read."""

    viewers: list[ViewerInfo] = []  # Default empty, will be populated when needed


# Union of all server message types
ServerMessage = (
    UserJoinedMessage
    | UserLeftMessage
    | TypingUpdateMessage
    | MessageUpdateMessage
    | MarkedReadMessage
)


# ============================================================================
# Serialization Utilities
# ============================================================================

# Create encoder/decoder with discriminator on 'type' field
_client_decoder = msgspec.json.Decoder(ClientMessage)
_server_encoder = msgspec.json.Encoder()


def decode_client_message(data: bytes | str) -> ClientMessage:
    """Decode a client WebSocket message from JSON.

    Args:
        data: JSON string or bytes to decode

    Returns:
        Decoded client message of appropriate type

    Raises:
        msgspec.ValidationError: If message is invalid or unknown type
    """
    if isinstance(data, str):
        data = data.encode("utf-8")
    return _client_decoder.decode(data)


def encode_server_message(message: ServerMessage) -> bytes:
    """Encode a server WebSocket message to JSON bytes.

    Args:
        message: Server message to encode

    Returns:
        JSON bytes ready to send over WebSocket
    """
    return _server_encoder.encode(message)


def encode_server_message_str(message: ServerMessage) -> str:
    """Encode a server WebSocket message to JSON string.

    Args:
        message: Server message to encode

    Returns:
        JSON string ready to send over WebSocket
    """
    return encode_server_message(message).decode("utf-8")
