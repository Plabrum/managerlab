from app.base.schemas import BaseSchema


class CreateUserSchema(BaseSchema):
    name: str
    email: str


class UserWaitlistFormSchema(BaseSchema):
    name: str
    email: str
    company: str | None = None
    message: str | None = None
