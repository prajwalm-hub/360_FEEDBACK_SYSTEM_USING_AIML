"""
Authentication and Authorization Module
Handles JWT tokens, password hashing, and user authentication
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import secrets

from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from .database import get_database, User
from .config import settings


# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
SECRET_KEY = getattr(settings, 'SECRET_KEY', secrets.token_urlsafe(32))
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

# HTTP Bearer for token authentication
security = HTTPBearer()


def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token
    
    Args:
        data: Payload data (should include 'sub' with user ID)
        expires_delta: Token expiration time
        
    Returns:
        Encoded JWT token
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt


def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Decode and validate a JWT token
    
    Args:
        token: JWT token string
        
    Returns:
        Decoded payload or None if invalid
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


def authenticate_user(username: str, password: str, db: Session) -> Optional[User]:
    """
    Authenticate a user by username and password
    
    Args:
        username: Username or email
        password: Plain text password
        db: Database session
        
    Returns:
        User object if authenticated, None otherwise
    """
    # Try to find user by username or email
    user = db.query(User).filter(
        (User.username == username) | (User.email == username)
    ).first()
    
    if not user:
        return None
    
    if not verify_password(password, user.password_hash):
        return None
    
    if not user.is_active:
        return None
    
    return user


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> User:
    """
    Get current authenticated user from JWT token
    
    Args:
        credentials: HTTP Bearer token
        db: Database session
        
    Returns:
        Current user object
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token = credentials.credentials
    payload = decode_access_token(token)
    
    if payload is None:
        raise credentials_exception
    
    user_id: str = payload.get("sub")
    if user_id is None:
        raise credentials_exception
    
    db = get_database()
    with db.get_session() as session:
        user = session.query(User).filter(User.id == user_id).first()
    
        if user is None:
            raise credentials_exception
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive"
            )
        
        return user


def get_current_pib_officer(current_user: User = Depends(get_current_user)) -> User:
    """
    Require current user to be a PIB officer
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        User object if PIB officer
        
    Raises:
        HTTPException: If user is not a PIB officer
    """
    if current_user.role != 'pib_officer':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="PIB Officer privileges required"
        )
    return current_user


def create_user(
    username: str,
    email: str,
    password: str,
    full_name: str,
    region: Optional[str] = None,
    languages: Optional[list] = None,
    phone: Optional[str] = None,
    department: Optional[str] = None,
    db: Session = None
) -> User:
    """
    Create a new PIB officer user
    
    Args:
        username: Unique username
        email: Email address
        password: Plain text password (will be hashed)
        full_name: Full name
        region: Region (for PIB officers)
        languages: Languages monitored (for PIB officers)
        phone: Phone number
        department: Department
        db: Database session
        
    Returns:
        Created user object
    """
    password_hash = hash_password(password)
    
    user = User(
        username=username,
        email=email,
        password_hash=password_hash,
        full_name=full_name,
        role='pib_officer',  # All users are PIB officers
        region=region,
        languages=languages,
        phone=phone,
        department=department,
        is_active=True,
        is_verified=True
    )
    
    if db:
        db.add(user)
        db.commit()
        db.refresh(user)
    
    return user


# Optional: Dependency for getting current user without raising exception
def get_optional_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db = Depends(lambda: get_database().get_session())
) -> Optional[User]:
    """Get current user if authenticated, None otherwise"""
    if not credentials:
        return None
    
    try:
        token = credentials.credentials
        payload = decode_access_token(token)
        
        if payload is None:
            return None
        
        user_id: str = payload.get("sub")
        if user_id is None:
            return None
        
        user = db.query(User).filter(User.id == user_id).first()
        
        if user and user.is_active:
            return user
        
        return None
    except Exception:
        return None
