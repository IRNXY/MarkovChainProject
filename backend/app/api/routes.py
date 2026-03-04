from fastapi import APIRouter
from .v1.endpoints import markov_generation


api_router = APIRouter()

api_router.include_router(markov_generation.router)
