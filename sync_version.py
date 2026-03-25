from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
INIT_FILE = ROOT / "src" / "__init__.py"
VERSION_INFO_FILE = ROOT / "version_info.txt"
VERSION_PATTERN = re.compile(r"\bv=(\d+\.\d+\.\d+\.\d+)\b")
INIT_PATTERN = re.compile(r"^__version__\s*=\s*['\"]([^'\"]+)['\"]\s*$", re.MULTILINE)


def get_last_commit_message() -> str:
    result = subprocess.run(
        ["git", "log", "-1", "--pretty=%B"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return result.stdout.strip()


def extract_version(message: str) -> str:
    match = VERSION_PATTERN.search(message)
    if not match:
        raise ValueError(
            "Version marker not found in the latest commit message. "
            "Use the format: v=0.0.0.26"
        )
    return match.group(1)


def update_init_file(version: str) -> None:
    original = INIT_FILE.read_text(encoding="utf-8")
    updated, count = INIT_PATTERN.subn(f"__version__ = '{version}'", original, count=1)
    if count != 1:
        raise ValueError(f"Could not update __version__ in {INIT_FILE}")
    INIT_FILE.write_text(updated, encoding="utf-8")


def write_version_info(version: str) -> None:
    major, minor, patch, build = version.split(".")
    content = f"""VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=({major}, {minor}, {patch}, {build}),
    prodvers=({major}, {minor}, {patch}, {build}),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
    ),
  kids=[
    StringFileInfo(
      [
      StringTable(
        '040904B0',
        [
        StringStruct('CompanyName', 'L1L2'),
        StringStruct('FileDescription', 'L1L2'),
        StringStruct('FileVersion', '{version}'),
        StringStruct('InternalName', 'L1L2'),
        StringStruct('OriginalFilename', 'L1L2.exe'),
        StringStruct('ProductName', 'L1L2'),
        StringStruct('ProductVersion', '{version}')
        ])
      ]),
    VarFileInfo([VarStruct('Translation', [1033, 1200])])
  ]
)"""
    VERSION_INFO_FILE.write_text(content, encoding="utf-8")


def main() -> int:
    try:
        message = get_last_commit_message()
        version = extract_version(message)
        update_init_file(version)
        write_version_info(version)
    except Exception as exc:
        print(f"Version sync failed: {exc}", file=sys.stderr)
        return 1

    print(f"Synchronized version: {version}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
