from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, EmailStr


class RegisterReq(BaseModel):
    email: EmailStr
    password: str


class RegisterResp(BaseModel):
    user_id: str
    email: str
    created_at: datetime


class LoginReq(BaseModel):
    email: EmailStr
    password: str


class LoginResp(BaseModel):
    user_id: str
    email: str
