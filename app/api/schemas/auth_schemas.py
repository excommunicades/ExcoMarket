from pydantic import BaseModel, EmailStr, constr, model_validator


class RegisterSchema(BaseModel):

    nickname: constr(min_length=3, max_length=64)
    email: EmailStr
    password: constr(min_length=8, max_length=128)
    confirm_password: str

    @model_validator(mode="after")
    def passwords_match(self):
        if self.password != self.confirm_password:
            raise ValueError("Passwords do not match")
        return self


class LoginSchema(BaseModel):

    nickname_or_email: str
    password: str


class UserResponse(BaseModel):

    id: int
    nickname: str
    email: EmailStr

    model_config = {
        "from_attributes": True
    }
