
from pathlib import Path


Dnn_filesDir = Path(__file__).parent

Dnn_models_path = Dnn_filesDir / "Models"

Dnn_config_default_path = Dnn_models_path / "deploy.prototxt"
Dnn_model_default_path = Dnn_models_path / "sr6033/res10_300x300_ssd_iter_140000.caffemodel"


