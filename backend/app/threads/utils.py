import msgspec

from app.threads.schemas import ClientMessage, ServerMessage


def get_thread_channel(thread_id: int) -> str:
    return f"thread_{thread_id}"


def decode_client_message(data: bytes | str) -> ClientMessage:
    if isinstance(data, str):
        data = data.encode("utf-8")
    return msgspec.json.Decoder(ClientMessage).decode(data)


def encode_server_message_str(message: ServerMessage) -> str:
    return msgspec.json.Encoder().encode(message).decode("utf-8")
