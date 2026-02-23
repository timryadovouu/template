from sqlalchemy import Column, Integer, String, Text, Boolean, TIMESTAMP, CheckConstraint, ForeignKey  # type: ignore
from sqlalchemy.orm import relationship  # type: ignore
from sqlalchemy.sql import func  # type: ignore
from db.database import Base


class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True)
    login = Column(String(255), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=True)
    hashed_password = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    phone = Column(String(20), nullable=True)
    role = Column(String(50), nullable=False, server_default="viewer")

    posts = relationship(
        "Post",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True
    )


class Post(Base):
    __tablename__ = "posts"

    post_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    likes_count = Column(Integer, server_default="0")
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp())

    user = relationship(
        "User",
        back_populates="posts",
    )
