"""
Authentication routes.
"""
from fastapi import APIRouter, HTTPException, status
from app.schemas.user import UserCreate, UserLogin, Token, UserResponse
from app.core.security import hash_password, verify_password, create_access_token
from app.db.mongodb import get_database
from datetime import datetime, timezone

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


def _serialize_user(user):
    user["_id"] = str(user["_id"])
    user.pop("hashed_password", None)
    return user


@router.post("/register", response_model=Token)
async def register(data: UserCreate):
    db = get_database()

    # Check if email exists
    existing = await db.users.find_one({"email": data.email})
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Create user
    user_doc = {
        "email": data.email,
        "name": data.name,
        "hashed_password": hash_password(data.password),
        "age": data.age,
        "gender": data.gender,
        "created_at": datetime.now(timezone.utc),
    }
    result = await db.users.insert_one(user_doc)
    user_doc["_id"] = result.inserted_id

    # Generate token
    token = create_access_token({"sub": str(result.inserted_id)})
    return Token(access_token=token, user=UserResponse(**_serialize_user(user_doc)))


@router.post("/login", response_model=Token)
async def login(data: UserLogin):
    db = get_database()
    user = await db.users.find_one({"email": data.email})
    if not user or not verify_password(data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    token = create_access_token({"sub": str(user["_id"])})
    return Token(access_token=token, user=UserResponse(**_serialize_user(user)))
