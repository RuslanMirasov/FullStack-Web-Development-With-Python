from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, PastDate


class ContactModel(BaseModel):
    first_name: str = Field(min_length=1, max_length=50)
    last_name: str = Field(min_length=1, max_length=50)
    email: EmailStr = Field(max_length=100)
    phone: str = Field(
        min_length=7,
        max_length=20,
        pattern=r"^\+?[\d\s\-()]+$",
        examples=["+38 (000) 000-00-00"],
    )
    birthday: PastDate
    additional_data: str | None = Field(default=None, max_length=250)


class ContactResponse(ContactModel):
    id: int
    created_at: datetime | None
    updated_at: datetime | None

    model_config = ConfigDict(from_attributes=True)


class User(BaseModel):
    id: int
    username: str
    email: str
    avatar: str | None

    model_config = ConfigDict(from_attributes=True)


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr = Field(max_length=100)
    password: str = Field(min_length=6, max_length=72)


class Token(BaseModel):
    access_token: str
    token_type: str


class RequestEmail(BaseModel):
    email: EmailStr