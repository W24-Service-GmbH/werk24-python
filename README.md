# Werk24 Client

[![pypi](https://img.shields.io/pypi/v/werk24.svg)](https://pypi.python.org/pypi/werk24)
[![Tests | cpython 3.7, 3.8, 3.9](https://github.com/W24-Service-GmbH/werk24-python/actions/workflows/python-test.yml/badge.svg)](https://github.com/W24-Service-GmbH/werk24-python/actions/workflows/python-test.yml)


- Digitize your (scanned) Enginering Drawing or Technical Drawing with a simple API call.

# Features
When submitting a PDF, PNG, JPEG of a Technical Drawing to Werk24's API, you receive within seconds
the following features:

- Measures and Tolerances
- Threads and Chamfers
- Geometric Dimensioning and Tolerancing frames
- the Title Block information (Material, Drawing ID, Designation, General Tolerances)

And finally you can obtain a CAD Approximation of the part's Geometry.
Currently this features is focused on flat parts, such as sheet metal parts, but more is in the pipeline.

Check our website at [https://www.werk24.io](https://www.werk24.io).


# Applications
Typical applications of our Technology include

- Instant Pricing on 2D Engineering Drawings
- Feasibility Checks on incoming RFQs
- Auto-Fill of Online Configurators
- Automated Anonymiziation of Technical Drawings
- Automated Supplier Scouting
- Automated Registration of incoming RFQs into your ERP system
- Structured Archiving

## Installation

Pip installation

    pip install werk24

## Documentation

See [https://werk24.io/docs/index.html](https://werk24.io/docs/index.html)

## CLI

To get a first impression, you can run the CLI:

    usage: w24cli techread [-h] [--ask-techread-started] [--ask-page-thumbnail]
                       [--ask-sheet-thumbnail] [--ask-sectional-thumbnail]
                       [--ask-variant-measures]
                       input_files

## Example

    from werk24 import Hook, W24TechreadClient, W24AskVariantMeasures

    async def read_measures_from_drawing(document_bytes:bytes) -> None:

        # define what you want to learn about the drawing, and what function
        # should be called when a response arrives
        hooks = [Hook(ask=W24AskVariantMeasures(), function=print)]

        # make the call
        client = W24TechreadClient.make_from_env()
        async with client as session:
            await session.read_drawing_with_hooks(document_bytes,hooks)
