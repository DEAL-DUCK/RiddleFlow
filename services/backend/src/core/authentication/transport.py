from fastapi_users.authentication import BearerTransport

bearer_transport = BearerTransport(
    tokenUrl="/api/v1/auth/login",
)
