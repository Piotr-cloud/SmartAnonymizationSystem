
from pathlib import Path

EasyOCR_filesDir = Path(__file__).parent

EasyOCR_data_dir      =   EasyOCR_filesDir / "data/ocr"
EasyOCR_darknet_dir   =   EasyOCR_filesDir / "darknet"

EasyOCR_config_filePath    =   EasyOCR_data_dir / "ocr-net.cfg"
EasyOCR_weights_filePath   =   EasyOCR_data_dir / "ocr-net.weights"
EasyOCR_dataset_filePath   =   EasyOCR_data_dir / "ocr-net.data"
EasyOCR_names_filePath     =   EasyOCR_data_dir / "ocr-net.names"

EasyOCR_DLL_filePath = EasyOCR_darknet_dir / "libdarknet.so"


EasyOCR_tempImgFile_fileName  = "tempImg.jpg"


