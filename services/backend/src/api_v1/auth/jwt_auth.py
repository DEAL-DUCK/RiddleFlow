from datetime import datetime, timedelta
from typing import List
from fastapi import APIRouter, Depends, Form, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import bcrypt
import jwt
from jwt.exceptions import InvalidTokenError
from pathlib import Path
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from services.backend.src.api_v1.users.schemas import UserSchema2, UserRole, TokenInfo

router = APIRouter(prefix="/jwt", tags=["JWT"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api_v1/jwt/login/")
JWT_CONFIG = {
    "ALGORITHM": "RS256",
    "ACCESS_TOKEN_EXPIRE_MINUTES": 30,
    "REFRESH_TOKEN_EXPIRE_DAYS": 7
}

KEYSDIR = Path(__file__).parent.parent.parent.parent.parent.parent / "keys"

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


john = UserSchema2(
    username="john",
    password=bcrypt.hashpw(b"qwerty", bcrypt.gensalt()),
    sub=UserRole.PARTICIPANT,
    email="john@example.com",
    active=True
)

sam = UserSchema2(
    username="sam",
    password=bcrypt.hashpw(b"secret", bcrypt.gensalt()),
    sub=UserRole.CREATOR,
    email="sam@example.com",
    active=True
)

users_db = {john.username: john, sam.username: sam}

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

def create_jwt_token(payload: dict, expires_delta: timedelta = None) -> str:
    to_encode = payload.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=JWT_CONFIG["ACCESS_TOKEN_EXPIRE_MINUTES"]))
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

def get_current_auth_user(payload: dict = Depends(get_current_token_payload)) -> UserSchema2:
    if user := users_db.get(payload.get("sub")):
        return user
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

@router.post("/login/", response_model=TokenInfo)
def auth_user_issue_jwt(user: UserSchema2 = Depends(validate_auth_user)):
    token_payload = {
        "sub": user.username,
        "role": user.sub.value,
        "email": user.email
    }
    token = create_jwt_token(token_payload)
    return TokenInfo(access_token=token, token_type="Bearer")



@router.get("/users/me/")
def get_current_user_info(user: UserSchema2 = Depends(get_current_active_auth_user)):
    return {
        "username": user.username,
        "email": user.email,
        "role": user.sub.value
    }

@router.get("/creator-only/", dependencies=[Depends(check_roles([UserRole.CREATOR]))])
def creator_endpoint():
    return {"message": "Creator access granted"}

@router.get("/participant-only/", dependencies=[Depends(check_roles([UserRole.PARTICIPANT]))])
def participant_endpoint():
    return {"message": "Participant access granted"}