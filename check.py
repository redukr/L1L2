python - <<'PY'
import sqlite3
from pathlib import Path

candidates = [
    Path("database/education.db"),
    Path("data/education.db"),
]
for p in candidates:
    print("DB:", p.resolve())
    if not p.exists():
        print("missing")
        continue
    try:
        con = sqlite3.connect(p)
        rows = con.execute("PRAGMA integrity_check;").fetchall()
        print(" / ".join(r[0] for r in rows))
    except Exception as e:
        print("ERROR:", e)
    finally:
        try: con.close()
        except: pass
    print("---")
PY
