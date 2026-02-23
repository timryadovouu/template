from fastapi import APIRouter, Depends, HTTPException, status  # type: ignore
from fastapi.security import OAuth2PasswordRequestForm  # type: ignore
from sqlalchemy.orm import Session  # type: ignore
from typing import Annotated
import os

from auth.auth import create_access_token, get_current_user
from auth.utils import get_password_hash, verify_password
from db.database import get_db
from db.models import User
from db.schemas import Token
from db.schemas import UserCreate, UserResponse
from db.schemas import PostResponse


router = APIRouter(tags=["Authentication"])

ADMIN_REGISTRATION_KEY = os.getenv("ADMIN_REGISTRATION_KEY")
REST_KEY = os.getenv("REST_KEY")


@router.post("/register", response_model=Token)
async def register(
    user: UserCreate,
    db: Session = Depends(get_db)
):
    db_user = db.query(User).filter(User.login == user.login).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Login already registered")     
    hashed_password = get_password_hash(user.password)
    new_user = User(
        login=user.login,   
        email=user.email,
        hashed_password=hashed_password,
        first_name=user.first_name,
        last_name=user.last_name,
        phone=user.phone,
        role=user.role
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    access_token = create_access_token(data={"sub": new_user.login})

    return Token(
        access_token=access_token,
        token_type="bearer"
    )


@router.post("/login", response_model=Token)
async def login(
    user_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db)
):

    user = db.query(User).filter(User.login == user_data.username).first()

    if not user or not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect login or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": user.login})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/api/me", response_model=UserResponse)
async def get_me(
    current_user: Annotated[User, Depends(get_current_user)]
) -> UserResponse:
    return current_user
