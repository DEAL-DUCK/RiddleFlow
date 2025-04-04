from fastapi import APIRouter, Depends
from services.backend.src.api_v1.users.schemas import UserSchema2, UserRole, TokenInfo
from services.backend.src.api_v1.auth.utils import validate_auth_user, create_jwt_access_token,create_jwt_refresh_token, check_roles, \
    get_current_active_auth_user
from fastapi.security import HTTPBearer
http_auth = HTTPBearer(auto_error=False)
router = APIRouter(
    prefix="/jwt", tags=["JWT"],dependencies=[Depends(http_auth)])

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
@router.post('/refresh/', response_model=TokenInfo,
             response_model_exclude_none=True)
def refresh_jwt_token():
    access_token = create_jwt_access_token()

@router.get("/creator-only/", dependencies=[Depends(check_roles([UserRole.CREATOR]))])
def creator_endpoint():
    return {"message": "Creator access granted"}


@router.get("/participant-only/", dependencies=[Depends(check_roles([UserRole.PARTICIPANT]))])
def participant_endpoint():
    return {"message": "Participant access granted"}
