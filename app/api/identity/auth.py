from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.security import verify_password, create_access_token , get_password_hash
from app.models.tenant import User

router = APIRouter()

@router.post("/login", tags=["Authentication"])
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """Authenticates a user and returns a JWT Bearer token."""
    
    # 1. Look up the user by email (OAuth2 uses 'username' field for the identifier)
    result = await db.execute(select(User).where(User.email == form_data.username))
    user = result.scalar_one_or_none()

    # 2. Verify existence and password
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 3. Generate the JWT
    access_token = create_access_token(
        data={"sub": str(user.id)} # Store the user UUID as the subject
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

from pydantic import BaseModel
from uuid import UUID

# Schema for incoming registration data
class UserRegister(BaseModel):
    email: str
    password: str
    factory_id: UUID
    role: str = "admin"

@router.post("/register", tags=["Authentication"])
async def register_new_user(
    user_data: UserRegister, 
    db: AsyncSession = Depends(get_db)
):
    """Creates a new user with a mathematically hashed password."""
    
    # Check if user already exists
    existing_user = await db.execute(select(User).where(User.email == user_data.email))
    if existing_user.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")

    # Hash the password using bcrypt
    hashed_pw = get_password_hash(user_data.password)
    
    # Create the user record
    new_user = User(
        email=user_data.email,
        hashed_password=hashed_pw,
        factory_id=user_data.factory_id,
        role=user_data.role
    )
    
    db.add(new_user)
    await db.commit()
    
    return {"status": "success", "message": "User securely created."}