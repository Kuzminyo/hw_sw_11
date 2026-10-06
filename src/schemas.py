from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

PHONE_PATTERN = r"^\+?[0-9\s\-()]{7,20}$"


def _check_birthday(value: date | None) -> date | None:
    if value is not None and value > date.today():
        raise ValueError("Birthday cannot be in the future")
    return value


class ContactBase(BaseModel):
    first_name: str = Field(min_length=1, max_length=50, examples=["Taras"])
    last_name: str = Field(min_length=1, max_length=50, examples=["Shevchenko"])
    email: EmailStr = Field(examples=["taras@example.com"])
    phone: str = Field(pattern=PHONE_PATTERN, examples=["+380501234567"])
    birthday: date = Field(examples=["1990-03-09"])
    additional_info: str | None = Field(default=None, max_length=1000)


class ContactCreate(ContactBase):
    _validate_birthday = field_validator("birthday")(_check_birthday)


class ContactUpdate(BaseModel):
    """All fields are optional: only the provided ones are updated."""

    first_name: str | None = Field(default=None, min_length=1, max_length=50)
    last_name: str | None = Field(default=None, min_length=1, max_length=50)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, pattern=PHONE_PATTERN)
    birthday: date | None = None
    additional_info: str | None = Field(default=None, max_length=1000)

    _validate_birthday = field_validator("birthday")(_check_birthday)


class ContactResponse(ContactBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
