import ast
from pathlib import Path


SRC = Path(__file__).resolve().parents[1] / "src"


def iter_py_files(root: Path):
    for path in root.rglob("*.py"):
        yield path


def module_name_from_path(path: Path, root: Path) -> str:
    rel = path.relative_to(root).with_suffix("")
    return ".".join(rel.parts)


def collect_imports(py_files: list[Path]) -> set[str]:
    imports: set[str] = set()
    for path in py_files:
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.add(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.add(node.module)
    return imports


def find_unused_modules() -> list[Path]:
    py_files = list(iter_py_files(SRC))
    module_map = {module_name_from_path(p, SRC): p for p in py_files}
    imports = collect_imports(py_files)

    unused: list[Path] = []
    for mod, path in module_map.items():
        if mod.endswith(".__init__"):
            continue
        if not any(imp == mod or imp.startswith(mod + ".") for imp in imports):
            unused.append(path)
    return sorted(unused)


def main() -> int:
    unused = find_unused_modules()
    out_path = Path(__file__).resolve().parents[1] / "backup" / "imports_static.txt"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(str(p) for p in unused), encoding="utf-8")
    print(f"Wrote {len(unused)} entries to {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
