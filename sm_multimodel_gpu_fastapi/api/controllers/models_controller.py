"""
This file contains the main logic for handling models in the API.
"""

from datetime import datetime
import gc

from fastapi import Request
import logging as log

from sm_multimodel_gpu_fastapi.api.models.detection_model import DetectionModel


# Maximum number of models that can be loaded at a time,
# this can be adjusted based on the available memory and on
# the requirements of your models.
MAX_LOADED_MODELS = 20


def handle_model_loading(
    request: Request,
    models_list: list[str]
):
    """
    Handles the loading of models based on the given request and inference
    request body.

    Args:
        request (Request): incoming request object from fastapi
        models_list (list[str]): list of model names to load

    Raises:
        Exception: if the number of models in the request exceeds the maximum
            allowed number of models per single request

    """
    prediction_models: list[DetectionModel] = \
        request.app.state.prediction_models

    if len(models_list) > MAX_LOADED_MODELS:
        raise Exception(
            f"""
            Number of models in request ({len(models_list)}) exceeds the
            maximum allowed number of models ({MAX_LOADED_MODELS}) per
            single request
            """
        )
    log.info(
        f"""
        Current loaded model count: {len(prediction_models)}/{
            MAX_LOADED_MODELS
        }
        """
    )
    non_loaded_models = __get_non_loaded_models_from_prediction_models(
        models_list,
        prediction_models
    )
    if non_loaded_models:
        (
            should_models_be_unloaded,
            num_models_to_unload
        ) = __should_models_be_unloaded(
            prediction_models,
            len(non_loaded_models)
        )
        if should_models_be_unloaded:
            get_model_names_to_unload = __get_model_names_to_unload(
                prediction_models,
                num_models_to_unload
            )
            for model_name in get_model_names_to_unload:
                __unload_model(model_name, request)

        for model_name in non_loaded_models:
            loaded_model = __load_model(
                model_name
            )
            request.app.state.prediction_models.append(loaded_model)
            log.info(
                f"""
                Model {model_name} loaded into memory
                Current loaded model count: {len(prediction_models)}/{
                    MAX_LOADED_MODELS
                }
                """
            )
    else:
        for existing_model_name in models_list:
            __update_model_called_time(request, existing_model_name)


def __load_model(
    model_name: str,
) -> DetectionModel:
    """This function loads a model into memory.

    Args:
        model_name (str): name of the model to load

    Returns:
        LoadedModel: loaded model
    """
    log.info(f"Loading model {model_name} into memory...")
    return DetectionModel(model_name)


def __unload_model(
    model_name_to_unload: str,
    request: Request
) -> None:
    """This function unloads a model from memory.

    Args:
        model_name_to_unload (str): name of the model to unload
        request (Request): incoming request object from fastapi
    """
    request.app.state.prediction_models = [
        model for model in request.app.state.prediction_models
        if model.model_name != model_name_to_unload
    ]

    gc.collect()
    log.info(f"Model {model_name_to_unload} unloaded from memory.")


def __should_models_be_unloaded(
    prediction_models: list[DetectionModel],
    non_loaded_models_len: int
) -> tuple[bool, int]:
    """This function checks if models should be unloaded from memory.

    Args:
        prediction_models (list[LoadedModel]): list of loaded models
        non_loaded_models_len (int): number of models to be loaded

    Returns:
        tuple[bool, int]: a tuple containing a boolean and an integer
    """
    num_total_models = len(prediction_models) + non_loaded_models_len
    return (
        num_total_models > MAX_LOADED_MODELS,
        num_total_models - MAX_LOADED_MODELS
    )


def __get_model_names_to_unload(
    prediction_models: list[DetectionModel],
    num_models_to_unload: int
) -> list[str]:
    """This function returns a list of model names to unload by getting the
        name of the models that have been called the time farthest away.

    Args:
        prediction_models (list[LoadedModel]): list of loaded models
        num_models_to_unload (int): number of models to unload

    Returns:
        list[str]: list of model names to unload
    """
    sorted_models = sorted(
        prediction_models,
        key=lambda model: model.last_called_time
    )
    return [model.model_name for model in sorted_models[:num_models_to_unload]]


def __get_non_loaded_models_from_prediction_models(
    models_list: list[str],
    prediction_models: list[DetectionModel]
) -> list[str]:
    """This function returns a list of models that are not loaded.

    Args:
        models_list (list[str]): list of model names
        prediction_models (list[LoadedModel]): list of loaded models

    Returns:
        list[str]: list of models that are not loaded
    """
    return [
        model for model in models_list if
        model not in [model.model_name for model in prediction_models]
    ]


def __update_model_called_time(request: Request, model_name: str) -> None:
    """This function updates the last called time of a model.

    Args:
        request (Request): the request object from fastapi
        model_name (str): name of the model to update
    """
    prediction_models: list[DetectionModel] = \
        request.app.state.prediction_models
    for model in prediction_models:
        if model.model_name == model_name:
            model.last_called_time = datetime.now()
            break
    request.app.state.prediction_models = prediction_models
    log.info(f"Model {model_name} last called time updated.")
