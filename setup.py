from setuptools import setup


setup(
    name="werk24",
    version="0.1.6",
    author="Jochen Mattes",
    packages=["werk24", "werk24.models"],
    install_requires=["websockets"]
)
