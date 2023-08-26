from pathlib import Path


exampleProvider_dir         =  Path(__file__).parent

faceExamples_dir            =  exampleProvider_dir / "Face"
licensePlateExamples_dir    =  exampleProvider_dir / "Plate"

faceExample_path            =  faceExamples_dir / "Face_example.jpeg"
licensePlateExample_path    =  licensePlateExamples_dir / "Plate_example.png"
