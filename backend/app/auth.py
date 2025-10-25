from datetime import datetime, timedelta
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from passlib.hash import bcrypt
from sqlalchemy.orm import Session
from .settings import settings
from .database import SessionLocal
from . import models

security = HTTPBearer()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def hash_password(pw: str) -> str:
    return bcrypt.hash(pw)

def verify_password(pw: str, pw_hash: str) -> bool:
    return bcrypt.verify(pw, pw_hash)

def create_token(payload: dict, expires_minutes: int = 60*24) -> str:
    data = payload.copy()
    data["exp"] = datetime.utcnow() + timedelta(minutes=expires_minutes)
    return jwt.encode(data, settings.JWT_SECRET, algorithm=settings.JWT_ALG)

def current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)) -> models.User:
    token = credentials.credentials
    try:
        data = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALG])
    except Exception:
        raise HTTPException(401, "Invalid or expired token")
    user = db.query(models.User).filter_by(id=data.get("uid")).first()
    if not user:
        raise HTTPException(401, "User not found")
    return user

def require_role(*roles):
    def checker(user: models.User = Depends(current_user)):
        if user.role not in roles:
            raise HTTPException(403, "Forbidden")
        return user
    return checker