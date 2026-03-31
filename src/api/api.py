from fastapi import APIRouter

from api.api_evaluation import api_evaluation
from api.api_jeopardy import api_jeopardy

api = APIRouter(prefix="/api")
api.include_router(api_evaluation)
api.include_router(api_jeopardy)
