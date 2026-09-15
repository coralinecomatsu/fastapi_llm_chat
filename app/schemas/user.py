from pydantic import BaseModel, Field, field_validator, EmailStr
from pydantic import ConfigDict

class UserCreate(BaseModel):
    email: EmailStr
    # password: str = Field(min_length=8)
    name: str = Field(min_length=1, max_length=50)
    age: int = Field(ge=0, le=150)

    @field_validator('name')
    @classmethod
    def strip_name(cls, v: str) -> str:
        return v.strip()

    # @field_validator('password')
    # @classmethod
    # def has_digit(cls, v: str) -> str:
    #     if not any(char.isdigit() for char in v):
    #         raise ValueError("Password must contain only digits")
    #     return v

class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    email: EmailStr
    name: str | None
    age: int
