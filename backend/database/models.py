from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    Text,
    Boolean,
    Enum,
)
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import enum


class Category(str, enum.Enum):
    GENERAL = "general"
    WORK = "work"
    FAMILY = "family"
    HEALTH = "health"
    SOCIAL = "social"
    PERSONAL = "personal"


Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    encryption_key = Column(String)  # Encrypted with user's password
    created_at = Column(DateTime, default=datetime.utcnow)


class MoodEntry(Base):
    __tablename__ = "mood_entries"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    date = Column(DateTime, default=datetime.utcnow)
    mood_score = Column(Integer)  # 1-5 scale
    content = Column(Text)  # Main content of the entry
    category = Column(Enum(Category), default=Category.GENERAL)
    is_encrypted = Column(Boolean, default=True)  # Whether the content is encrypted
    is_breakdown = Column(Boolean, default=False)  # Whether this is a breakdown entry
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
