from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, EmailStr, validator
import re
from uuid import uuid4

from app.core.database import get_db
from app.core.security import verify_password, create_access_token, get_password_hash
from app.models.tenant import User

router = APIRouter()

# Pydantic Schemas 
# We define strict JSON schemas that perfectly match the React frontend payloads

class UserLogin(BaseModel):
    email: EmailStr
    password: str

    @validator('email')
    def validate_email_com(cls, v):
        # v could be a string or EmailStr object (which is a string subclass)
        email_str = str(v)
        if not email_str.endswith('.com'):
            raise ValueError('Only .com emails are allowed')
        return v

class UserRegister(BaseModel):
    name: str
    contact_number: str
    email: EmailStr
    password: str

    @validator('email')
    def validate_email_com(cls, v):
        email_str = str(v)
        if not email_str.endswith('.com'):
            raise ValueError('Only .com emails are allowed')
        return v

    @validator('name')
    def validate_name(cls, v):
        if not re.match(r"^[A-Za-z\s]+$", v):
            raise ValueError('Name should only contain alphabets and spaces')
        return v

    @validator('contact_number')
    def validate_contact_number(cls, v):
        if not re.match(r"^\d+$", v):
            raise ValueError('Contact number strictly requires integers')
        return v


# Endpoints 

@router.post("/login", tags=["Authentication"])
async def login_for_access_token(
    credentials: UserLogin, 
    db: AsyncSession = Depends(get_db)
):
    """Authenticates a user via JSON payload and returns a JWT Bearer token."""
    
    # Look up the user by email
    result = await db.execute(select(User).where(User.email == credentials.email))
    user = result.scalar_one_or_none()

    # Verify existence and password
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Generate the JWT
    access_token = create_access_token(
        data={"sub": str(user.id)} # Store the user UUID as the subject
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/register", tags=["Authentication"])
async def register_new_user(
    user_data: UserRegister, 
    db: AsyncSession = Depends(get_db)
):
    """Creates a new user, automatically handling the factory assignment."""
    
    # Check if user already exists
    existing_user = await db.execute(select(User).where(User.email == user_data.email))
    if existing_user.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")

    # Hash the password using bcrypt
    hashed_pw = get_password_hash(user_data.password)
    default_factory_id = uuid4()
    
    # Create the user record
    new_user = User(
        name=user_data.name,
        contact_number=user_data.contact_number,
        email=user_data.email,
        hashed_password=hashed_pw,
        factory_id=default_factory_id,
        role="admin", 
    )
    
    db.add(new_user)
    await db.commit()
    
    return {"status": "success", "message": "User securely created."}