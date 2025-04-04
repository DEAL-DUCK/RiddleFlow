from datetime import datetime, timedelta
from typing import List
from fastapi import  Depends, Form, HTTPException, status
import bcrypt
import jwt
from services.backend.src.api_v1.auth.user_bd import users_db
from jwt.exceptions import InvalidTokenError
from pathlib import Path
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from fastapi.security import OAuth2PasswordBearer
from services.backend.src.core.config import JWT_CONFIG
from services.backend.src.api_v1.users.schemas import UserSchema2,UserRole
KEYSDIR = Path(__file__).parent.parent.parent.parent.parent.parent / "keys"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api_v1/jwt/login/")

def load_private_key():
    private_key_path = KEYSDIR / "private_key.pem"
    if not private_key_path.exists():
        raise FileNotFoundError(f"Private key not found at {private_key_path}")
    with open(private_key_path, "rb") as key_file:
        return serialization.load_pem_private_key(
            key_file.read(),
            password=None,
            backend=default_backend()
        )

def load_public_key():
    public_key_path = KEYSDIR / "public_key.pem"
    if not public_key_path.exists():
        raise FileNotFoundError(f"Public key not found at {public_key_path}")
    with open(public_key_path, "rb") as key_file:
        return serialization.load_pem_public_key(
            key_file.read(),
            backend=default_backend()
        )




def validate_auth_user(username: str = Form(), password: str = Form()):
    unauthed_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid username or password",
    )
    if not (user := users_db.get(username)):
        raise unauthed_exc
    if not bcrypt.checkpw(password.encode(), user.password):
        raise unauthed_exc
    if not user.active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User inactive")
    return user

def create_jwt_access_token(payload: dict, expires_delta: timedelta = None) -> str:
    to_encode = payload.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=JWT_CONFIG["ACCESS_TOKEN_EXPIRE_MINUTES"]))
    to_encode.update({"exp": expire})
    private_key = load_private_key()
    return jwt.encode(to_encode, private_key, algorithm=JWT_CONFIG["ALGORITHM"])

def create_jwt_refresh_token(payload: dict, expires_delta: timedelta = None) -> str:
    to_encode = payload.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(days=JWT_CONFIG["REFRESH_TOKEN_EXPIRE_DAYS"]))
    to_encode.update({"exp": expire})
    private_key = load_private_key()
    return jwt.encode(to_encode, private_key, algorithm=JWT_CONFIG["ALGORITHM"])

def decode_jwt_token(token: str) -> dict:
    public_key = load_public_key()
    return jwt.decode(token, public_key, algorithms=[JWT_CONFIG["ALGORITHM"]])

def get_current_token_payload(token: str = Depends(oauth2_scheme)) -> dict:
    try:
        return decode_jwt_token(token)
    except InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {e}",
        )

def validation_token_type(payload: dict,token_type : str) -> bool:
    if payload.get('token_type') == token_type:
        return True
    if payload.get('token_type') != token_type:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                          detail=f'invalid token type: {payload.get("token_type")}')
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

def get_current_auth_user(payload: dict = Depends(get_current_token_payload)) -> UserSchema2:
    user = users_db.get(payload.get("sub"))
    if user and payload.get('token_type') == 'access':
        return user
    if payload.get('token_type') != 'access':
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                          detail=f'invalid token type: {payload.get("token_type")}')
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
def get_current_auth_user_for_refresh(payload: dict = Depends(get_current_token_payload)) -> UserSchema2:
    user = users_db.get(payload.get("sub"))
    if user and payload.get('token_type') == 'refresh':
        return user
    if payload.get('token_type') != 'access':
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                          detail=f'invalid token type: {payload.get("token_type")}')
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


def get_current_active_auth_user(user: UserSchema2 = Depends(get_current_auth_user)):
    if user.active:
        return user
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User inactive")

def check_roles(required_roles: List[UserRole]):
    def role_checker(user: UserSchema2 = Depends(get_current_active_auth_user)):
        if user.sub not in required_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return user
    return role_checker
