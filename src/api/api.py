from fastapi import APIRouter

from api.api_evaluation import api_evaluation

api = APIRouter(prefix="/api")
api.include_router(api_evaluation)
