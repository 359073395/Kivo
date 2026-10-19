"""Check that every file from the pinned upstream archive is still present."""
import argparse
import ast
import hashlib
import json
from pathlib import Path
import zipfile

parser = argparse.ArgumentParser()
parser.add_argument("archive", type=Path)
parser.add_argument("--output", type=Path)
args = parser.parse_args()
root = Path(__file__).resolve().parents[1]
modified, missing, unchanged = [], [], 0
def surface(source):
    module = ast.parse(source)
    functions, routes = set(), set()
    for node in module.body:
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)): continue
        functions.add(node.name)
        for decorator in node.decorator_list:
            if (isinstance(decorator, ast.Call) and isinstance(decorator.func, ast.Attribute)
                    and decorator.func.attr in {"get", "post", "put", "patch", "delete"}
                    and decorator.args and isinstance(decorator.args[0], ast.Constant)):
                routes.add((decorator.func.attr, decorator.args[0].value))
    return functions, routes

with zipfile.ZipFile(args.archive) as archive:
    commit = archive.comment.decode()
    for entry in archive.infolist():
        if entry.is_dir(): continue
        relative = Path(*Path(entry.filename).parts[1:])
        target = root / relative
        if not target.is_file():
            missing.append(relative.as_posix())
        elif hashlib.sha256(target.read_bytes()).digest() != hashlib.sha256(archive.read(entry)).digest():
            modified.append(relative.as_posix())
        else:
            unchanged += 1
    upstream_app = next(e for e in archive.infolist() if e.filename.endswith("/web/app.py"))
    original_functions, original_routes = surface(archive.read(upstream_app).decode("utf-8-sig"))
    current_functions, current_routes = surface((root / "web/app.py").read_text(encoding="utf-8-sig"))
result = {"upstreamCommit": commit, "missing": missing, "modified": modified, "unchanged": unchanged,
          "builtinSkills": len(list((root / "skills/builtin").glob("*/SKILL.md"))),
          "missingBackendFunctions": sorted(original_functions - current_functions),
          "missingHttpRoutes": sorted(original_routes - current_routes),
          "modifiedBuiltinSkills": [p for p in modified if p.startswith("skills/builtin/")],
          "allUpstreamFilesPreserved": not missing}
if args.output:
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(result, ensure_ascii=False, indent=2))
raise SystemExit(bool(missing or result["missingBackendFunctions"] or result["missingHttpRoutes"]))
