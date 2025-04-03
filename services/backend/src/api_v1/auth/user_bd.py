from services.backend.src.api_v1.users.schemas import UserSchema2, UserRole
import bcrypt
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