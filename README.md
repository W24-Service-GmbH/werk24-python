# Werk24 Client
<p align="center">
  <p align="center">
    <a href="https://werk24.io/?utm_source=github&utm_medium=logo" target="_blank">
      <img src="https://docs.werk24.io/img/logo_300px.png" alt="Werk24">
    </a>
  </p>
  <p align="center">
    Digitize your (scanned) Enginering Drawing or Technical Drawing with a simple API call.
  </p>
</p>

[![pypi](https://img.shields.io/pypi/v/werk24.svg)](https://pypi.python.org/pypi/werk24)
[![Tests | cpython 3.7, 3.8, 3.9](https://github.com/W24-Service-GmbH/werk24-python/actions/workflows/python-test.yml/badge.svg)](https://github.com/W24-Service-GmbH/werk24-python/actions/workflows/python-test.yml)



# Features
When submitting a PDF, PNG, JPEG of a Technical Drawing to Werk24's API, you receive within seconds
the following features:

- Measures and Tolerances
- Threads and Chamfers
- Geometric Dimensioning and Tolerancing frames
- the Title Block information (Material, Drawing ID, Designation, General Tolerances)

And finally you can obtain a CAD Approximation of the part's Geometry.
Currently this features is focused on flat parts, such as sheet metal parts, but more is in the pipeline.

Check our website at [https://werk24.io](https://werk24.io/?utm_source=github&utm_medium=feature_link).


<table style="width:100%">
<tr>
<td>
Input
</td>
<td>
Output
</td>
</tr>
<tr>
<td style="width:50%">
    <a href="https://werk24.io/?utm_source=github&utm_medium=drawing_input" target="_blank">
      <img src="https://docs.werk24.io/img/drawing_input.png" alt="Werk24" style="max-height:200px">
    </a>
</td>
<td style="width:50%">
    <a href="https://werk24.io/?utm_source=github&utm_medium=drawing_output" target="_blank">
      <img src="https://docs.werk24.io/img/drawing_output.png" alt="Werk24" style="max-height:200px">
    </a>
</td>
</tr>
<tr>
<td colspan="2">
    <small>Original drawing by T. Hartmann (CC)</small>
</td>
</tr>
</table>



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
