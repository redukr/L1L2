# Educational Program Manager

Offline desktop application for managing educational programs, topics, lessons, questions, teachers, and methodical materials. Built with Python 3.11+, PySide6, and SQLite.

## Features
- Program browsing: Program -> Topic -> Lesson -> Question
- Full-text search across all entities
- Methodical material tracking with file attachments
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
- `data/education.db`
- `data/admin_credentials.json`

Demo data is inserted automatically when the database is empty.

## Admin Mode
Default admin password: `admin123`

To reset the password, delete `data/admin_credentials.json` and restart the app.

## Build Portable EXE (PyInstaller)
From the repository root:
```bash
pyinstaller --onefile --windowed --name "EducationalProgramManager" src/app.py
```

The EXE will be in `dist/`. The app will create a `data/` folder next to the EXE on first run.

## Data Storage
All data is stored locally in a single SQLite file at `data/education.db`. Attached files are copied to `data/materials/` and referenced by the database.
