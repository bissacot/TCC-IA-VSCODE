import json
from pathlib import Path
from typing import Optional, List, Dict

class StudentManager:
    """Simple CRUD manager for students."""
    
    def __init__(self, data_file: str = "students_data.json"):
        self.data_file = data_file
        self.students: Dict[str, dict] = {}
        self.course_counters: Dict[str, int] = {}
        self.load_students()
    
    def load_students(self) -> None:
        """Load students from JSON file if it exists."""
        if Path(self.data_file).exists():
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.students = data.get('students', {})
                    self.course_counters = data.get('course_counters', {})
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error loading data: {e}")
                self.students = {}
                self.course_counters = {}
    
    def save_students(self) -> None:
        """Save students to JSON file."""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'students': self.students,
                    'course_counters': self.course_counters
                }, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"Error saving data: {e}")
    
    def generate_student_id(self, course_code: str) -> str:
        """Generate a unique student ID based on course code and sequence number."""
        course_code = course_code.upper()
        if course_code not in self.course_counters:
            self.course_counters[course_code] = 0
        
        self.course_counters[course_code] += 1
        return f"{course_code}{self.course_counters[course_code]}"
    
    def create_student(self, name: str, course_code: str) -> tuple[bool, str]:
        """Create a new student and return (success, student_id or error_message)."""
        if not name or not course_code:
            return False, "Name and course code cannot be empty."
        
        name = name.strip()
        course_code = course_code.upper()
        
        student_id = self.generate_student_id(course_code)
        
        self.students[student_id] = {
            'id': student_id,
            'name': name,
            'course': course_code
        }
        
        self.save_students()
        return True, student_id
    
    def list_students(self) -> List[dict]:
        """Return all students."""
        return sorted(
            self.students.values(),
            key=lambda x: (x['course'], int(x['id'][len(x['course']):]))
        )
    
    def get_student(self, student_id: str) -> Optional[dict]:
        """Get a specific student by ID."""
        return self.students.get(student_id.upper())
    
    def update_student(self, student_id: str, name: Optional[str] = None) -> tuple[bool, str]:
        """Update a student's information."""
        student_id = student_id.upper()
        
        if student_id not in self.students:
            return False, f"Student {student_id} not found."
        
        if name:
            self.students[student_id]['name'] = name.strip()
            self.save_students()
            return True, f"Student {student_id} updated successfully."
        
        return False, "No fields to update."
    
    def delete_student(self, student_id: str) -> tuple[bool, str]:
        """Delete a student."""
        student_id = student_id.upper()
        
        if student_id not in self.students:
            return False, f"Student {student_id} not found."
        
        del self.students[student_id]
        self.save_students()
        return True, f"Student {student_id} deleted successfully."


def display_menu() -> None:
    """Display the main menu."""
    print("\n" + "="*50)
    print("STUDENT CRUD SYSTEM")
    print("="*50)
    print("1. Register a new student")
    print("2. List all students")
    print("3. Search for a student")
    print("4. Update a student")
    print("5. Delete a student")
    print("6. Exit")
    print("="*50)


def main() -> None:
    """Main application loop."""
    manager = StudentManager()
    
    while True:
        display_menu()
        choice = input("Enter your choice (1-6): ").strip()
        
        if choice == '1':
            # Register a new student
            name = input("Enter student name: ").strip()
            course_code = input("Enter course code (e.g., GES, GEC): ").strip()
            
            if name and course_code:
                success, result = manager.create_student(name, course_code)
                if success:
                    print(f"\n✓ Student registered successfully!")
                    print(f"  Student ID: {result}")
                    print(f"  Name: {name}")
                    print(f"  Course: {course_code.upper()}")
                else:
                    print(f"\n✗ Error: {result}")
            else:
                print("\n✗ Name and course code are required.")
        
        elif choice == '2':
            # List all students
            students = manager.list_students()
            if students:
                print("\n" + "-"*70)
                print(f"{'Student ID':<15} {'Name':<30} {'Course':<15}")
                print("-"*70)
                for student in students:
                    print(f"{student['id']:<15} {student['name']:<30} {student['course']:<15}")
                print("-"*70)
                print(f"Total: {len(students)} student(s)")
            else:
                print("\n✗ No students registered yet.")
        
        elif choice == '3':
            # Search for a student
            student_id = input("Enter student ID: ").strip()
            student = manager.get_student(student_id)
            
            if student:
                print("\n" + "-"*50)
                print(f"Student ID: {student['id']}")
                print(f"Name: {student['name']}")
                print(f"Course: {student['course']}")
                print("-"*50)
            else:
                print(f"\n✗ Student {student_id} not found.")
        
        elif choice == '4':
            # Update a student
            student_id = input("Enter student ID to update: ").strip()
            student = manager.get_student(student_id)
            
            if student:
                new_name = input(f"Enter new name (current: {student['name']}): ").strip()
                if new_name:
                    success, message = manager.update_student(student_id, name=new_name)
                    if success:
                        print(f"\n✓ {message}")
                    else:
                        print(f"\n✗ {message}")
                else:
                    print("\n✗ New name cannot be empty.")
            else:
                print(f"\n✗ Student {student_id} not found.")
        
        elif choice == '5':
            # Delete a student
            student_id = input("Enter student ID to delete: ").strip()
            confirm = input(f"Are you sure you want to delete {student_id}? (y/n): ").strip().lower()
            
            if confirm == 'y':
                success, message = manager.delete_student(student_id)
                if success:
                    print(f"\n✓ {message}")
                else:
                    print(f"\n✗ {message}")
            else:
                print("\n✗ Deletion cancelled.")
        
        elif choice == '6':
            print("\nGoodbye!")
            break
        
        else:
            print("\n✗ Invalid choice. Please enter a number between 1 and 6.")


if __name__ == "__main__":
    main()
