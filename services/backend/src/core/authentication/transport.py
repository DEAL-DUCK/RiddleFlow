from fastapi_users.authentication import BearerTransport

bearer_transport = BearerTransport(
    tokenUrl="auth/jwt/login",
)
