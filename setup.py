import re
from pathlib import Path
from setuptools import setup

VERSIONFILE = "werk24/_version.py"
NAME = "werk24"


def _get_version(version_file: str) -> str:
    """Retrieve the version string from the version file."""
    version_pattern = r"^__version__ = ['\"]([^'\"]*)['\"]"
    try:
        with open(version_file, "rt") as file_handle:
            match = re.search(version_pattern, file_handle.read(), re.M)
            if match:
                return match.group(1)
    except FileNotFoundError:
        raise RuntimeError(f"Version file '{version_file}' not found.")
    raise RuntimeError(f"Unable to find version string in '{version_file}'.")



def _get_description() -> str:
    """Read and return the long description from README.md."""
    readme_path = Path(__file__).parent / "README.md"
    with readme_path.open("r", encoding="utf-8") as file_handle:
        return file_handle.read()


setup(
    name=NAME,
    version=_get_version(VERSIONFILE),
    author="W24 Service GmbH",
    author_email="info@werk24.io",
    description=(
        "AI-powered library for extracting engineering data from PDF and "
        "image-based technical drawings, automating key detail retrieval "
        "for manufacturing workflows."
    ),
    url="https://werk24.io",
    entry_points={
        "console_scripts": [
            "w24cli=werk24.cli.w24cli:main",
        ],
    },
    license="commercial",
    packages=[
        "werk24",
        "werk24.cli",
        "werk24.models",
    ],
    include_package_data=True,
    package_data={"werk24": ["assets/*"]},
    install_requires=[
        "aiohttp>=3.10.3,<=4.0.0",
        "boto3>=1.14.44,<=2.0.0",
        "certifi>=2020.12.5,<=2025.0.0",
        "colorama>=0.4.4,<=0.5.0",
        "cryptography>=42.0.7,<=44.0.0",
        "packaging>=21.3,<=24.2",
        "pint>=0.21,<=0.25",
        "pydantic-extra-types>=2.1.0,<=3.0.0",
        "pydantic>=2.5.1,<=3.0.0",
        "python-dotenv>=1.0.1,<=2.0.0",
        "termcolor>=2.0.0,<=3.0.0",
        "websockets>=13.0,!=14.0,<15.0",
    ],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Manufacturing",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Information Technology",
        "License :: Other/Proprietary License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Image Recognition",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
    ],
    keywords=[
        "AI",
        "Artificial Intelligence",
        "Machine Learning",
        "Technical Drawing",
        "Engineering Drawing",
        "CAD",
        "Data Extraction",
        "Information Extraction",
        "Manufacturing",
        "Additive Manufacturing",
        "3D Printing",
        "Product Manufacturing Information",
        "PMI",
        "Geometric Dimensioning and Tolerancing",
        "GD&T",
        "Title Block",
        "General Tolerances",
        "Material Identification",
        "Drawing ID",
        "Drawing Designation",
        "Bill of Materials",
        "BOM",
        "Anonymization",
        "RFQ",
        "Vectorization",
        "Digitization",
        "Digitisation",
        "Computer Vision",
        "Deep Learning",
        "Automation",
        "Process Automation",
        "Manufacturing Intelligence",
        "Digital Transformation",
        "Smart Manufacturing",
        "Industrial AI",
        "Engineering Automation",
        "Technical Documentation",
        "Manufacturing Software",
        "Procurement",
        "Supplier Management",
        "Product Lifecycle Management",
        "Computer-Aided Design",
        "CAM",
        "CNC",
        "Sheet Metal",
        "Mechanical Engineering",
        "Industrial Engineering",
        "Legacy Data",
        "Document Digitization",
        "Technical Data",
        "Engineering Data",
        "Drawing Conversion",
        "Drawing Management",
        "Drawing Automation",
        "Drawing Processing",
        "Drawing Digitization",
        "Drawing Extraction",
        "Drawing Recognition",
        "Drawing Understanding",
        "Drawing Analysis",
        "Drawing Intelligence",
        "Drawing Insights",
    ],
    python_requires=">=3.9.0",
    project_urls={"Documentation": "https://docs.werk24.io/"},
    long_description_content_type="text/markdown",
    long_description=_get_description(),
)
