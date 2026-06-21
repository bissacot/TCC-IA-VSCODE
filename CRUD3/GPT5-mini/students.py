from dataclasses import dataclass, asdict
import json
from typing import Dict, List, Optional
import re
import os


@dataclass
class Student:
    id: str
    name: str
    course: str


class StudentDB:
    """Simple student CRUD with per-course sequential IDs.

    If `storage_path` is None or ':memory:' the DB stays in-memory.
    Otherwise it persists to a JSON file.
    """

    def __init__(self, storage_path: Optional[str] = 'students.json'):
        self.storage_path = storage_path
        self.students: Dict[str, Student] = {}
        self.counters: Dict[str, int] = {}
        if storage_path and storage_path != ':memory:':
            self._load()

    def _load(self) -> None:
        if not os.path.exists(self.storage_path):
            self._save()
            return
        with open(self.storage_path, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = {}
        students = data.get('students', [])
        self.students = {}
        self.counters = {}
        for s in students:
            st = Student(id=s['id'], name=s['name'], course=s['course'])
            self.students[st.id] = st
            m = re.match(r'^([A-Za-z]+)(\d+)$', st.id)
            if m:
                course_code = m.group(1)
                seq = int(m.group(2))
                self.counters[course_code] = max(self.counters.get(course_code, 0), seq)

    def _save(self) -> None:
        if not self.storage_path or self.storage_path == ':memory:':
            return
        data = {'students': [asdict(s) for s in self.students.values()]}
        with open(self.storage_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

    def _normalize_course(self, course: str) -> str:
        return course.strip().upper()

    def _next_id(self, course: str) -> str:
        course = self._normalize_course(course)
        seq = self.counters.get(course, 0) + 1
        self.counters[course] = seq
        return f"{course}{seq}"

    def create_student(self, name: str, course: str) -> Student:
        course = self._normalize_course(course)
        sid = self._next_id(course)
        student = Student(id=sid, name=name.strip(), course=course)
        self.students[student.id] = student
        self._save()
        return student

    def list_students(self) -> List[Student]:
        return list(self.students.values())

    def get_student(self, student_id: str) -> Optional[Student]:
        return self.students.get(student_id)

    def update_student(self, student_id: str, name: Optional[str] = None, course: Optional[str] = None) -> Optional[Student]:
        student = self.students.get(student_id)
        if not student:
            return None
        old_id = student.id
        if name:
            student.name = name.strip()
        changed_course = False
        if course:
            new_course = self._normalize_course(course)
            if new_course != student.course:
                changed_course = True
        if changed_course:
            new_id = self._next_id(new_course)
            student.course = new_course
            student.id = new_id
            del self.students[old_id]
            self.students[new_id] = student
        else:
            self.students[student.id] = student
        self._save()
        return student

    def delete_student(self, student_id: str) -> bool:
        if student_id in self.students:
            del self.students[student_id]
            self._save()
            return True
        return False


if __name__ == '__main__':
    # quick manual smoke test
    db = StudentDB(storage_path=':memory:')
    a = db.create_student('Alice', 'GES')
    b = db.create_student('Bob', 'GES')
    c = db.create_student('Carol', 'GEC')
    print('Students:')
    for s in db.list_students():
        print(f"{s.id}: {s.name} - {s.course}")