# Student CRUD (Python)

Simple CLI app and module to register, list, update and delete students.

- Run interactive CLI: `python app.py`
- Run quick verification script: `python test_run.py`

IDs are generated as the uppercase course code plus a sequential integer per course (e.g. `GES1`, `GES2`). Counters are persisted in `students.json` so IDs are not reused.
