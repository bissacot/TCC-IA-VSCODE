"""Simple student database with persistent JSON storage.

Each student: {"id": "COURSE1", "name": "...", "course": "COURSE"}
IDs are generated as COURSE + sequential integer per course (counters persisted).
"""
import json
from pathlib import Path
from typing import List, Dict, Optional


class StudentDatabase:
    def __init__(self, path: str = "students.json"):
        self.path = Path(path)
        if not self.path.exists():
            self._data = {"students": [], "counters": {}}
            self._save()
        else:
            self._load()

    def _load(self) -> None:
        with self.path.open("r", encoding="utf-8") as f:
            self._data = json.load(f)

    def _save(self) -> None:
        with self.path.open("w", encoding="utf-8") as f:
            json.dump(self._data, f, indent=2, ensure_ascii=False)

    def list_students(self) -> List[Dict]:
        return list(self._data["students"])

    def _next_id_for_course(self, course: str) -> str:
        course = course.upper()
        curr = self._data["counters"].get(course, 0) + 1
        self._data["counters"][course] = curr
        return f"{course}{curr}"

    def add_student(self, name: str, course: str) -> Dict:
        course = course.strip().upper()
        name = name.strip()
        if not course.isalpha():
            raise ValueError("Course code must contain only letters.")
        sid = self._next_id_for_course(course)
        student = {"id": sid, "name": name, "course": course}
        self._data["students"].append(student)
        self._save()
        return student

    def get(self, student_id: str) -> Optional[Dict]:
        for s in self._data["students"]:
            if s["id"].upper() == student_id.upper():
                return s
        return None

    def update(self, student_id: str, name: Optional[str] = None, course: Optional[str] = None) -> Optional[Dict]:
        student = self.get(student_id)
        if student is None:
            return None
        changed = False
        if name is not None and name.strip() != "":
            student["name"] = name.strip()
            changed = True
        if course is not None and course.strip() != "":
            course = course.strip().upper()
            if not course.isalpha():
                raise ValueError("Course code must contain only letters.")
            if course != student["course"]:
                # assign new ID under the new course
                new_id = self._next_id_for_course(course)
                student["course"] = course
                student["id"] = new_id
                changed = True
        if changed:
            self._save()
        return student

    def delete(self, student_id: str) -> bool:
        for i, s in enumerate(self._data["students"]):
            if s["id"].upper() == student_id.upper():
                del self._data["students"][i]
                self._save()
                return True
        return False

    def find_by_name(self, name: str) -> List[Dict]:
        n = name.strip().lower()
        return [s for s in self._data["students"] if n in s["name"].lower()]
