"""Dispatch bundled Python commands after the installation directory changes."""
from importlib.metadata import entry_points
import sys


command = sys.argv.pop(1)
sys.argv[0] = command
if command in {"easel", "lingxi"}:
    from easel.cli import main
    raise SystemExit(main())
entries = entry_points(group="console_scripts", name=command)
if not entries:
    raise SystemExit(f"Python command is unavailable: {command}")
raise SystemExit(next(iter(entries)).load()())
