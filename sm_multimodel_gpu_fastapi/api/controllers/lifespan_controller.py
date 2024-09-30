"""
This file contains the lifespan startup tasks for the FastAPI app
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI


@asynccontextmanager
async def startup_tasks(app: FastAPI):
    """Startup tasks for the FastAPI app

    Args:
        app (FastAPI): The FastAPI app
    """
    app.state.prediction_models = []
    yield
