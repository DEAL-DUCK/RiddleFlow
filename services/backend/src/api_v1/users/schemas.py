from pydantic import BaseModel, ConfigDict, EmailStr


class UserBaseSchema(BaseModel):
    username: str
    hashed_password: str
    email: EmailStr
    role: str


class UserCreateSchema(UserBaseSchema):
    pass


class UserSchema(UserBaseSchema):
    model_config = ConfigDict(from_attributes=True)
    id: int
