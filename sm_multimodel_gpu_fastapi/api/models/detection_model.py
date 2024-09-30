from typing import Any
from datetime import datetime


class DetectionModel():
    def __init__(self, model_name) -> None:
        self.model_name = model_name
        self.last_called_time = datetime.now()
        self.model = self.load_model()

    def load_model(self) -> Any:
        model = "<Load you model here>"  # Add function to load the model here
        return model
