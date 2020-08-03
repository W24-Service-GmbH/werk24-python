# Werk24 Client

[![pypi](https://img.shields.io/pypi/v/werk24.svg)](https://pypi.python.org/pypi/werk24)

* Understand the content of your PDF- and image-based Technical Drawings with a simple API call.

Werk24 offers an easy to use API to extract information from PDF- and image-based Technical Drawings.
With the API are able to obtain:

* Thumbnails of the Page / Canvas / Sectionals (Cuts and Perspectives)
* Measures incl. tolerances
* Geometric Dimensioning and Tolerancing Frames

Check our website at [https://www.werk24.biz](https://www.werk24.biz).
The project is persistently improved. Get in touch with us to obtain your API key.

## Installation

Pip installation

    pip install werk24

## Documentation

See [https://werk24.github.io/docs/](https://werk24.github.io/docs/).

## CLI

To get a first impression, you can run the CLI:

    usage: w24cli techread [-h] [--ask-techread-started] [--ask-page-thumbnail]
                       [--ask-sheet-thumbnail] [--ask-sectional-thumbnail]
                       [--ask-variant-measures]
                       input_files

## Example

    import sys
    import asyncio
    from werk24 import W24TechreadClient, W24AskVariantOverallDimensions, Hook

    from werk24 import Hook, W24TechreadClient,W24AskVariantMeasures

    # get the drawing_bytes
    document_bytes = ...

    # define what you want to learn about the drawing, and what function
    # should be called when a response arrives
    hooks = [Hook(ask=W24AskVariantMeasures(), function=print)]

    # make the call
    client = W24TechreadClient.make_from_env()
    async with client as session:
        await session.read_drawing_with_hooks(document_bytes,hooks)
