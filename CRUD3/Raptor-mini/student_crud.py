class StudentRegistry:
    def __init__(self):
        self.students = []
        self.next_id_by_course = {}

    def _generate_student_id(self, course_code: str) -> str:
        course_code = course_code.upper().strip()
        count = self.next_id_by_course.get(course_code, 0) + 1
        self.next_id_by_course[course_code] = count
        return f"{course_code}{count}"

    def create_student(self, name: str, course_code: str) -> dict:
        student_id = self._generate_student_id(course_code)
        student = {
            "name": name.strip(),
            "course_code": course_code.upper().strip(),
            "student_id": student_id,
        }
        self.students.append(student)
        return student

    def list_students(self) -> list:
        return list(self.students)

    def find_student(self, student_id: str) -> dict | None:
        normalized_id = student_id.strip().upper()
        for student in self.students:
            if student["student_id"] == normalized_id:
                return student
        return None

    def update_student(self, student_id: str, name: str | None = None, course_code: str | None = None) -> dict | None:
        student = self.find_student(student_id)
        if not student:
            return None

        if name is not None and name.strip():
            student["name"] = name.strip()

        if course_code is not None and course_code.strip():
            student["course_code"] = course_code.upper().strip()

        return student

    def delete_student(self, student_id: str) -> bool:
        student = self.find_student(student_id)
        if not student:
            return False
        self.students.remove(student)
        return True


def main():
    registry = StudentRegistry()

    while True:
        print("\nStudent CRUD Menu")
        print("1. Register student")
        print("2. List students")
        print("3. Update student")
        print("4. Delete student")
        print("5. Exit")
        choice = input("Choose an option: ").strip()

        if choice == "1":
            name = input("Student name: ").strip()
            course_code = input("Course code (e.g. GES, GEC): ").strip().upper()
            if not name or not course_code:
                print("Name and course code are required.")
                continue
            student = registry.create_student(name, course_code)
            print(f"Registered student: {student}")

        elif choice == "2":
            students = registry.list_students()
            if not students:
                print("No students registered.")
            else:
                for student in students:
                    print(f"ID: {student['student_id']}, Name: {student['name']}, Course: {student['course_code']}")

        elif choice == "3":
            student_id = input("Student ID to update: ").strip().upper()
            student = registry.find_student(student_id)
            if not student:
                print("Student not found.")
                continue
            name = input(f"New name (leave blank to keep '{student['name']}'): ").strip()
            course_code = input(f"New course code (leave blank to keep '{student['course_code']}'): ").strip().upper()
            updated = registry.update_student(student_id, name or None, course_code or None)
            print(f"Updated student: {updated}")

        elif choice == "4":
            student_id = input("Student ID to delete: ").strip().upper()
            if registry.delete_student(student_id):
                print("Student deleted.")
            else:
                print("Student not found.")

        elif choice == "5":
            print("Goodbye.")
            break

        else:
            print("Invalid option. Please choose 1-5.")


if __name__ == "__main__":
    main()
