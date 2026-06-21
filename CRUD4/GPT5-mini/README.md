# Student Registry (CRUD)

Simple Python program implementing Create, Read, Update, Delete for students.

Each student has:
- name
- course code (e.g., GES, GEC)
- student ID generated as `<COURSE><N>` (e.g., GES1)

Usage:

Run CLI:

```bash
python cli.py add "Alice" GES
python cli.py list
python cli.py get GES1
python cli.py update GES1 -n "Alicia" -c GEC
python cli.py delete GES1
```

Run demo:

```bash
python demo.py
```
