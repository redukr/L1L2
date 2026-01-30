"""Bootstrap entry point for PyInstaller builds."""
from __future__ import annotations

import os
import sys


def main() -> int:
    root = os.path.dirname(os.path.abspath(__file__))
    if root not in sys.path:
        sys.path.insert(0, root)
    from src.app import main as app_main  # local import after sys.path fix

    return app_main()


if __name__ == "__main__":
    raise SystemExit(main())
