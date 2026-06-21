import json
import os
from typing import List, Dict, Optional

class Student:
    """Represents a student with name, course code, and automatically generated student ID."""
    
    def __init__(self, name: str, course_code: str, student_id: str):
        self.name = name
        self.course_code = course_code
        self.student_id = student_id
    
    def to_dict(self) -> Dict:
        """Convert student to dictionary."""
        return {
            'name': self.name,
            'course_code': self.course_code,
            'student_id': self.student_id
        }
    
    def __str__(self) -> str:
        return f"ID: {self.student_id} | Name: {self.name} | Course: {self.course_code}"


class StudentManager:
    """Manages CRUD operations for students."""
    
    def __init__(self, data_file: str = "students.json"):
        self.data_file = data_file
        self.students: List[Student] = []
        self.load_students()
    
    def load_students(self) -> None:
        """Load students from JSON file."""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                    self.students = [
                        Student(s['name'], s['course_code'], s['student_id'])
                        for s in data
                    ]
            except Exception as e:
                print(f"Error loading students: {e}")
                self.students = []
        else:
            self.students = []
    
    def save_students(self) -> None:
        """Save students to JSON file."""
        try:
            with open(self.data_file, 'w') as f:
                json.dump([s.to_dict() for s in self.students], f, indent=2)
        except Exception as e:
            print(f"Error saving students: {e}")
    
    def generate_student_id(self, course_code: str) -> str:
        """Generate next student ID for a given course code."""
        # Count existing students with the same course code
        count = sum(1 for s in self.students if s.course_code == course_code)
        return f"{course_code}{count + 1}"
    
    def create_student(self, name: str, course_code: str) -> Optional[Student]:
        """Create and add a new student."""
        # Validate input
        if not name or not name.strip():
            print("Error: Student name cannot be empty.")
            return None
        
        if not course_code or not course_code.strip():
            print("Error: Course code cannot be empty.")
            return None
        
        # Generate student ID
        student_id = self.generate_student_id(course_code.upper())
        
        # Create student
        student = Student(name.strip(), course_code.upper(), student_id)
        self.students.append(student)
        self.save_students()
        
        print(f"✓ Student created successfully: {student}")
        return student
    
    def read_all_students(self) -> List[Student]:
        """Get all students."""
        return self.students
    
    def read_student_by_id(self, student_id: str) -> Optional[Student]:
        """Get a student by their ID."""
        for student in self.students:
            if student.student_id == student_id:
                return student
        return None
    
    def list_students_by_course(self, course_code: str) -> List[Student]:
        """Get all students from a specific course."""
        return [s for s in self.students if s.course_code == course_code.upper()]
    
    def update_student(self, student_id: str, name: Optional[str] = None, 
                      course_code: Optional[str] = None) -> bool:
        """Update a student's information (except student ID)."""
        student = self.read_student_by_id(student_id)
        
        if not student:
            print(f"Error: Student with ID '{student_id}' not found.")
            return False
        
        if name and name.strip():
            student.name = name.strip()
        
        if course_code and course_code.strip():
            old_course = student.course_code
            student.course_code = course_code.upper()
            # Note: Student ID remains the same even if course code changes
            print(f"Note: Student ID remains '{student.student_id}' (course code changed from {old_course} to {course_code.upper()})")
        
        self.save_students()
        print(f"✓ Student updated successfully: {student}")
        return True
    
    def delete_student(self, student_id: str) -> bool:
        """Delete a student by their ID."""
        student = self.read_student_by_id(student_id)
        
        if not student:
            print(f"Error: Student with ID '{student_id}' not found.")
            return False
        
        self.students.remove(student)
        self.save_students()
        print(f"✓ Student deleted successfully: {student}")
        return True
    
    def display_all_students(self) -> None:
        """Display all students in a formatted way."""
        if not self.students:
            print("\n📋 No students registered yet.\n")
            return
        
        print("\n" + "="*60)
        print("ALL STUDENTS".center(60))
        print("="*60)
        for i, student in enumerate(self.students, 1):
            print(f"{i}. {student}")
        print("="*60 + "\n")
    
    def display_students_by_course(self, course_code: str) -> None:
        """Display students from a specific course."""
        students = self.list_students_by_course(course_code)
        
        if not students:
            print(f"\n❌ No students found for course '{course_code}'.\n")
            return
        
        print("\n" + "="*60)
        print(f"STUDENTS FROM {course_code}".center(60))
        print("="*60)
        for i, student in enumerate(students, 1):
            print(f"{i}. {student}")
        print("="*60 + "\n")


def main():
    """Main menu for the student management system."""
    manager = StudentManager()
    
    while True:
        print("\n" + "="*60)
        print("STUDENT MANAGEMENT SYSTEM".center(60))
        print("="*60)
        print("1. Register a new student")
        print("2. List all students")
        print("3. List students by course")
        print("4. Update student information")
        print("5. Delete a student")
        print("6. Exit")
        print("="*60)
        
        choice = input("\nEnter your choice (1-6): ").strip()
        
        if choice == '1':
            # Register a new student
            print("\n--- Register New Student ---")
            name = input("Enter student name: ").strip()
            course_code = input("Enter course code (e.g., GES, GEC): ").strip()
            manager.create_student(name, course_code)
        
        elif choice == '2':
            # List all students
            manager.display_all_students()
        
        elif choice == '3':
            # List students by course
            print("\n--- List Students by Course ---")
            course_code = input("Enter course code: ").strip()
            manager.display_students_by_course(course_code)
        
        elif choice == '4':
            # Update student
            print("\n--- Update Student ---")
            student_id = input("Enter student ID to update: ").strip()
            print("(Leave blank to skip updating a field)")
            new_name = input("New name (or press Enter to skip): ").strip()
            new_course = input("New course code (or press Enter to skip): ").strip()
            
            manager.update_student(
                student_id,
                name=new_name if new_name else None,
                course_code=new_course if new_course else None
            )
        
        elif choice == '5':
            # Delete student
            print("\n--- Delete Student ---")
            student_id = input("Enter student ID to delete: ").strip()
            confirm = input(f"Are you sure you want to delete student '{student_id}'? (yes/no): ").strip().lower()
            if confirm == 'yes':
                manager.delete_student(student_id)
        
        elif choice == '6':
            # Exit
            print("\n✓ Thank you for using Student Management System. Goodbye!\n")
            break
        
        else:
            print("\n❌ Invalid choice. Please enter a number between 1 and 6.")


if __name__ == "__main__":
    main()
