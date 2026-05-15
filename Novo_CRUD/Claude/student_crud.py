import json
import os
from collections import defaultdict

DATA_FILE = "students_data.json"


class StudentCRUD:
    def __init__(self):
        self.students = []
        self.course_counters = defaultdict(int)
        self.load_data()

    def load_data(self):
        """Load student data from JSON file if it exists."""
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, 'r') as f:
                    self.students = json.load(f)
                    # Rebuild course counters
                    for student in self.students:
                        course = student['course_code']
                        # Extract counter from student_id
                        counter = int(student['student_id'].replace(course, ''))
                        self.course_counters[course] = max(self.course_counters[course], counter)
            except Exception as e:
                print(f"Error loading data: {e}")
                self.students = []

    def save_data(self):
        """Save student data to JSON file."""
        try:
            with open(DATA_FILE, 'w') as f:
                json.dump(self.students, f, indent=2)
        except Exception as e:
            print(f"Error saving data: {e}")

    def create_student(self, name, course_code):
        """Register a new student and assign a unique student ID."""
        if not name or not course_code:
            print("Error: Name and course code cannot be empty!")
            return False

        # Increment counter for this course
        self.course_counters[course_code] += 1
        student_id = f"{course_code}{self.course_counters[course_code]}"

        student = {
            "student_id": student_id,
            "name": name,
            "course_code": course_code
        }

        self.students.append(student)
        self.save_data()
        print(f"✓ Student registered successfully!")
        print(f"  Student ID: {student_id}")
        print(f"  Name: {name}")
        print(f"  Course: {course_code}\n")
        return True

    def list_students(self):
        """Display all registered students."""
        if not self.students:
            print("No students registered yet.\n")
            return

        print("\n" + "="*60)
        print(f"{'Student ID':<15} {'Name':<25} {'Course':<15}")
        print("="*60)
        for student in self.students:
            print(f"{student['student_id']:<15} {student['name']:<25} {student['course_code']:<15}")
        print("="*60 + "\n")

    def update_student(self, student_id, name=None, course_code=None):
        """Update student information."""
        student = self.find_student(student_id)
        if not student:
            print(f"Error: Student with ID '{student_id}' not found!\n")
            return False

        if name:
            student['name'] = name
        if course_code:
            student['course_code'] = course_code

        self.save_data()
        print(f"✓ Student '{student_id}' updated successfully!\n")
        return True

    def delete_student(self, student_id):
        """Delete a student by student ID."""
        student = self.find_student(student_id)
        if not student:
            print(f"Error: Student with ID '{student_id}' not found!\n")
            return False

        self.students.remove(student)
        self.save_data()
        print(f"✓ Student '{student_id}' deleted successfully!\n")
        return True

    def find_student(self, student_id):
        """Find a student by student ID."""
        for student in self.students:
            if student['student_id'] == student_id:
                return student
        return None

    def display_student(self, student_id):
        """Display detailed information about a specific student."""
        student = self.find_student(student_id)
        if not student:
            print(f"Error: Student with ID '{student_id}' not found!\n")
            return False

        print("\n" + "="*40)
        print(f"Student ID: {student['student_id']}")
        print(f"Name: {student['name']}")
        print(f"Course: {student['course_code']}")
        print("="*40 + "\n")
        return True


def display_menu():
    """Display the main menu."""
    print("\n" + "="*40)
    print("       STUDENT CRUD SYSTEM")
    print("="*40)
    print("1. Register a new student")
    print("2. List all students")
    print("3. View student details")
    print("4. Update student information")
    print("5. Delete a student")
    print("6. Exit")
    print("="*40)
    print()


def main():
    """Main application loop."""
    crud = StudentCRUD()

    while True:
        display_menu()
        choice = input("Select an option (1-6): ").strip()

        if choice == "1":
            print()
            name = input("Enter student name: ").strip()
            course_code = input("Enter course code (e.g., GES, GEC): ").strip().upper()
            crud.create_student(name, course_code)

        elif choice == "2":
            crud.list_students()

        elif choice == "3":
            print()
            student_id = input("Enter student ID to view: ").strip()
            crud.display_student(student_id)

        elif choice == "4":
            print()
            student_id = input("Enter student ID to update: ").strip()
            crud.display_student(student_id)
            
            print("Leave blank to keep current value.")
            name = input("Enter new name (or press Enter to skip): ").strip() or None
            course_code = input("Enter new course code (or press Enter to skip): ").strip().upper() or None
            
            crud.update_student(student_id, name, course_code)

        elif choice == "5":
            print()
            student_id = input("Enter student ID to delete: ").strip()
            confirm = input(f"Are you sure you want to delete student '{student_id}'? (yes/no): ").strip().lower()
            if confirm == "yes":
                crud.delete_student(student_id)
            else:
                print("Deletion cancelled.\n")

        elif choice == "6":
            print("Goodbye!\n")
            break

        else:
            print("Invalid option! Please select a valid option (1-6).\n")


if __name__ == "__main__":
    main()
