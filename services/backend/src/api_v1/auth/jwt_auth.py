from fastapi import APIRouter, Depends
from services.backend.src.api_v1.users.schemas import UserSchema2, UserRole, TokenInfo
from services.backend.src.api_v1.auth.utils import validate_auth_user, create_jwt_token, check_roles, \
    get_current_active_auth_user

router = APIRouter(prefix="/jwt", tags=["JWT"])


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
