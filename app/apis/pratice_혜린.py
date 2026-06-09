import re

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, field_validator

router = APIRouter(
    prefix="/practice_api",
    tags=["practice_혜린"],
)

user_list = [
    {
        "id": 1,
        "name": "홍길동",
        "age": 24,
        "email": "gildong24@example.com",
        "password": "Password1234!!",
    },
    {
        "id": 2,
        "name": "문럭",
        "age": 21,
        "email": "moonluck12@example.com",
        "password": "Check1321!",
    },
    {
        "id": 3,
        "name": "임우지",
        "age": 31,
        "email": "limousine33@example.com",
        "password": "lwsPAssword12@",
    },
]

def validate_email_format(value):
    email_regex = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    if not re.match(email_regex, value):
        raise ValueError("Invalid email format")
    return value


def validate_password_format(value):
    if not re.search(r"[A-Z]", value):
        raise ValueError("Password must contain at least one uppercase letter")
    if not re.search(r"[a-z]", value):
        raise ValueError("Password must contain at least one lowercase letter")
    if not re.search(r"[^A-Za-z0-9]", value):
        raise ValueError("Password must contain at least one special character")
    return value

class UserCreateRequest(BaseModel):
    name: str = Field(min_length=2, max_length=10)
    age: int = Field(ge=14)
    email: str = Field(max_length=30)
    password: str = Field(min_length=8, max_length=20)

    @field_validator("email")
    @classmethod
    def validate_email(cls, value):
        return validate_email_format(value)

    @field_validator("password")
    @classmethod
    def validate_password(cls, value):
        return validate_password_format(value)

class UserUpdateRequest(BaseModel):
    age: int | None = Field(default=None, ge=14)
    email: str | None = Field(default=None, max_length=30)
    password: str | None = Field(default=None, min_length=8, max_length=20)

    @field_validator("email")
    @classmethod
    def validate_email(cls, value):
        if value is None:
            return value
        return validate_email_format(value)

    @field_validator("password")
    @classmethod
    def validate_password(cls, value):
        if value is None:
            return value
        return validate_password_format(value)
    

    @field_validator("password")
    @classmethod
    def validate_password(cls, value):
        if value is None:
            return value

        if not re.search(r"[A-Z]", value):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", value):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"[^A-Za-z0-9]", value):
            raise ValueError("Password must contain at least one special character")

        return value


def remove_password(user):
    return {
        key: value
        for key, value in user.items()
        if key != "password"
    }


def get_user_list_not_pwd():
    return [remove_password(user) for user in user_list]


def email_check(email):
    for user in user_list:
        if user["email"] == email:
            raise HTTPException(status_code=400, detail="Email already exists")


@router.get("/users")
def get_users_handler():
    return get_user_list_not_pwd()


@router.get("/users/{user_id}")
def get_user_handler(user_id: int):
    for user in user_list:
        if user["id"] == user_id:
            return remove_password(user)

    raise HTTPException(status_code=404, detail="User not found")


@router.post("/users")
def create_user_handler(body: UserCreateRequest):
    email_check(body.email)

    new_user = {
        "id": max([user["id"] for user in user_list], default=0) + 1,
        "name": body.name,
        "age": body.age,
        "email": body.email,
        "password": body.password,
    }

    user_list.append(new_user)

    return remove_password(new_user)

@router.patch("/users/{user_id}")
def update_user_handler(user_id: int, body: UserUpdateRequest):
    if body.age is None and body.email is None and body.password is None:
        raise HTTPException(status_code=400, detail="At least one field is required")
    for user in user_list:
        if user["id"] == user_id:
            if body.age is not None:
                user["age"] = body.age
            if body.email is not None:
                     user["email"] = body.email
            if body.password is not None:
                user["password"] = body.password
        return remove_password(user)
			

# 회원의 id 값을 path parameter로 입력받아 특정 회원의 정보를 삭제하는 API
# endpoint
    # practice_api/users/{user_id: int}
# id 값으로 조회되는 회원의 정보를 user_list 에서 삭제.
# 유효한 id 가 아닌 경우 404 Not Found 를 응답으로 반환.
@router.delete("/users/{user_id}")
def delete_user_handler(user_id: int):
    for user in user_list:
        if user["id"] == user_id:
            user_list.remove(user)
            return {"message":"User deleted"}
    raise HTTPException(status_code=404, detail="User not found")