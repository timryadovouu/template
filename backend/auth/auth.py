from datetime import datetime, timedelta, timezone  # type: ignore
from fastapi import Depends, HTTPException, status  # type: ignore
from sqlalchemy.orm import Session  # type: ignore
from fastapi.security import OAuth2PasswordBearer  # type: ignore
from jwt.exceptions import InvalidTokenError  # type: ignore
from typing import Annotated
import jwt  # type: ignore
import os

from db.database import get_db
from db.models import User
from db.schemas import TokenData


SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_TTL = int(os.getenv("ACCESS_TOKEN_TTL"))  # minutes

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

# Function to create a JWT access token
def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_TTL)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Function to verify and decode JWT token
async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Session = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        login = payload.get("sub")
        if login is None:
            raise credentials_exception
        token_data = TokenData(login=login)
    except InvalidTokenError:
        raise credentials_exception

    user = db.query(User).filter(User.login == token_data.login).first()
    if user is None:
        raise credentials_exception
    return user
