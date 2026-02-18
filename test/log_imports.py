import builtins
import importlib
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    sys.path.insert(0, str(ROOT))
    seen: set[str] = set()
    real_import = builtins.__import__

    def tracking_import(name, globals=None, locals=None, fromlist=(), level=0):
        module = real_import(name, globals, locals, fromlist, level)
        try:
            if name.startswith("src."):
                seen.add(name)
        except Exception:
            pass
        return module

    builtins.__import__ = tracking_import
    try:
        importlib.import_module("src.app")
    finally:
        builtins.__import__ = real_import

    for name in sys.modules:
        if name == "src" or name.startswith("src."):
            seen.add(name)

    out_path = ROOT / "backup" / "imports_runtime.txt"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(sorted(seen)), encoding="utf-8")
    print(f"Wrote {len(seen)} entries to {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
