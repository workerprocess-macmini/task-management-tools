# /tools - Shared Code Repository

Central repository สำหรับเก็บทุก scripts, utilities, และ tools ที่ทีมเขียน

---

## 📁 Structure

```
tools/
├── scripts/        ← Main scripts (work-logging, automation, etc.)
├── utils/          ← Utility modules (helpers, validators, etc.)
├── tests/          ← Test files
└── README.md       ← This file
```

---

## 📝 Key Files (Phase 1 MVP)

### Scripts (Moved to tools/)
- `log_work.py` — Work logging with category + priority
- `retrieve_tasks.py` — Query and filter work tasks
- `validators.py` — Bilingual validation
- `daily_summary.py` — Daily summary generation
- `summarize_employee_day.py` — Employee day summary

### Tests
- `test_schema.py` — Unit tests
- `test_integration.py` — Integration tests
- `run_tests.py` — Test runner

---

## 🚀 Usage

All agents use `../tools/` (relative path from workspace):

```python
# From any agent workspace
import sys
sys.path.insert(0, '../tools/')

from scripts.log_work import log_work
from utils.validators import validate_input
```

---

## 📌 Rules

- ✅ All shared code lives here
- ✅ Use relative paths (`../tools/`)
- ✅ Portable to any machine
- ✅ Test before committing
- ✅ Document changes

---

## 🔄 Who Adds Code?

1. **Developer** — Writes new code → saves to `../tools/`
2. **Worker Script** — Runs code from `../tools/`
3. **Main** — Routes requests → no direct code changes
4. **QA** — Tests code in `../tools/`
5. **Analytics** — Analyzes data from `../tools/`

---

*Last Updated: 2026-03-28*
