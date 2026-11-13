"""Give bundled Python child processes access to the selected local worktree."""
import os
from pathlib import Path
import sys
import site

_packages = os.environ.get("KIVO_PYTHON_PACKAGES")
if _packages and Path(_packages).is_dir():
    site.addsitedir(_packages)
    sys.path.remove(_packages)
    sys.path.insert(0, _packages)

_runtime = Path(sys.executable).parent
_tool_paths = [_runtime, _runtime / "Tools" / "python-scripts", _runtime / "Scripts",
               _runtime / "Tools" / "ffmpeg", _runtime / "Tools" / "node"]
if _packages:
    _tool_paths.extend([Path(_packages) / "Scripts", Path(_packages) / "bin"])
_path_key = next((key for key in os.environ if key.upper() == "PATH"), "PATH")
_existing = os.environ.get(_path_key, "").split(os.pathsep)
_additions = [str(path) for path in _tool_paths if path.is_dir() and str(path) not in _existing]
if _additions:
    os.environ[_path_key] = os.pathsep.join([*_additions, *_existing])

_playwright = _runtime / "Lib" / "site-packages" / "playwright" / "driver" / "package"
if (_playwright / "package.json").is_file():
    os.environ.setdefault("PLAYWRIGHT_MODULE", str(_playwright))

_root = os.environ.get("KIVO_PLATFORM_ROOT")
if _root:
    for _relative in ("", "scripts", "skills/shared/scripts"):
        _path = str(Path(_root) / _relative)
        if Path(_path).is_dir() and _path not in sys.path:
            sys.path.insert(0, _path)
