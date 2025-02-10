from importlib.resources import files

FILE_PATH = files("werk24") / "assets/DRAWING_SUCCESS.png"


def get_test_drawing():
    return open(FILE_PATH, "rb")
