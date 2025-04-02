from jwt.exceptions import InvalidTokenError
from fastapi import APIRouter, Depends, Form, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from services.backend.src.api_v1.auth import utils as auth_utils
from services.backend.src.api_v1.users.schemas import UserSchema2, UserRole

# Инициализация OAuth2 схемы для JWT аутентификации
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/demo-auth/jwt/login/")

# Модель для возврата JWT токена
class TokenInfo(BaseModel):
    access_token: str
    token_type: str

# Создание роутера для JWT-эндпоинтов
router = APIRouter(prefix="/jwt", tags=["JWT"])

# Тестовые пользователи в памяти
john = UserSchema2(
    username="john",
    password=auth_utils.hash_password("qwerty"),
    email="john@example.com",
    role = UserRole.PARTICIPANT
)
sam = UserSchema2(
    username="sam",
    password=auth_utils.hash_password("secret"),
    role = UserRole.CREATOR
)
users_db: dict[str, UserSchema2] = {john.username: john, sam.username: sam}

# Проверка учетных данных пользователя
def validate_auth_user(username: str = Form(), password: str = Form()):
    unauthed_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="invalid username or password",
    )
    if not (user := users_db.get(username)):
        raise unauthed_exc

    if not auth_utils.validate_password(password=password, hashed_password=user.password):
        raise unauthed_exc

    if not user.active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="user inactive")
    return user

# Декодирование JWT токена
def get_current_token_payload(token: str = Depends(oauth2_scheme)) -> dict:
    try:
        return auth_utils.decode_jwt(token=token)
    except InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"invalid token error: {e}",
        )

# Получение текущего пользователя из JWT
def get_current_auth_user(payload: dict = Depends(get_current_token_payload)) -> UserSchema2:
    if user := users_db.get(payload.get("sub")):
        return user
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="token invalid (user not found)")

# Проверка активности пользователя
def get_current_active_auth_user(user: UserSchema2 = Depends(get_current_auth_user)):
    if user.active:
        return user
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="user inactive")

# Эндпоинт для входа и получения JWT
@router.post("/login/", response_model=TokenInfo)
def auth_user_issue_jwt(user: UserSchema2 = Depends(validate_auth_user)):
    token = auth_utils.encode_jwt({
        "sub": user.role,
        "username": user.username,
        "email": user.email,
    })
    return TokenInfo(access_token=token, token_type="Bearer")

# Эндпоинт для получения информации о текущем пользователе
@router.get("/users/me/")
def auth_user_check_self_info(
    payload: dict = Depends(get_current_token_payload),
    user: UserSchema2 = Depends(get_current_active_auth_user),
):
    return {
        "username": user.username,
        "email": user.email,
        "logged_in_at": payload.get("iat"),
    }