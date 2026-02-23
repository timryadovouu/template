from fastapi import APIRouter, Depends, HTTPException, status, Query  # type: ignore
from sqlalchemy.orm import Session  # type: ignore
from typing import Optional, Literal, Annotated
from datetime import datetime
from sqlalchemy import or_, and_  # type: ignore

from backend.auth.auth import get_current_user
from backend.db.database import get_db
from backend.auth.utils import get_password_hash
from backend.db.models import User, Post
from backend.db.schemas import PostsResponse
from backend.db.schemas import UserResponse, UsersResponse, UserUpdate, UserResponseLight


router = APIRouter(tags=["Users"])


@router.get("/api/users/{user_id}/posts", response_model=PostsResponse)
def get_user_posts(
    user_id: int,
    page: int = Query(1, ge=1),
    pageSize: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):

    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    query = db.query(Post).filter(Post.user_id == user_id)
    query = query.order_by(Post.created_at.desc())
    
    total_count = query.count()
    offset = (page - 1) * pageSize
    posts = query.offset(offset).limit(pageSize).all()
    total_pages = (total_count + pageSize - 1) // pageSize

    return PostsResponse(
        totalCount=total_count,
        page=page,
        pageSize=pageSize,
        totalPages=total_pages,
        posts=posts
    )


@router.get("/api/users", response_model=UsersResponse)
def get_all_users(
    page: int = Query(1, ge=1),
    pageSize: int = Query(10, ge=1, le=100),
    role: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(User)
    
    if role:
        query = query.filter(User.role == role)
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                User.login.ilike(search_term),
                User.email.ilike(search_term),
                User.first_name.ilike(search_term),
                User.last_name.ilike(search_term)
            )
        )
    
    query = query.order_by(User.user_id.asc())
    
    total_count = query.count()
    offset = (page - 1) * pageSize
    users = query.offset(offset).limit(pageSize).all()
    total_pages = (total_count + pageSize - 1) // pageSize

    return UsersResponse(
        totalCount=total_count,
        page=page,
        pageSize=pageSize,
        totalPages=total_pages,
        users=users
    )


@router.get("/api/users/{user_id}", response_model=UserResponseLight)
def get_user(
    user_id: int,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


@router.patch("/api/users/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own profile"
        )
    
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    update_data = user_data.model_dump(exclude_unset=True)
    
    if "login" in update_data and update_data["login"] != user.login:
        existing_user = db.query(User).filter(User.login == update_data["login"]).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Login already exists"
            )
    
    if "email" in update_data and update_data["email"] != user.email:
        existing_user = db.query(User).filter(User.email == update_data["email"]).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already exists"
            )
    
    if "password" in update_data:
        update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
    
    for field, value in update_data.items():
        setattr(user, field, value)
    
    db.commit()
    db.refresh(user)
    return user


@router.delete("/api/users/{user_id}", status_code=status.HTTP_200_OK)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own profile"
        )
    
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user_login = user.login
    
    db.delete(user)
    db.commit()
    
    return {
        "message": f"User '{user_login}' deleted successfully",
        "user_id": user_id
    }
