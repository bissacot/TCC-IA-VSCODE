import re

class StudentRegistry:
    def __init__(self):
        self.students = []
        self.course_counters = {}

    def _generate_student_id(self, course_code):
        code = course_code.upper()
        self.course_counters.setdefault(code, 0)
        self.course_counters[code] += 1
        return f"{code}{self.course_counters[code]}"

    def create_student(self, name, course_code):
        if not name.strip():
            raise ValueError("Student name cannot be empty.")
        if not re.match(r"^[A-Za-z]{3}$", course_code):
            raise ValueError("Course code must be exactly 3 letters, e.g. GES, GEC.")

        student_id = self._generate_student_id(course_code)
        student = {
            "id": student_id,
            "name": name.strip(),
            "course_code": course_code.upper()
        }
        self.students.append(student)
        return student

    def list_students(self):
        return list(self.students)

    def find_student(self, student_id):
        return next((student for student in self.students if student["id"] == student_id.upper()), None)

    def update_student(self, student_id, new_name=None, new_course_code=None):
        student = self.find_student(student_id)
        if student is None:
            raise ValueError(f"Student with ID {student_id} not found.")

        if new_name is not None and new_name.strip():
            student["name"] = new_name.strip()

        if new_course_code is not None:
            if not re.match(r"^[A-Za-z]{3}$", new_course_code):
                raise ValueError("Course code must be exactly 3 letters, e.g. GES, GEC.")
            student["course_code"] = new_course_code.upper()

        return student

    def delete_student(self, student_id):
        student = self.find_student(student_id)
        if student is None:
            raise ValueError(f"Student with ID {student_id} not found.")
        self.students.remove(student)
        return student


def print_menu():
    print("\nStudent CRUD Registry")
    print("1. Register student")
    print("2. List students")
    print("3. Update student")
    print("4. Delete student")
    print("5. Exit")


def main():
    registry = StudentRegistry()

    while True:
        print_menu()
        choice = input("Choose an option: ").strip()

        try:
            if choice == "1":
                name = input("Student name: ")
                course_code = input("Course code (3 letters): ")
                student = registry.create_student(name, course_code)
                print(f"Registered: {student}")

            elif choice == "2":
                students = registry.list_students()
                if not students:
                    print("No students registered.")
                else:
                    for student in students:
                        print(f"ID: {student['id']}, Name: {student['name']}, Course: {student['course_code']}")

            elif choice == "3":
                student_id = input("Student ID to update: ")
                new_name = input("New name (leave blank to keep current): ")
                new_course_code = input("New course code (leave blank to keep current): ")
                updated = registry.update_student(
                    student_id,
                    new_name=new_name if new_name.strip() else None,
                    new_course_code=new_course_code if new_course_code.strip() else None
                )
                print(f"Updated: {updated}")

            elif choice == "4":
                student_id = input("Student ID to delete: ")
                deleted = registry.delete_student(student_id)
                print(f"Deleted: {deleted}")

            elif choice == "5":
                print("Goodbye.")
                break

            else:
                print("Invalid option. Please choose 1-5.")

        except ValueError as error:
            print(f"Error: {error}")


if __name__ == "__main__":
    main()
