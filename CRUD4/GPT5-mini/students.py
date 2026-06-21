"""Student registry with simple CRUD operations and JSON persistence.

Each student has:
- `student_id`: generated as <COURSE><N> (e.g. GES1)
- `name`
- `course_code`

The registry stores data in a JSON file (default `students.json`).
"""
from dataclasses import dataclass, asdict
import json
import os
from typing import Dict, List, Optional


@dataclass
class Student:
    student_id: str
    name: str
    course_code: str


class StudentRegistry:
    def __init__(self, storage_path: str = "students.json") -> None:
        self.storage_path = storage_path
        self.students: Dict[str, Student] = {}
        self.counters: Dict[str, int] = {}
        self._load()

    def _load(self) -> None:
        if not os.path.exists(self.storage_path):
            self._save()
            return
        try:
            with open(self.storage_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            data = {}
        students = data.get("students", [])
        counters = {k.upper(): int(v) for k, v in data.get("counters", {}).items()}
        self.students = {}
        for s in students:
            sid = s.get("student_id", "").strip().upper()
            name = s.get("name", "").strip()
            course = s.get("course_code", "").strip().upper()
            if sid:
                self.students[sid] = Student(student_id=sid, name=name, course_code=course)
        # Merge counters from file and computed from students to be safe
        merged: Dict[str, int] = {k: v for k, v in counters.items()}
        for sid, st in self.students.items():
            course = st.course_code
            try:
                n = int(sid[len(course):])
            except Exception:
                n = 0
            merged[course] = max(merged.get(course, 0), n)
        self.counters = merged

    def _save(self) -> None:
        data = {
            "students": [asdict(s) for s in self.students.values()],
            "counters": self.counters,
        }
        with open(self.storage_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def _normalize_course(self, course_code: str) -> str:
        return (course_code or "").strip().upper()

    def _next_id(self, course_code: str) -> str:
        code = self._normalize_course(course_code)
        self.counters.setdefault(code, 0)
        self.counters[code] += 1
        return f"{code}{self.counters[code]}"

    def create_student(self, name: str, course_code: str) -> Student:
        if not name:
            raise ValueError("name is required")
        course = self._normalize_course(course_code)
        sid = self._next_id(course)
        student = Student(student_id=sid, name=name.strip(), course_code=course)
        self.students[sid] = student
        self._save()
        return student

    def list_students(self, course: Optional[str] = None) -> List[Student]:
        if course:
            course = self._normalize_course(course)
            return sorted([s for s in self.students.values() if s.course_code == course], key=lambda x: x.student_id)
        return sorted(self.students.values(), key=lambda x: x.student_id)

    def get_student(self, student_id: str) -> Optional[Student]:
        if not student_id:
            return None
        return self.students.get(student_id.strip().upper())

    def update_student(self, student_id: str, name: Optional[str] = None, course_code: Optional[str] = None) -> Optional[Student]:
        if not student_id:
            return None
        sid = student_id.strip().upper()
        student = self.students.get(sid)
        if not student:
            return None
        changed = False
        if name:
            student.name = name.strip()
            changed = True
        if course_code:
            new_course = self._normalize_course(course_code)
            if new_course != student.course_code:
                new_id = self._next_id(new_course)
                del self.students[sid]
                student.course_code = new_course
                student.student_id = new_id
                self.students[new_id] = student
                self._save()
                return student
        if changed:
            self.students[student.student_id] = student
            self._save()
        return student

    def delete_student(self, student_id: str) -> bool:
        if not student_id:
            return False
        sid = student_id.strip().upper()
        if sid in self.students:
            del self.students[sid]
            self._save()
            return True
        return False
"""students.py

Simple Student registry with CRUD operations and JSON persistence.

Student IDs are generated as <COURSE><N> (e.g., GES1, GES2).
"""
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional
import json
import os
import re


@dataclass
class Student:
    student_id: str
    name: str
    course: str

    def to_dict(self) -> Dict[str, str]:
        return asdict(self)


class StudentRegistry:
    def __init__(self, storage_path: str = "students.json") -> None:
        self.storage_path = storage_path
        self.students: Dict[str, Student] = {}
        self.counters: Dict[str, int] = {}
        self.load()

    def load(self) -> None:
        if not os.path.exists(self.storage_path):
            self.save()
            return
        with open(self.storage_path, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except Exception:
                data = {}
        students = data.get("students", [])
        counters = data.get("counters", {})
        for s in students:
            sid = s.get("student_id", "").upper()
            self.students[sid] = Student(student_id=sid, name=s.get("name", ""), course=s.get("course", "").upper())
        self.counters = {k.upper(): int(v) for k, v in counters.items()}
        for sid in self.students:
            m = re.match(r"^([A-Z]+)(\d+)$", sid)
            if m:
                code, num = m.group(1), int(m.group(2))
                self.counters[code] = max(self.counters.get(code, 0), num)

    def save(self) -> None:
        data = {
            "students": [s.to_dict() for s in self.students.values()],
            "counters": self.counters,
        }
        dirpath = os.path.dirname(self.storage_path)
        if dirpath and not os.path.exists(dirpath):
            os.makedirs(dirpath, exist_ok=True)
        with open(self.storage_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def generate_id(self, course: str) -> str:
        code = (course or "").strip().upper()
        if not code:
            raise ValueError("course code required")
        self.counters.setdefault(code, 0)
        self.counters[code] += 1
        return f"{code}{self.counters[code]}"

    def create_student(self, name: str, course: str) -> Student:
        name = (name or "").strip()
        code = (course or "").strip().upper()
        if not name:
            raise ValueError("name required")
        if not code:
            raise ValueError("course code required")
        sid = self.generate_id(code)
        student = Student(student_id=sid, name=name, course=code)
        self.students[sid.upper()] = student
        self.save()
        return student

    def list_students(self, course: Optional[str] = None) -> List[Student]:
        if course:
            code = course.strip().upper()
            return sorted([s for s in self.students.values() if s.course == code], key=lambda s: s.student_id)
        return sorted(self.students.values(), key=lambda s: s.student_id)

    def get_student(self, student_id: str) -> Optional[Student]:
        if not student_id:
            return None
        return self.students.get(student_id.strip().upper())

    def update_student(self, student_id: str, name: Optional[str] = None, course: Optional[str] = None) -> Optional[Student]:
        if not student_id:
            return None
        sid = student_id.strip().upper()
        student = self.students.get(sid)
        if not student:
            return None
        changed = False
        if name:
            student.name = name.strip()
            changed = True
        if course:
            new_course = course.strip().upper()
            if new_course and new_course != student.course:
                new_id = self.generate_id(new_course)
                del self.students[sid]
                student.course = new_course
                student.student_id = new_id
                self.students[new_id.upper()] = student
                self.save()
                return student
        if changed:
            self.students[student.student_id.upper()] = student
            self.save()
        return student

    def delete_student(self, student_id: str) -> bool:
        if not student_id:
            return False
        sid = student_id.strip().upper()
        if sid in self.students:
            del self.students[sid]
            self.save()
            return True
        return False
