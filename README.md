# Educational Program Manager

Offline desktop application for managing educational programs, topics, lessons, questions, teachers, and methodical materials. Built with Python 3.11+, PySide6, and SQLite.

## Features
- Program browsing: Program -> Discipline -> Topic -> Lesson -> Question
- Full-text search across all entities
- Methodical material tracking with file attachments
- Report tab that shows lesson coverage by teacher/material type with color status
- Admin mode for CRUD and relationship management
- Local SQLite database with FTS5 support
- Designed for offline use and portable packaging

## Run in Development
1) Create and activate a virtual environment (recommended).
2) Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3) Run the app:
   ```bash
   python -m src.app
   ```

On first run, the app creates:
- `database/education.db`
- `settings/admin_credentials.json`
- `files/` (attachment storage root)

Demo data is inserted automatically when the database is empty.

## Admin Mode
On first access, the app asks you to create a local admin password.

If you need to reset it, delete `settings/admin_credentials.json` and create a new one on next access.

Curriculum import supports a preview step before writing changes to the database.
Batch curriculum import also shows a confirmation summary based on filenames before data is written.

## Build Portable EXE (PyInstaller)
Use the provided build script (Windows):
```bat
build.bat
```

Build scripts automatically sync the app version from the latest Git commit message.
Use this format in the last commit message before building:
```text
v=0.0.0.26
```

Manual build from the repository root:
```bash
pyinstaller --onefile --noconsole --name "L1L2" --paths src run_app.py
```

The EXE will be in `dist/`. The app will create a `data/` folder next to the EXE on first run.

## Database Migration (Discipline Level)
On startup, the app checks the schema version and migrates existing data.
- Existing Program -> Topic links are migrated into Program -> Discipline -> Topic.
- A discipline is created per program using the program name (e.g., "Discipline for <Program Name>").
- Before schema migrations run on an existing database, the app creates a backup in `settings/schema_backups/`.

## Translations (UA/EN)
Translation sources are in `translations/` as `.ts` files. The app loads `.qm` if present and falls back to `.ts`.
Compile them to `.qm` if desired:
```bash
pyside6-lrelease translations/app_uk.ts -qm translations/app_uk.qm
pyside6-lrelease translations/app_en.ts -qm translations/app_en.qm
```

When building with PyInstaller, include translation files:
```bash
pyinstaller --onefile --windowed --name "EducationalProgramManager" ^
  --add-data "translations;translations" src/app.py
```

## Data Storage
All data is stored locally in a single SQLite file at `database/education.db`. Attached files are stored under `files/` (default root) and referenced by the database.
- Cleanup operations create a backup bundle in `settings/cleanup_backups/` before deleting orphaned data.
- Attaching an existing file is blocked when that physical file already belongs to another material record.
