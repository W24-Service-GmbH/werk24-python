# Werk24 Python Client

<p align="center">
  <p align="center">
    <a href="https://werk24.io/?utm_source=github&utm_medium=logo" target="_blank">
      <img src="https://github.com/W24-Service-GmbH/.github/blob/prod/profile/Werk24_banner_GitHub.png?raw=true" alt="Werk24">
    </a>
  </p>
</p>

[![PyPI version](https://img.shields.io/pypi/v/werk24.svg)](https://pypi.python.org/pypi/werk24)
[![Tests](https://github.com/W24-Service-GmbH/werk24-python/actions/workflows/python-test.yml/badge.svg)](https://github.com/W24-Service-GmbH/werk24-python/actions/workflows/python-test.yml)

## Introduction

Werk24 enables instant processing of technical drawings (PDF, PNG, JPEG) via its API.
With advanced features like automatic extraction of the MetaData, Features and Insights from Mechanical Component Drawings, Werk24 simplifies engineering workflows.

## Features

Upload a technical drawing, and within seconds, obtain:

- **Meta Data**: Drawing ID, Part ID, Designation, General Tolerances, General Roughness, Material, Weight, Bill of Material, Revision Table, Languages and Notes.
- **Features**: Dimensions incl. Tolerances, Threads, Bores, Chamfers, Roughnesses, GDnTs, Radii
- **Insights**: Manufacturing Method, Postprocesses, Input Geometry, Output Geometry
- **Redaction**: Redact information from Technical Drawings.

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

Harness Werk24 for:

- **Instant Pricing**: Automate 2D drawing-based quoting.
- **Feasibility Checks**: Evaluate RFQs efficiently.
- **Configurator Auto-Fill**: Populate online configurators with minimal input.
- **Drawing Anonymization**: Protect sensitive data in technical drawings.
- **Supplier Scouting**: Automate vendor selection for specific requirements.
- **ERP Registration**: Streamline incoming RFQ registrations.
- **Structured Archiving**: Organize drawings with metadata extraction.

## Installation

Pip installation

```bash
pip install werk24
```

## Documentation

See [https://werk24.io/docs/index.html](https://werk24.io/docs/index.html)

## CLI

To get a first impression, you can run the CLI:

```bash
$> werk24 --help
 Usage: python -m werk24.cli.werk24 [OPTIONS] COMMAND [ARGS]...

╭─ Options ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --log-level                 TEXT  Set the log level [default: INFO]                                                                                                                                        │
│ --install-completion              Install completion for the current shell.                                                                                                                                │
│ --show-completion                 Show completion for the current shell, to copy it or customize the installation.                                                                                         │
│ --help                            Show this message and exit.                                                                                                                                              │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Commands ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ init           Initialize Werk24 by providing or creating a license.                                                                                                                                       │
│ health-check   Run a comprehensive health check for the CLI.                                                                                                                                               │
│ techread       Read a drawing file and extract information.                                                                                                                                                │
│ version        Print the version of the Client.                                                                                                                                                            │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯

```

## Example

```python
from werk24 import Hook, AskMetaData, Werk24Client

async def read(drawing):
  hooks = [Hook(ask=AskMetaData(), function=print)]
  async with Werk24Client() as client:
      await client.read_drawing_with_hooks(drawing, hooks, max_pages)

asyncio.run(drawing(open("<path>","rb")))
```
