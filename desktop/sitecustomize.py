"""Give bundled Python child processes access to the selected local worktree."""
import os
from pathlib import Path
import sys

_root = os.environ.get("KIVO_PLATFORM_ROOT")
if _root:
    for _relative in ("", "scripts", "skills/shared/scripts"):
        _path = str(Path(_root) / _relative)
        if Path(_path).is_dir() and _path not in sys.path:
            sys.path.insert(0, _path)
