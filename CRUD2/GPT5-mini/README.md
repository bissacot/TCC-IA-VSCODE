# Student CRUD

Simple Python CLI CRUD app to register, list, update, and delete students.

Each student has:
- name
- course code (e.g., GES, GEC)
- student ID: `<COURSE><n>` where `n` is sequential per course (e.g., `GES1`).

Usage

Run:

```bash
python main.py
```

Commands:
- `create` - add a student
- `list` - list students
- `update` - update student name or course (ID adjusts if course changes)
- `delete` - remove a student
- `exit` - quit
