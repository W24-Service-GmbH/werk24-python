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
- [Dependency Management](#dependency-management)
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
werk24 init           # paste your API key; it is saved to ~/.werk24 and found from any folder
```

Calling the API needs an API key and is billed pay as you go. [Sign up for the Werk24 API](https://studio.werk24.io/console/signup?product=console&plan=payg&utm_source=github&utm_medium=install_signup), then create a key on the [API keys page](https://studio.werk24.io/console/keys) of the Werk24 console. `werk24 init` asks for the key and stores it for the client. On a server or in CI, set the `W24TECHREAD_AUTH_TOKEN` environment variable instead.

To see what Werk24 reads from a drawing before you sign up, try the free [browser demo](https://studio.werk24.io/demo?utm_source=github&utm_medium=install_demo).

### Where the client looks for your API key

The client uses the first key it finds, in this order:

1. The `token` argument: `Werk24Client(token="...")`.
2. `.werk24` in the folder the script is started from.
3. `~/.werk24` in your home folder. This is where `werk24 init` saves the key.
4. `werk24_license.txt` in the folder the script is started from.
5. `~/werk24_license.txt` in your home folder.
6. The environment variable `W24TECHREAD_AUTH_TOKEN`.

The environment variable suits CI jobs and containers, where no key file
exists. On a machine that has a key file, the file is used instead. When no
key is found, the error lists every place the client looked. `werk24
health-check` shows which key is in use and where it was read from.

## Dependency Management

### Overview

The werk24 library uses a flexible dependency management strategy designed to minimize conflicts with other packages in your environment. We specify **minimum versions** for dependencies based on required features and security fixes, but avoid restrictive upper bounds that can cause installation conflicts.

### Why Minimum Versions?

Each minimum version requirement exists for a specific reason:

- **Security Fixes**: Dependencies like `cryptography>=44.0.0` require minimum versions that include critical security patches
- **Required Features**: Some dependencies introduced features we rely on in specific versions
- **API Stability**: Minimum versions ensure the APIs we use are available and stable

### Philosophy

We follow these principles:

1. **Trust Semantic Versioning**: For dependencies that follow [SemVer](https://semver.org/), we trust that minor and patch updates won't break compatibility
2. **No Restrictive Upper Bounds**: We avoid upper bounds (like `<=X.Y.Z`) on stable dependencies to prevent blocking your other packages
3. **Surgical Exclusions**: If a specific version has issues, we exclude only that version using `!=X.Y.Z` rather than blocking all future versions
4. **Tested Configurations**: We maintain `requirements.txt` with exact versions we've tested, but your environment can use compatible newer versions

### Troubleshooting Dependency Conflicts

If you encounter dependency conflicts during installation:

1. **Check Your Environment**: Use `pip list` to see what's already installed
2. **Update pip**: Ensure you're using a recent version: `pip install --upgrade pip`
3. **Use Virtual Environments**: Always install in a clean virtual environment to avoid conflicts
4. **Review Conflict Messages**: pip will show which packages have incompatible requirements
5. **Report Issues**: If werk24's requirements conflict with popular packages, please [open an issue](https://github.com/W24-Service-GmbH/werk24-python/issues)

### Common Scenarios

**Installing alongside other packages:**

```bash
# werk24 works well with other packages
pip install werk24 requests pandas numpy
```

**Upgrading from older versions:**

```bash
# Simply upgrade to the latest version
pip install --upgrade werk24
```

**Checking installed versions:**

```bash
# See what versions are actually installed
pip show werk24
pip list | grep -E "(cryptography|pydantic|websockets)"
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

See [v2.docs.werk24.io](https://v2.docs.werk24.io).

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
│ init           Set up Werk24 with your API key.                                           │
│ health-check   Run a comprehensive health check for the CLI.                              │
│ techread       Read a drawing file and extract information.                               │
│ version        Print the version of the Client.                                           │
│ status         Fetch and display the Werk24 system status.                               │
╰───────────────────────────────────────────────────────────────────────────────────────────╯

```

### Reading a drawing from the command line

`werk24 techread` reads a drawing and prints one JSON object per line on stdout for every message that answers an ask. Each object has the fields of `TechreadMessage` (`request_id`, `message_type`, `message_subtype`, `page_number`, `payload_dict`, `payload_url`, `exceptions`). Binary results such as sheet images or the redacted file are not inlined; download them from `payload_url`.

```bash
werk24 techread drawing.pdf --ask-meta-data | jq .
werk24 techread drawing.pdf --ask-meta-data --ask-redaction --pretty
```

Asks: `--ask-balloons`, `--ask-custom <custom_id>`, `--ask-document-profile`, `--ask-features`, `--ask-insights`, `--ask-meta-data`, `--ask-page-assessment`, `--ask-redaction`, `--ask-reference-positions`, `--ask-sheet-images`, `--ask-view-images`. `--pretty` indents each object. `--ask-sheet-images` and `--ask-view-images` also open each image in the default image viewer, which needs Pillow (`pip install pillow`).

Exceptions reported by the server are written to stderr, one line each. The exit status is `0` when every ask was answered without an `ERROR`-level exception. It is `1` when an ask failed, when the read ended before the server reported it complete, or when the client raised an error. It is `2` for a usage error such as an unknown option.

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
