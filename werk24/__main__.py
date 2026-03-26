"""Allow running the werk24 CLI via `python -m werk24`.

This ensures the CLI works on all platforms regardless of
whether the Scripts/bin directory is on the system PATH.
"""

from werk24.cli.werk24 import app

app()
