from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api_v1 import router as router_v1

app = FastAPI()
app.include_router(router=router_v1, prefix="/api")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
