import sys
import os
from dotenv import load_dotenv

sys.path.append("..")
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from models.models import Users
from datetime import datetime, timedelta
from utils.hashing import verify_password
from typing import Optional

load_dotenv(".env")

SECRET_KEY = os.environ["SECRET_KEY"]
ALGORITHM = os.environ["ALGORITHM"]

oauth2_bearer = OAuth2PasswordBearer(tokenUrl="token")


def authenticate_user(username: str, password: str, db):
    user = db.query(Users) \
        .filter(Users.username == username) \
        .first()

    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(username: str, user_id: int,
                        expires_delta: Optional[timedelta] = None):
    encode = {"sub": username, "id": user_id}
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    encode.update({"exp": expire})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

