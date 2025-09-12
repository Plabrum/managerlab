import msgspec


class CreateUserSchema(msgspec.Struct):
    """Schema for creating a new user."""

    email: str
    name: str
