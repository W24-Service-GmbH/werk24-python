import re
from os import path

from setuptools import setup

VERSIONFILE = "werk24/_version.py"
NAME = "werk24"


def _get_version(version_file: str) -> str:
    version_pattern = r"^__version__ = ['\"]([^'\"]*)['\"]"
    with open(version_file, "rt") as file_handle:
        match = re.search(version_pattern, file_handle.read(), re.M)
    if match:
        return match.group(1)

    raise RuntimeError(
        "Unable to find version string in %s." %
        (VERSIONFILE,))


def _get_description() -> str:
    this_directory = path.abspath(path.dirname(__file__))
    with open(path.join(this_directory, 'README.md')) as file_handle:
        return file_handle.read()


setup(
    name=NAME,
    version=_get_version(VERSIONFILE),
    author="W24 Service GmbH",
    author_email="info@werk24.io",
    description="Werk24 Client to read PDF- and Image-based "
    "Technical Drawings / Engineering Drawings",
    url="https://werk24.io",
    entry_points={
        "console_scripts": [
            "w24cli=werk24.cli.w24cli:main",
            "w24gui=werk24.gui.w24gui:main",
        ]
    },
    extras_require={
        "gui": ["PyQt5", "pillow"]
    },
    license='commercial',
    packages=[
        "werk24",
        "werk24.cli",
        "werk24.gui",
        "werk24.models",
    ],
    include_package_data=True,

    package_data={"werk24": ["assets/*"]},
    install_requires=[
        "aiohttp >= 3.6.2",
        "boto3 >= 1.14.44",
        "devtools>=0.6.1",
        "pydantic >= 1.4",
        "python-dotenv>=0.10.1",
        "websockets >= 8.1"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Image Recognition"],
    keywords=[
        'Digitisation', 'Digitization', 'Engineering Drawing',
        'Engineering Drawings', 'Technical Drawing', 'Technical Drawings',
        'CAD', 'CAD Drawing', 'Data Extraction', 'Information Extraction',
        'Model Based Definition', 'EN10027', 'ISO2768', 'Title Block',
        'General Tolerances', 'Material', 'Drawing ID', 'Drawing Designation',
        'Product Manufacturing Information', 'PMI', 'Scanned Document',
        'Bill of Material', 'BOM', 'Anonymiziation', 'RFQ', 'GD&T',
        'General Dimensioning and Toleration', 'Vectorization'
    ],
    python_requires='>=3.7.1',
    project_urls={
        "Documentation": "https://docs.werk24.io/"
    },
    long_description_content_type='text/markdown',
    long_description=_get_description(),
)
