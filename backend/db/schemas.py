from pydantic import BaseModel, EmailStr  # type: ignore
from typing import List, Optional
from datetime import datetime


# ================ POSTS ================
class PostCreate(BaseModel):
    title: str
    content: str

class PostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None

class PostResponse(BaseModel):
    post_id: int
    user_id: int
    title: str
    content: str
    likes_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class PostsResponse(BaseModel):
    totalCount: int
    page: int = 1
    pageSize: int = 10
    totalPages: int = 1
    posts: List[PostResponse]


# ================ USERS ================
class UserCreate(BaseModel):
    login: str
    password: str
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    role: str = "viewer"

class UserUpdate(BaseModel):
    login: Optional[str] = None  
    email: Optional[EmailStr] = None  
    password: Optional[str] = None 
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    role: Optional[str] = None

class UserResponse(BaseModel):
    user_id: int
    login: str
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    role: str
    posts: List[PostResponse]

    class Config:
        from_attributes = True

class UserResponseLight(BaseModel):
    """Легковесный ответ пользователя без постов"""
    user_id: int
    login: str
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    role: str

    class Config:
        from_attributes = True
        
class UsersResponse(BaseModel):
    totalCount: int
    page: int = 1
    pageSize: int = 10
    totalPages: int = 1
    users: List[UserResponse]
    

# ================ JWT ================
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    login: str | None = None
