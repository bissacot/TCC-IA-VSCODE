import re

class Student:
    def __init__(self, name: str, course_code: str, student_id: str):
        self.name = name
        self.course_code = course_code
        self.student_id = student_id

    def __repr__(self):
        return f"Student(name={self.name!r}, course_code={self.course_code!r}, student_id={self.student_id!r})"


class StudentRegistry:
    def __init__(self):
        self.students = []
        self.sequence = {}

    def _next_id(self, course_code: str) -> str:
        course_code = course_code.upper()
        count = self.sequence.get(course_code, 0) + 1
        self.sequence[course_code] = count
        return f"{course_code}{count}"

    def create_student(self, name: str, course_code: str) -> Student:
        course_code = course_code.strip().upper()
        if not re.fullmatch(r"[A-Z]{2,4}", course_code):
            raise ValueError("Course code must be 2 to 4 letters.")
        student_id = self._next_id(course_code)
        student = Student(name.strip(), course_code, student_id)
        self.students.append(student)
        return student

    def list_students(self):
        return list(self.students)

    def find_student(self, student_id: str):
        student_id = student_id.strip().upper()
        for student in self.students:
            if student.student_id == student_id:
                return student
        return None

    def update_student(self, student_id: str, name: str = None, course_code: str = None) -> Student:
        student = self.find_student(student_id)
        if student is None:
            raise ValueError(f"Student with ID {student_id} not found.")
        if name is not None:
            student.name = name.strip()
        if course_code is not None:
            course_code = course_code.strip().upper()
            if not re.fullmatch(r"[A-Z]{2,4}", course_code):
                raise ValueError("Course code must be 2 to 4 letters.")
            if course_code != student.course_code:
                student.course_code = course_code
                # Note: existing ID remains unchanged for simplicity
        return student

    def delete_student(self, student_id: str) -> bool:
        student = self.find_student(student_id)
        if student is None:
            return False
        self.students.remove(student)
        return True


def main():
    registry = StudentRegistry()

    while True:
        print("\nStudent CRUD Menu")
        print("1. Create student")
        print("2. List students")
        print("3. Update student")
        print("4. Delete student")
        print("5. Exit")
        choice = input("Choose an option: ").strip()

        try:
            if choice == "1":
                name = input("Student name: ").strip()
                course_code = input("Course code (e.g. GES, GEC): ").strip()
                student = registry.create_student(name, course_code)
                print(f"Created: {student}")
            elif choice == "2":
                students = registry.list_students()
                if not students:
                    print("No students registered.")
                else:
                    for student in students:
                        print(f"{student.student_id}: {student.name} ({student.course_code})")
            elif choice == "3":
                student_id = input("Student ID to update: ").strip()
                name = input("New name (leave blank to keep current): ").strip()
                course_code = input("New course code (leave blank to keep current): ").strip()
                updated = registry.update_student(
                    student_id,
                    name=name if name else None,
                    course_code=course_code if course_code else None,
                )
                print(f"Updated: {updated}")
            elif choice == "4":
                student_id = input("Student ID to delete: ").strip()
                deleted = registry.delete_student(student_id)
                if deleted:
                    print(f"Deleted student {student_id}.")
                else:
                    print(f"Student {student_id} not found.")
            elif choice == "5":
                print("Exiting.")
                break
            else:
                print("Invalid choice. Please select 1-5.")
        except ValueError as error:
            print(f"Error: {error}")


if __name__ == "__main__":
    main()
