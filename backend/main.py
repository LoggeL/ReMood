from fastapi import FastAPI, Depends, HTTPException, status, Form
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional, List
from jose import jwt
from passlib.context import CryptContext
from pydantic import BaseModel
import random
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from .database.database import get_db, SessionLocal
from .database.models import Base, User, MoodEntry, Category
from .database.database import engine
from .utils.encryption import generate_key_from_password, encrypt_text, decrypt_text

# Create database tables
Base.metadata.create_all(bind=engine)


# Create demo data
def create_demo_data(db: Session):
    # Check if demo user exists
    demo_user = db.query(User).filter(User.username == "demo").first()
    if demo_user:
        return

    # Create demo user
    hashed_password = pwd_context.hash("demo")
    key, salt = generate_key_from_password("demo")
    demo_user = User(
        username="demo", hashed_password=hashed_password, encryption_key=key.decode()
    )
    db.add(demo_user)
    db.commit()
    db.refresh(demo_user)

    # Sample entries data
    sample_entries = [
        {
            "content": "Heute war ein wundervoller Tag! Das Wetter war perfekt für einen Spaziergang im Park. Ich habe mich mit einem alten Freund getroffen und wir hatten tolle Gespräche.",
            "mood_score": 5,
            "is_encrypted": True,  # Private entry
            "is_breakdown": False,
            "category": Category.SOCIAL,
            "days_ago": 0,
        },
        {
            "content": "Fühle mich heute etwas gestresst wegen der Arbeit. Zu viele Deadlines auf einmal. Aber ich schaffe das!",
            "mood_score": 3,
            "is_encrypted": True,  # Private entry
            "is_breakdown": False,
            "category": Category.WORK,
            "days_ago": 1,
        },
        {
            "content": "Heute war ein schwerer Tag. Nichts lief wie geplant und ich fühle mich überfordert. Brauche dringend eine Pause.",
            "mood_score": 1,
            "is_encrypted": True,  # Private entry
            "is_breakdown": True,
            "category": Category.PERSONAL,
            "days_ago": 2,
        },
        {
            "content": "Mein neues Hobby macht so viel Spaß! Ich hätte nie gedacht, dass Malen so entspannend sein kann. Teile diesen Erfolg gerne mit allen!",
            "mood_score": 5,
            "is_encrypted": False,  # Public entry
            "is_breakdown": False,
            "category": Category.PERSONAL,
            "days_ago": 3,
        },
        {
            "content": "Ein ganz normaler Tag. Nichts Besonderes passiert, aber das ist auch mal okay.",
            "mood_score": 3,
            "is_encrypted": True,  # Private entry
            "is_breakdown": False,
            "category": Category.GENERAL,
            "days_ago": 4,
        },
        {
            "content": "Hatte heute ein tolles Erfolgserlebnis bei der Arbeit. Mein Chef hat mein Projekt sehr gelobt!",
            "mood_score": 4,
            "is_encrypted": False,  # Public entry
            "is_breakdown": False,
            "category": Category.WORK,
            "days_ago": 5,
        },
        {
            "content": "Fühle mich heute etwas einsam. Vermisse meine Familie, die weit weg wohnt. Sollte sie mal wieder besuchen.",
            "mood_score": 2,
            "is_encrypted": True,  # Private entry
            "is_breakdown": False,
            "category": Category.FAMILY,
            "days_ago": 6,
        },
        {
            "content": "Kompletter Breakdown heute. Alles ist zu viel. Die Panikattacke kam aus dem Nichts...",
            "mood_score": 1,
            "is_encrypted": True,  # Private entry
            "is_breakdown": True,
            "category": Category.HEALTH,
            "days_ago": 7,
        },
        {
            "content": "Endlich wieder Sport gemacht! Es fühlt sich so gut an, aktiv zu sein. Teile diese Motivation gerne mit anderen!",
            "mood_score": 4,
            "is_encrypted": False,  # Public entry
            "is_breakdown": False,
            "category": Category.HEALTH,
            "days_ago": 8,
        },
        {
            "content": "Meditation hilft mir wirklich sehr. Heute war eine besonders gute Session.",
            "mood_score": 4,
            "is_encrypted": True,  # Private entry
            "is_breakdown": False,
            "category": Category.HEALTH,
            "days_ago": 9,
        },
    ]

    # Add entries
    for entry in sample_entries:
        content = entry["content"]
        if entry["is_encrypted"]:
            content = encrypt_text(content, demo_user.encryption_key.encode())

        entry_date = datetime.utcnow() - timedelta(
            days=entry["days_ago"],
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59),
        )

        db_entry = MoodEntry(
            user_id=demo_user.id,
            date=entry_date,
            mood_score=entry["mood_score"],
            content=content,
            category=entry["category"],
            is_encrypted=entry["is_encrypted"],
            is_breakdown=entry["is_breakdown"],
            created_at=entry_date,
            updated_at=entry_date,
        )
        db.add(db_entry)

    db.commit()


# Initialize FastAPI app
app = FastAPI(title="ReMood API")


# Create demo data on startup
@app.on_event("startup")
async def startup_event():
    db = SessionLocal()
    try:
        create_demo_data(db)
    finally:
        db.close()


# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# JWT settings
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30"))


# Pydantic Models
class UserCreate(BaseModel):
    username: str
    password: str


