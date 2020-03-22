from setuptools import setup


setup(
    name="werk24",
    version="0.1.6",
    author="Jochen Mattes",
    packages=["werk24", "werk24.models"],
    install_requires=[
        "aioboto3 >= 6.5.0",
        "pydantic >= 1.4",
        "python-dotenv>=0.10.1",
        "websockets >= 8.1"],
    scripts=['w24cli']
)
