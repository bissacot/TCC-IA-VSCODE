import re

class Student:
    def __init__(self, name: str, course_code: str, student_id: str):
        self.name = name
        self.course_code = course_code.upper()
        self.student_id = student_id

    def __repr__(self):
        return f"Student(name={self.name!r}, course_code={self.course_code!r}, student_id={self.student_id!r})"


class StudentRegistry:
    def __init__(self):
        self.students = []
        self.next_id = {}

    def _generate_student_id(self, course_code: str) -> str:
        code = course_code.upper()
        self.next_id.setdefault(code, 1)
        student_id = f"{code}{self.next_id[code]}"
        self.next_id[code] += 1
        return student_id

    def create_student(self, name: str, course_code: str) -> Student:
        if not name.strip():
            raise ValueError("Student name cannot be empty.")
        if not re.fullmatch(r"[A-Za-z]{2,5}", course_code.strip()):
            raise ValueError("Course code must be 2 to 5 letters.")

        student_id = self._generate_student_id(course_code)
        student = Student(name=name.strip(), course_code=course_code.strip(), student_id=student_id)
        self.students.append(student)
        return student

    def read_students(self):
        return list(self.students)

    def find_student(self, student_id: str):
        return next((student for student in self.students if student.student_id == student_id), None)

    def update_student(self, student_id: str, name: str = None, course_code: str = None) -> Student:
        student = self.find_student(student_id)
        if not student:
            raise ValueError(f"Student with ID {student_id} not found.")

        if name is not None:
            if not name.strip():
                raise ValueError("Student name cannot be empty.")
            student.name = name.strip()

        if course_code is not None:
            if not re.fullmatch(r"[A-Za-z]{2,5}", course_code.strip()):
                raise ValueError("Course code must be 2 to 5 letters.")
            student.course_code = course_code.strip().upper()

        return student

    def delete_student(self, student_id: str) -> bool:
        student = self.find_student(student_id)
        if student:
            self.students.remove(student)
            return True
        return False


def main():
    registry = StudentRegistry()
    print("Simple Student CRUD")
    print("Commands: create, list, update, delete, exit")

    while True:
        command = input("Enter command: ").strip().lower()
        if command == "create":
            name = input("Student name: ").strip()
            course_code = input("Course code: ").strip().upper()
            try:
                student = registry.create_student(name, course_code)
                print(f"Created: {student.student_id} - {student.name} ({student.course_code})")
            except ValueError as error:
                print(f"Error: {error}")

        elif command == "list":
            students = registry.read_students()
            if not students:
                print("No students registered.")
            else:
                for student in students:
                    print(f"{student.student_id}: {student.name} ({student.course_code})")

        elif command == "update":
            student_id = input("Student ID to update: ").strip().upper()
            student = registry.find_student(student_id)
            if not student:
                print(f"Student with ID {student_id} not found.")
                continue
            new_name = input(f"New name (leave blank to keep '{student.name}'): ").strip()
            new_course = input(f"New course code (leave blank to keep '{student.course_code}'): ").strip()
            try:
                updated = registry.update_student(
                    student_id,
                    name=new_name if new_name else None,
                    course_code=new_course if new_course else None,
                )
                print(f"Updated: {updated.student_id}: {updated.name} ({updated.course_code})")
            except ValueError as error:
                print(f"Error: {error}")

        elif command == "delete":
            student_id = input("Student ID to delete: ").strip().upper()
            deleted = registry.delete_student(student_id)
            if deleted:
                print(f"Deleted student {student_id}.")
            else:
                print(f"Student with ID {student_id} not found.")

        elif command == "exit":
            print("Exiting.")
            break

        else:
            print("Unknown command. Use create, list, update, delete, or exit.")


if __name__ == "__main__":
    main()
