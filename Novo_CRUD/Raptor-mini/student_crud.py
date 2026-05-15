import sys

class Student:
    def __init__(self, name: str, course_code: str, student_id: str):
        self.name = name
        self.course_code = course_code
        self.student_id = student_id

    def __repr__(self):
        return f"{self.student_id}: {self.name} ({self.course_code})"


class StudentCRUD:
    def __init__(self):
        self.students = []
        self.course_counters = {}

    def _generate_student_id(self, course_code: str) -> str:
        code = course_code.strip().upper()
        count = self.course_counters.get(code, 0) + 1
        self.course_counters[code] = count
        return f"{code}{count}"

    def register_student(self, name: str, course_code: str) -> Student:
        student_id = self._generate_student_id(course_code)
        student = Student(name.strip(), course_code.strip().upper(), student_id)
        self.students.append(student)
        return student

    def list_students(self):
        return list(self.students)

    def find_student(self, student_id: str):
        key = student_id.strip().upper()
        for student in self.students:
            if student.student_id == key:
                return student
        return None

    def update_student(self, student_id: str, new_name: str = None, new_course_code: str = None) -> bool:
        student = self.find_student(student_id)
        if not student:
            return False
        if new_name:
            student.name = new_name.strip()
        if new_course_code:
            new_code = new_course_code.strip().upper()
            if new_code != student.course_code:
                student.course_code = new_code
                student.student_id = self._generate_student_id(new_code)
        return True

    def delete_student(self, student_id: str) -> bool:
        student = self.find_student(student_id)
        if not student:
            return False
        self.students.remove(student)
        return True


def print_menu():
    print("\nStudent CRUD Menu")
    print("1. Register student")
    print("2. List students")
    print("3. Update student")
    print("4. Delete student")
    print("5. Exit")


def main():
    crud = StudentCRUD()

    while True:
        print_menu()
        choice = input("Choose an option: ").strip()

        if choice == "1":
            name = input("Student name: ")
            course_code = input("Course code (e.g. GES, GEC): ")
            student = crud.register_student(name, course_code)
            print(f"Registered: {student}")

        elif choice == "2":
            students = crud.list_students()
            if not students:
                print("No students registered.")
            else:
                print("Registered students:")
                for student in students:
                    print(f"- {student}")

        elif choice == "3":
            student_id = input("Student ID to update: ")
            student = crud.find_student(student_id)
            if not student:
                print("Student not found.")
                continue
            print(f"Found: {student}")
            new_name = input("New name (leave blank to keep current): ")
            new_course = input("New course code (leave blank to keep current): ")
            success = crud.update_student(student_id, new_name or None, new_course or None)
            if success:
                print("Student updated successfully.")
            else:
                print("Update failed.")

        elif choice == "4":
            student_id = input("Student ID to delete: ")
            success = crud.delete_student(student_id)
            if success:
                print("Student deleted.")
            else:
                print("Student not found.")

        elif choice == "5":
            print("Goodbye.")
            sys.exit(0)

        else:
            print("Invalid option, try again.")


if __name__ == "__main__":
    main()
