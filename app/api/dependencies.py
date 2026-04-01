from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
from uuid import UUID

from app.core.database import AsyncSessionLocal
from app.core.config import settings
from app.models.tenant import User

# The OAuth2 scheme defines where the client sends the token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_PREFIX}/identity/login")

# Database Session Injection
async def get_db() -> AsyncSession: # type: ignore
    """Yields a secure, async database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

# Authentication & Identity Extraction
import jwt
from jwt.exceptions import InvalidTokenError
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Annotated
from uuid import UUID

from app.core.database import AsyncSessionLocal
from app.core.config import settings
from app.models.tenant import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_PREFIX}/identity/login")

async def get_db() -> AsyncSession: # type: ignore
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: AsyncSession = Depends(get_db)
) -> User:
    """Validates the JWT and fetches the real user from PostgreSQL."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # 1. Cryptographically verify the token signature and expiration
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        
        if user_id is None:
            raise credentials_exception
            
    except InvalidTokenError:
        raise credentials_exception

    # 2. Query the database for the verified user ID
    try:
        parsed_uuid = UUID(user_id)
    except ValueError:
        raise credentials_exception

    result = await db.execute(select(User).where(User.id == parsed_uuid))
    user = result.scalar_one_or_none()
    
    if user is None:
        raise credentials_exception
        
    return user

async def get_current_factory_id(current_user: User = Depends(get_current_user)) -> UUID:
    return current_user.factory_id


async def get_current_factory_id(current_user: User = Depends(get_current_user)) -> UUID:
    """
    Extracts the factory ID from the authenticated user.
    This is passed to the AI state and database queries to enforce strict RLS.
    """
    return current_user.factory_id