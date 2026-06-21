# Student CRUD (Python)

Simple Python implementation of a student CRUD (Create, Read, Update, Delete).

Features
- Per-course sequential student IDs (e.g. `GES1`, `GES2`, `GEC1`).
- In-memory or JSON-file persistence (`students.json` by default).
- Interactive CLI and a non-interactive demo script.

Files
- `students.py`: core `StudentDB` class and `Student` dataclass.
- `cli.py`: interactive menu-driven CLI.
- `run_demo.py`: programmatic demo that prints create/update/delete results.

Quick start
Run the demo (non-interactive):

```bash
python run_demo.py
```

Run the interactive CLI (persists to `students.json` in the current folder):

```bash
python cli.py
```

Notes
- Updating a student's course will assign a new student ID using the target course's next sequence number.
- The DB computes per-course counters from existing IDs when loading a JSON file, so new IDs always continue the sequence.
