#!/usr/bin/env python3
"""
Simple students CRUD with JSON persistence.

Fields: name, course (code like GES), id = COURSE + sequential integer.
"""
import json
import os
from typing import Dict, List, Optional

DATA_FILE = "students.json"

def load_data() -> Dict:
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"students": [], "counters": {}}

def save_data(data: Dict) -> None:
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def _generate_student_id(course_code: str, data: Dict) -> str:
    code = course_code.upper()
    counters = data.setdefault("counters", {})
    n = counters.get(code, 0) + 1
    counters[code] = n
    return f"{code}{n}"

def register_student(name: str, course_code: str) -> Dict:
    data = load_data()
    sid = _generate_student_id(course_code, data)
    student = {"id": sid, "name": name.strip(), "course": course_code.upper()}
    data.setdefault("students", []).append(student)
    save_data(data)
    return student

def list_students() -> List[Dict]:
    data = load_data()
    return data.get("students", [])

def find_student(student_id: str) -> Optional[Dict]:
    sid = student_id.strip().upper()
    for s in list_students():
        if s["id"].upper() == sid:
            return s
    return None

def update_student(student_id: str, new_name: Optional[str] = None) -> Optional[Dict]:
    data = load_data()
    sid = student_id.strip().upper()
    for s in data.get("students", []):
        if s["id"].upper() == sid:
            if new_name is not None:
                s["name"] = new_name.strip()
                save_data(data)
            return s
    return None

def delete_student(student_id: str) -> Optional[Dict]:
    data = load_data()
    sid = student_id.strip().upper()
    students = data.get("students", [])
    for i, s in enumerate(students):
        if s["id"].upper() == sid:
            removed = students.pop(i)
            save_data(data)
            return removed
    return None

def print_students(students: List[Dict]) -> None:
    if not students:
        print("No students found.")
        return
    print(f"{'ID':<8} {'Name':<30} {'Course'}")
    print("-" * 50)
    for s in students:
        print(f"{s['id']:<8} {s['name']:<30} {s['course']}")

def interactive_menu() -> None:
    while True:
        print("\nStudent CRUD")
        print("1. Register student")
        print("2. List students")
        print("3. Update student name")
        print("4. Delete student")
        print("5. Exit")
        choice = input("Choice: ").strip()
        if choice == "1":
            name = input("Name: ").strip()
            course = input("Course code (e.g., GES): ").strip().upper()
            if not name or not course:
                print("Name and course required.")
                continue
            s = register_student(name, course)
            print(f"Registered: {s['id']} - {s['name']} ({s['course']})")
        elif choice == "2":
            print_students(list_students())
        elif choice == "3":
            sid = input("Student ID to update: ").strip()
            new_name = input("New name: ").strip()
            if not new_name:
                print("New name required.")
                continue
            updated = update_student(sid, new_name=new_name)
            if updated:
                print("Updated:", updated)
            else:
                print("Student not found.")
        elif choice == "4":
            sid = input("Student ID to delete: ").strip()
            removed = delete_student(sid)
            if removed:
                print("Deleted:", removed)
            else:
                print("Student not found.")
        elif choice == "5":
            print("Goodbye.")
            break
        else:
            print("Invalid choice.")

if __name__ == "__main__":
    interactive_menu()
