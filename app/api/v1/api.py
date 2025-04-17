from fastapi import APIRouter
from app.api.v1.endpoints import health, query, test
from app.api.v1.chat import chat_client
api_router = APIRouter()

api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(query.router, prefix="/query", tags=["query"]) 
api_router.include_router(test.router, prefix="/test", tags=["test"])
api_router.include_router(chat_client.router, prefix="/chat", tags=["chat"])