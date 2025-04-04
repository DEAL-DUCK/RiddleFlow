import jwt
from fastapi import APIRouter, Depends,HTTPException
from services.backend.src.api_v1.users.schemas import UserSchema2, UserRole, TokenInfo
from services.backend.src.api_v1.auth.utils import validate_auth_user, create_jwt_access_token,create_jwt_refresh_token, check_roles, \
    get_current_active_auth_user,load_public_key
from fastapi.security import HTTPBearer,HTTPAuthorizationCredentials
http_auth = HTTPBearer(auto_error=False)
http_bearer_refresh = HTTPBearer(auto_error=False, scheme_name="RefreshToken")
from services.backend.src.api_v1.auth.user_bd import users_db
router = APIRouter(
    prefix="/jwt", tags=["JWT"],dependencies=[Depends(http_auth),Depends(http_bearer_refresh)])


@router.post("/login/", response_model=TokenInfo)
def auth_user_issue_jwt(user: UserSchema2 = Depends(validate_auth_user)):
    token_payload_access = {
        "sub": user.username,
        "role": user.sub.value,
        "email": user.email,
        'token_type': 'access',
    }
    token_payload_refresh = {
        "sub": user.username,
        "role": user.sub.value,
        'token_type': 'refresh',
    }
    access_token = create_jwt_access_token(token_payload_access)
    refresh_token = create_jwt_refresh_token(token_payload_refresh)
    return TokenInfo(access_token=access_token,refresh_token=refresh_token)


@router.get("/users/me/")
def get_current_user_info(user: UserSchema2 = Depends(get_current_active_auth_user)):
    return {
        "username": user.username,
        "email": user.email,
        "role": user.sub.value
    }



def get_refresh_token_payload(
    credentials: HTTPAuthorizationCredentials = Depends(http_bearer_refresh)
) -> dict:
    token = credentials.credentials
    public_key = load_public_key()
    payload = jwt.decode(token,public_key,algorithms=['RS256'])
    if payload.get("token_type") != "refresh":
        raise HTTPException(status_code=400, detail="Need refresh token")
    return payload
@router.post('/refresh/', response_model=TokenInfo,
             response_model_exclude_none=True)
def refresh_jwt_token(
    payload: dict = Depends(get_refresh_token_payload)
):
    try:
        user = users_db.get(payload.get("sub"))
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        new_access_token = create_jwt_access_token({
            "sub": user.username,
            "role": user.sub.value,
            "email": user.email,
            "token_type": "access",
        })
    except AttributeError:
        raise HTTPException(status_code=400, detail="Need refresh token")
    return TokenInfo(access_token=new_access_token)

@router.get("/creator-only/", dependencies=[Depends(check_roles([UserRole.CREATOR])),Depends(get_current_active_auth_user)])
def creator_endpoint():
    return {"message": "Creator access granted"}


@router.get("/participant-only/", dependencies=[Depends(check_roles([UserRole.PARTICIPANT])),Depends(get_current_active_auth_user)])
def participant_endpoint():
    return {"message": "Participant access granted"}
