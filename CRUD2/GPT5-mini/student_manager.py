import json
import os
from typing import Dict, List

DB_FILE = os.path.join(os.path.dirname(__file__), 'students.json')

class Student:
    def __init__(self, student_id: str, name: str, course: str):
        self.id = student_id
        self.name = name
        self.course = course

    def to_dict(self):
        return {'id': self.id, 'name': self.name, 'course': self.course}

    @staticmethod
    def from_dict(d):
        return Student(d['id'], d['name'], d['course'])

class StudentManager:
    def __init__(self, db_file: str = DB_FILE):
        self.db_file = db_file
        self.students: Dict[str, Student] = {}
        self._load()

    def _load(self):
        if os.path.exists(self.db_file):
            with open(self.db_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for s in data:
                    student = Student.from_dict(s)
                    self.students[student.id] = student

    def _save(self):
        with open(self.db_file, 'w', encoding='utf-8') as f:
            json.dump([s.to_dict() for s in self.students.values()], f, indent=2)

    def _next_seq_for_course(self, course: str) -> int:
        max_seq = 0
        prefix = course.upper()
        for sid in self.students.keys():
            if sid.startswith(prefix):
                try:
                    seq = int(sid[len(prefix):])
                    if seq > max_seq:
                        max_seq = seq
                except ValueError:
                    continue
        return max_seq + 1

    def create_student(self, name: str, course: str) -> Student:
        course = course.upper()
        seq = self._next_seq_for_course(course)
        student_id = f"{course}{seq}"
        student = Student(student_id, name, course)
        self.students[student_id] = student
        self._save()
        return student

    def list_students(self) -> List[Student]:
        return list(self.students.values())

    def get_student(self, student_id: str) -> Student:
        return self.students.get(student_id)

    def update_student(self, student_id: str, name: str = None, course: str = None) -> Student:
        student = self.get_student(student_id)
        if not student:
            return None
        if name:
            student.name = name
        if course:
            course = course.upper()
            if course != student.course:
                # create a new ID for new course maintaining sequential per-course numbering
                seq = self._next_seq_for_course(course)
                new_id = f"{course}{seq}"
                # remove old entry and assign new
                del self.students[student_id]
                student.id = new_id
                student.course = course
                self.students[new_id] = student
            else:
                student.course = course
        self._save()
        return student

    def delete_student(self, student_id: str) -> bool:
        if student_id in self.students:
            del self.students[student_id]
            self._save()
            return True
        return False
