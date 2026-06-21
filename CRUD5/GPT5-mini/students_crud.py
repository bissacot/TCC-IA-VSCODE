#!/usr/bin/env python3
"""Simple Students CRUD

Each student has:
- `id`: COURSECODE + sequential integer (e.g., GES1, GES2)
- `name`
- `course` (uppercase course code)

Data is persisted to `students.json` in the same folder.
"""
from __future__ import annotations

import json
import os
import re
from typing import Dict, List, Optional

DB_FILENAME = "students.json"


class StudentManager:
    def __init__(self, db_path: str = DB_FILENAME):
        self.db_path = db_path
        self.students: List[Dict] = []
        self.counters: Dict[str, int] = {}
        self._load()

    def _load(self) -> None:
        if os.path.exists(self.db_path):
            with open(self.db_path, "r", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                    self.students = data.get("students", [])
                    self.counters = data.get("counters", {})
                except Exception:
                    self.students = []
                    self.counters = {}
        else:
            self._save()

        # Rebuild counters from existing student IDs to ensure correct sequencing
        pattern = re.compile(r"^([A-Z]+)(\d+)$")
        for s in self.students:
            sid = s.get("id", "")
            m = pattern.match(sid.upper())
            if m:
                course = m.group(1)
                num = int(m.group(2))
                if self.counters.get(course, 0) < num:
                    self.counters[course] = num

    def _save(self) -> None:
        payload = {"students": self.students, "counters": self.counters}
        with open(self.db_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)

    def _next_id(self, course_code: str) -> str:
        course = course_code.upper()
        next_num = self.counters.get(course, 0) + 1
        self.counters[course] = next_num
        return f"{course}{next_num}"

    def create_student(self, name: str, course_code: str) -> Dict:
        course = course_code.upper()
        sid = self._next_id(course)
        student = {"id": sid, "name": name, "course": course}
        self.students.append(student)
        self._save()
        return student

    def read_student(self, student_id: str) -> Optional[Dict]:
        for s in self.students:
            if s["id"] == student_id:
                return s
        return None

    def list_students(self, course_code: Optional[str] = None) -> List[Dict]:
        if course_code:
            c = course_code.upper()
            return [s for s in self.students if s.get("course") == c]
        return list(self.students)

    def update_student(self, student_id: str, name: Optional[str] = None, course_code: Optional[str] = None) -> Optional[Dict]:
        for idx, s in enumerate(self.students):
            if s["id"] == student_id:
                if name:
                    s["name"] = name
                if course_code:
                    new_course = course_code.upper()
                    if new_course != s.get("course"):
                        # generate a new ID for the new course
                        new_id = self._next_id(new_course)
                        s["course"] = new_course
                        s["id"] = new_id
                self.students[idx] = s
                self._save()
                return s
        return None

    def delete_student(self, student_id: str) -> bool:
        for idx, s in enumerate(self.students):
            if s["id"] == student_id:
                self.students.pop(idx)
                self._save()
                return True
        return False


def _print_students(students: List[Dict]) -> None:
    if not students:
        print("No students found.")
        return
    for s in students:
        print(f"{s['id']}: {s['name']} ({s['course']})")


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Students CRUD")
    sub = parser.add_subparsers(dest="cmd")

    p_create = sub.add_parser("create", help="Create a student")
    p_create.add_argument("--name", required=True)
    p_create.add_argument("--course", required=True)

    p_list = sub.add_parser("list", help="List students")
    p_list.add_argument("--course", required=False)

    p_get = sub.add_parser("get", help="Get student by ID")
    p_get.add_argument("student_id")

    p_update = sub.add_parser("update", help="Update student")
    p_update.add_argument("student_id")
    p_update.add_argument("--name", required=False)
    p_update.add_argument("--course", required=False)

    p_delete = sub.add_parser("delete", help="Delete student by ID")
    p_delete.add_argument("student_id")

    args = parser.parse_args()
    mgr = StudentManager()

    if not args.cmd:
        # Interactive menu
        while True:
            print()
            print("Students CRUD")
            print("1) Create")
            print("2) List")
            print("3) Get")
            print("4) Update")
            print("5) Delete")
            print("0) Exit")
            choice = input("> ").strip()
            if choice == "1":
                name = input("Name: ").strip()
                course = input("Course code: ").strip()
                s = mgr.create_student(name, course)
                print("Created:", s)
            elif choice == "2":
                course = input("Filter by course (leave empty for all): ").strip()
                students = mgr.list_students(course or None)
                _print_students(students)
            elif choice == "3":
                sid = input("Student ID: ").strip()
                s = mgr.read_student(sid)
                print(s or "Not found")
            elif choice == "4":
                sid = input("Student ID to update: ").strip()
                name = input("New name (leave empty to keep): ").strip() or None
                course = input("New course (leave empty to keep): ").strip() or None
                updated = mgr.update_student(sid, name=name, course_code=course)
                print(updated or "Not found")
            elif choice == "5":
                sid = input("Student ID to delete: ").strip()
                ok = mgr.delete_student(sid)
                print("Deleted" if ok else "Not found")
            elif choice == "0":
                break
            else:
                print("Unknown choice")
        return

    if args.cmd == "create":
        s = mgr.create_student(args.name, args.course)
        print("Created:", s)
    elif args.cmd == "list":
        students = mgr.list_students(args.course)
        _print_students(students)
    elif args.cmd == "get":
        s = mgr.read_student(args.student_id)
        print(s or "Not found")
    elif args.cmd == "update":
        updated = mgr.update_student(args.student_id, name=args.name, course_code=args.course)
        print(updated or "Not found")
    elif args.cmd == "delete":
        ok = mgr.delete_student(args.student_id)
        print("Deleted" if ok else "Not found")


if __name__ == "__main__":
    main()
