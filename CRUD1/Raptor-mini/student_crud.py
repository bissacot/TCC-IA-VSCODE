"""Simple student CRUD application.
Each student has a name, course code, and a generated student ID.
Student IDs are formed by course code + sequential integer, e.g. GES1, GES2.
"""

class Student:
    def __init__(self, student_id: str, name: str, course_code: str):
        self.student_id = student_id
        self.name = name
        self.course_code = course_code

    def __repr__(self) -> str:
        return f"Student(student_id='{self.student_id}', name='{self.name}', course_code='{self.course_code}')"


class StudentRegistry:
    def __init__(self):
        self.students = {}
        self.course_counts = {}

    def _generate_student_id(self, course_code: str) -> str:
        normalized = course_code.strip().upper()
        count = self.course_counts.get(normalized, 0) + 1
        self.course_counts[normalized] = count
        return f"{normalized}{count}"

    def create_student(self, name: str, course_code: str) -> Student:
        if not name.strip():
            raise ValueError("Name cannot be empty")
        if not course_code.strip():
            raise ValueError("Course code cannot be empty")

        student_id = self._generate_student_id(course_code)
        student = Student(student_id, name.strip(), course_code.strip().upper())
        self.students[student_id] = student
        return student

    def read_student(self, student_id: str) -> Student | None:
        return self.students.get(student_id.strip().upper())

    def list_students(self) -> list[Student]:
        return sorted(self.students.values(), key=lambda student: student.student_id)

    def update_student(self, student_id: str, name: str | None = None, course_code: str | None = None) -> Student:
        student_id = student_id.strip().upper()
        student = self.students.get(student_id)
        if student is None:
            raise KeyError(f"Student with ID {student_id} not found")

        if name is not None and name.strip():
            student.name = name.strip()

        if course_code is not None and course_code.strip():
            student.course_code = course_code.strip().upper()

        return student

    def delete_student(self, student_id: str) -> bool:
        student_id = student_id.strip().upper()
        return self.students.pop(student_id, None) is not None


def main() -> None:
    registry = StudentRegistry()

    def print_menu() -> None:
        print("\nStudent CRUD Menu")
        print("1. Register student")
        print("2. List students")
        print("3. Update student")
        print("4. Delete student")
        print("5. Show student details")
        print("0. Exit")

    while True:
        print_menu()
        choice = input("Choose an option: ").strip()

        if choice == "1":
            name = input("Student name: ")
            course_code = input("Course code (e.g. GES, GEC): ")
            try:
                student = registry.create_student(name, course_code)
                print(f"Registered: {student}")
            except ValueError as exc:
                print(f"Error: {exc}")

        elif choice == "2":
            students = registry.list_students()
            if not students:
                print("No students registered.")
            else:
                print("Registered students:")
                for student in students:
                    print(f"- {student.student_id}: {student.name} ({student.course_code})")

        elif choice == "3":
            student_id = input("Student ID to update: ")
            name = input("New name (leave blank to keep current): ")
            course_code = input("New course code (leave blank to keep current): ")
            try:
                student = registry.update_student(student_id, name if name else None, course_code if course_code else None)
                print(f"Updated: {student}")
            except KeyError as exc:
                print(f"Error: {exc}")

        elif choice == "4":
            student_id = input("Student ID to delete: ")
            if registry.delete_student(student_id):
                print(f"Deleted student {student_id.strip().upper()}")
            else:
                print("Student not found.")

        elif choice == "5":
            student_id = input("Student ID to show: ")
            student = registry.read_student(student_id)
            if student:
                print(f"{student.student_id}: {student.name} ({student.course_code})")
            else:
                print("Student not found.")

        elif choice == "0":
            print("Goodbye.")
            break

        else:
            print("Invalid option. Please try again.")


if __name__ == "__main__":
    main()
