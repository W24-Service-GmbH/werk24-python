import asyncio
from .client import w24_client
from werk24.models.architecture import W24Architecture
from time import time


def test_drawing_read():
    with open("./werk24/sdk/test/drawing_read_test.png", 'rb') as file_handle:
        start = time()
        response = asyncio.run(w24_client.read_drawing(
            drawing=file_handle.read(),
            ask_measures=True,
            architecture=W24Architecture.CPU_V1))
        print(response)
        end = time()
        print("Request time: {}".format(end - start))


if __name__ == "__main__":
    test_drawing_read()
