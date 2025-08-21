<p align="center">
  <a href="https://werk24.io/?utm_source=github&utm_medium=logo" target="_blank">
    <img src="https://github.com/W24-Service-GmbH/.github/blob/prod/profile/Werk24_banner_GitHub.png?raw=true" alt="Werk24">
  </a>
</p>

# Werk24 Python Client

Unlock manufacturing intelligence from technical drawings with AI.

[![PyPI version](https://img.shields.io/pypi/v/werk24.svg)](https://pypi.python.org/pypi/werk24)
![Python Version](https://img.shields.io/pypi/pyversions/werk24.svg)
![License](https://img.shields.io/badge/license-commercial-blue)
[![Downloads](https://img.shields.io/pypi/dm/werk24.svg)](https://pypi.python.org/pypi/werk24)
[![Tests](https://github.com/W24-Service-GmbH/werk24-python/actions/workflows/python-test.yml/badge.svg)](https://github.com/W24-Service-GmbH/werk24-python/actions/workflows/python-test.yml)

## Table of Contents

- [Overview](#overview)
- [Why Werk24?](#why-werk24)
- [Features](#features)
- [Applications](#applications)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Documentation](#documentation)
- [Community & Support](#community--support)
- [Contributing](#contributing)
- [License](#license)

## Overview

Werk24 provides AI-powered solutions for extracting and interpreting technical drawings.
This Python client enables easy interaction with the Werk24 API for processing technical drawings efficiently.
The API gives you access to the following structured data:

- **Meta Data**: Drawing ID, Part ID, Designation, General Tolerances, General Roughness, Material, Weight, Bill of Material, Revision Table, Languages and Notes.
- **Features**: Dimensions incl. Tolerances, Threads, Bores, Chamfers, Roughnesses, GDnTs, Radii.
- **Insights**: Manufacturing Method, Postprocesses, Input Geometry, Output Geometry.
- **Redaction**: Redact information from Technical Drawings.

👉 Visit [werk24.io](https://werk24.io/?utm_source=github&utm_medium=feature_link) to learn more or request a demo.

## Why Werk24?

- **Accelerate Quoting** – Generate prices from 2D drawings in seconds.
- **Reduce Manual Entry** – Automatically capture metadata and dimensions.
- **Speed Up Supplier Scouting** – Match drawings with capable vendors.
- **Protect IP** – Anonymize sensitive details before sharing.
- **Boost Productivity** – Let engineers focus on design, not data extraction.

## Features

- **Automated Extraction**: Retrieve metadata, dimensions, and annotations from technical drawings.
- **Fast Processing**: Optimized API calls for efficient inference.
- **Seamless Integration**: Works with Python-based workflows for manufacturing, CAD, and ERP systems.
- **JSON Output**: Standardized response format for easy processing.

## Applications

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
pip install werk24    # install the library
werk24 init           # obtain a trial license
```

## Quick Start

Here's how you can use the Werk24 client to extract data from a technical drawing:

```python
import asyncio
from werk24 import Werk24Client, AskMetaData, get_test_drawing

async def read_drawing(asks):
  fid = get_test_drawing()
  async with Werk24Client() as client:
      return [msg async for msg in client.read_drawing(fid, asks)]

asyncio.run(read_drawing([AskMetaData()]))
```

## Documentation

See [https://werk24.io/docs/index.html](https://werk24.io/docs/index.html)

## CLI

To get a first impression, you can run the CLI:

```bash
$> werk24 --help
 Usage: python -m werk24.cli.werk24 [OPTIONS] COMMAND [ARGS]...

╭─ Options ─────────────────────────────────────────────────────────────────────────────────╮
│ --log-level                 TEXT  Set the log level [default: WARNING]                    │
│ --install-completion              Install completion for the current shell.               │
│ --show-completion                 Show completion for the current shell, to copy it or... |
│ --help                            Show this message and exit.                             │
╰───────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Commands ────────────────────────────────────────────────────────────────────────────────╮
│ init           Initialize Werk24 by providing or creating a license.                      │
│ health-check   Run a comprehensive health check for the CLI.                              │
│ techread       Read a drawing file and extract information.                               │
│ version        Print the version of the Client.                                           │
│ status         Fetch and display the Werk24 system status.                               │
╰───────────────────────────────────────────────────────────────────────────────────────────╯

```

## Community & Support

- Website: [werk24.io](https://werk24.io/?utm_source=github&utm_medium=community_link)
- Email: [info@werk24.io](mailto:info@werk24.io)
- LinkedIn: [Werk24](https://www.linkedin.com/company/werk24/)

Have questions? [Request a demo](https://werk24.io/?utm_source=github&utm_medium=request_demo) or open an issue and we’ll be happy to help.

## Contributing

We welcome contributions that improve the client or documentation.

1. Fork the repository and create a new branch.
2. Make your changes and ensure tests pass with `pytest`.
3. Open a pull request describing your changes.

See [CONTRIBUTING.md](CONTRIBUTING.md) for more details.

## License

The Werk24 Python Client requires a commercial Werk24 license to use.
See [LICENSE.txt](LICENSE.txt) for terms and conditions.
