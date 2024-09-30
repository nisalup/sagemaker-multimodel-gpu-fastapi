"""
This file should have the model class/fucntions that will be
used for loading the model.
Note that this is not a complete implementation and you will need to
add the actual model loading logic.
"""
from typing import Any
from datetime import datetime


class DetectionModel():
    """
    Dummy class for loading the model.
    """
    def __init__(self, model_name: str) -> None:
        """Constructor for the DetectionModel class

        Args:
            model_name (str): The name of the model
        """
        self.model_name = model_name
        self.last_called_time = datetime.now()
        self.model = self.load_model()

    def load_model(self) -> Any:
        """Dummy function to load the model

        Returns:
            Any: The loaded model
        """
        model = "<Load you model here>"  # Add function to load the model here
        return model
