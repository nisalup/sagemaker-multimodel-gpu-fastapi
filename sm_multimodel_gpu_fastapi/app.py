"""
This is the main file for the SM_MULTIMODEL_GPU_FASTAPI API.
"""

from fastapi.responses import JSONResponse
import uvicorn
from fastapi import FastAPI, status, Request, Response

from sm_multimodel_gpu_fastapi.api.controllers.inference_controller import (
    do_inference
)
from sm_multimodel_gpu_fastapi.api.controllers.lifespan_controller import (
    startup_tasks
)
from sm_multimodel_gpu_fastapi.api.controllers.models_controller import (
    handle_model_loading
)

APP = FastAPI(
    lifespan=startup_tasks,
    title="SM_MULTIMODEL_GPU_FASTAPI",
    summary="GPU enabled multimodel inference with Fast API for AWS SageMaker",
    default_response_class=JSONResponse
)


@APP.post('/invocations')
async def invocations(request: Request):
    request_body = await request.json()
    models_list = request_body.get("models")
    await handle_model_loading(request, models_list)

    # hypothetical model response
    model_response = do_inference(
        request.app.state.prediction_models,
        request_body
    )

    response = Response(
        content=model_response,
        status_code=status.HTTP_200_OK,
        media_type="application/json",
    )
    return response


@APP.post('/ping')
async def ping():
    """Respond to the ping request

    Returns:
        Response: The response object
    """
    response = Response(
        content="OK",
        status_code=status.HTTP_200_OK,
        media_type="text/plain",
    )
    return response


if __name__ == "__main__":
    uvicorn.run(
        "main:APP",
        host="0.0.0.0",
        port=5000,
        reload=True
    )
