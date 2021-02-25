# Werk24 Client

[![pypi](https://img.shields.io/pypi/v/werk24.svg)](https://pypi.python.org/pypi/werk24)
[![Tests | cpython 3.7, 3.8, 3.9](https://github.com/W24-Service-GmbH/werk24-python/actions/workflows/python-test.yml/badge.svg)](https://github.com/W24-Service-GmbH/werk24-python/actions/workflows/python-test.yml)

- Understand the content of your PDF- and image-based Technical Drawings with a simple API call.

Werk24 offers an easy to use API to extract information from PDF- and image-based Technical Drawings.
With the API are able to obtain:

- Thumbnails of the Page / Canvas / Sectionals (Cuts and Perspectives)
- Measures incl. tolerances
- Geometric Dimensioning and Tolerancing Frames

Check our website at [https://www.werk24.io](https://www.werk24.io).
The project is persistently improved. Get in touch with us to obtain your API key.

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