class MoodEntryCreate(BaseModel):
    mood_score: int
    content: str
    category: Category = Category.GENERAL
    is_encrypted: bool = True
    is_breakdown: bool = False
    date: datetime = None


class MoodEntryResponse(BaseModel):
    id: int
    date: datetime
    mood_score: int
    content: str
    category: Category
    is_encrypted: bool
    is_breakdown: bool
    created_at: datetime
    username: str
    decryption_failed: bool = False

    class Config:
        from_attributes = True


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except jwt.JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    return user


@app.post("/register")
async def register(
    username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.username == username).first()
    if user:
        raise HTTPException(status_code=400, detail="Username already registered")

    hashed_password = pwd_context.hash(password)
    key, salt = generate_key_from_password(password)

    new_user = User(
        username=username, hashed_password=hashed_password, encryption_key=key.decode()
    )
    db.add(new_user)
    db.commit()
    return {"message": "User created successfully"}


@app.post("/token")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not pwd_context.verify(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/api/entries", response_model=MoodEntryResponse)
async def create_mood_entry(
    entry: MoodEntryCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    content = entry.content
    if entry.is_encrypted:
        content = encrypt_text(content, current_user.encryption_key.encode())

    entry_date = entry.date or datetime.utcnow()

    db_entry = MoodEntry(
        user_id=current_user.id,
        mood_score=entry.mood_score,
        content=content,
        category=entry.category,
        is_encrypted=entry.is_encrypted,
        is_breakdown=entry.is_breakdown,
        date=entry_date,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)

    # Decrypt content if it was encrypted
    if db_entry.is_encrypted:
        db_entry.content = decrypt_text(
            db_entry.content, current_user.encryption_key.encode()
        )

    # Return response with username
    return MoodEntryResponse(**{**db_entry.__dict__, "username": current_user.username})


@app.get("/api/entries", response_model=List[MoodEntryResponse])
async def get_mood_entries(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    entries = (
        db.query(MoodEntry)
        .filter(MoodEntry.user_id == current_user.id)
        .order_by(MoodEntry.date.desc())
        .all()
    )

    # Decrypt encrypted entries and add username
    result = []
    for entry in entries:
        try:
            if entry.is_encrypted:
                entry.content = decrypt_text(
                    entry.content, current_user.encryption_key.encode()
                )
            # Convert to response model with username
            result.append(
                MoodEntryResponse(
                    **{**entry.__dict__, "username": current_user.username}
                )
            )
        except Exception as e:
            # If decryption fails, mark the entry as failed but still include it
            entry.content = (
                "Entschlüsselung fehlgeschlagen. Bitte melden Sie sich erneut an."
            )
            result.append(
                MoodEntryResponse(
                    **{
                        **entry.__dict__,
                        "username": current_user.username,
                        "decryption_failed": True,
                    }
                )
            )

    return result


@app.get("/api/public-entries", response_model=List[MoodEntryResponse])
async def get_public_entries(db: Session = Depends(get_db)):
    entries = (
        db.query(MoodEntry, User.username)
        .join(User, MoodEntry.user_id == User.id)
        .order_by(MoodEntry.date.desc())
        .all()
    )

    return [
        MoodEntryResponse(
            **{
                **entry[0].__dict__,
                "username": entry[1],
                "content": (
                    "Dieser Eintrag ist privat"
                    if entry[0].is_encrypted
                    else entry[0].content
                ),
            }
        )
        for entry in entries
    ]


@app.get("/api/users/{username}/public-entries", response_model=List[MoodEntryResponse])
async def get_user_public_entries(username: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    entries = (
        db.query(MoodEntry)
        .filter(MoodEntry.user_id == user.id)
        .order_by(MoodEntry.date.desc())
        .all()
    )

    return [
        MoodEntryResponse(
            **{
                **entry.__dict__,
                "username": username,
                "content": (
                    "Dieser Eintrag ist privat" if entry.is_encrypted else entry.content
                ),
            }
        )
        for entry in entries
    ]


@app.put("/api/entries/{entry_id}", response_model=MoodEntryResponse)
async def update_mood_entry(
    entry_id: int,
    entry: MoodEntryCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Find the entry
    db_entry = (
        db.query(MoodEntry)
        .filter(MoodEntry.id == entry_id, MoodEntry.user_id == current_user.id)
        .first()
    )

    if not db_entry:
        raise HTTPException(status_code=404, detail="Eintrag nicht gefunden")

    # Update content with encryption if needed
    content = entry.content
    if entry.is_encrypted:
        content = encrypt_text(content, current_user.encryption_key.encode())

    # Update the entry
    db_entry.mood_score = entry.mood_score
    db_entry.content = content
    db_entry.category = entry.category
    db_entry.is_encrypted = entry.is_encrypted
    db_entry.is_breakdown = entry.is_breakdown
    db_entry.date = entry.date
    db_entry.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(db_entry)

    # Decrypt content if it was encrypted for the response
    if db_entry.is_encrypted:
        db_entry.content = decrypt_text(
            db_entry.content, current_user.encryption_key.encode()
        )

    # Return response with username
    return MoodEntryResponse(**{**db_entry.__dict__, "username": current_user.username})


# Mount static files
app.mount("/", StaticFiles(directory="frontend", html=True), name="static")
