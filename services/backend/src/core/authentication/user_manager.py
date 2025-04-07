import logging
from typing import Optional
from typing import TYPE_CHECKING
from fastapi_users import BaseUserManager, IntegerIDMixin

from core.config import settings
from core.types.user_id import UserIdType
from core.models import User

log = logging.getLogger(__name__)

if TYPE_CHECKING:
    from fastapi import Request


class UserManager(IntegerIDMixin, BaseUserManager[User, UserIdType]):
    reset_password_token_secret = settings.access_token.reset_password_token_secret
    verification_token_secret = settings.access_token.verification_token_secret

    async def on_after_register(self, user: User, request: Optional["Request"] = None):
        log.warning(
            "User %r has registered.",
            user.id,
        )
