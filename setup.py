from os import path
from setuptools import setup

NAME = "werk24"
VERSION = "0.2.2"

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md')) as f:
    long_description = f.read()

setup(
    name=NAME,
    version=VERSION,
    author="W24 Service GmbH",
    author_email="info@werk24.biz",
    description="Werk24 Client to read PDF- and Image-based "
    "Technical Drawings / Engineering Drawings",
    url="https://www.werk24.biz",
    entry_points={
        "console_scripts": [
            "w24cli=werk24.cli.w24cli:main",
        ]
    },
    license='Business Source License 1.1',
    packages=[
        "werk24",
        "werk24.models",
        "werk24.cli"],
    install_requires=[
        "aioboto3 >= 6.4.1",
        "pydantic >= 1.4",
        "python-dotenv>=0.10.1",
        "websockets >= 8.1"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Image Recognition"],
    python_requires='>=3.7.4',
    project_urls={
        "Documentation": "https://werk24.github.io/docs/"
    },
    long_description_content_type='text/markdown',
    long_description=long_description,
)
