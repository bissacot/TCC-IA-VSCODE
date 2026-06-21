"""
Student Management System - CRUD Application
Manages student records with automatic student ID generation based on course code
"""

class StudentManagementSystem:
    def __init__(self):
        """Initialize the student management system with empty storage and counters."""
        self.students = {}  # Dictionary to store students: {student_id: student_data}
        self.course_counters = {}  # Dictionary to track sequential numbers per course
    
    def _generate_student_id(self, course_code):
        """
        Generate a student ID with format: CourseCode + SequentialNumber
        
        Args:
            course_code (str): The course code (e.g., 'GES', 'GEC')
        
        Returns:
            str: Generated student ID (e.g., 'GES1', 'GES2')
        """
        # Normalize course code to uppercase
        course_code = course_code.upper()
        
        # Increment counter for this course code
        if course_code not in self.course_counters:
            self.course_counters[course_code] = 1
        else:
            self.course_counters[course_code] += 1
        
        # Generate and return the student ID
        return f"{course_code}{self.course_counters[course_code]}"
    
    def create(self, name, course_code):
        """
        Create a new student record.
        
        Args:
            name (str): Student's name
            course_code (str): Student's course code
        
        Returns:
            tuple: (success: bool, message: str, student_id: str or None)
        """
        # Validate inputs
        if not name or not name.strip():
            return False, "Error: Name cannot be empty.", None
        
        if not course_code or not course_code.strip():
            return False, "Error: Course code cannot be empty.", None
        
        # Generate student ID
        student_id = self._generate_student_id(course_code)
        
        # Store student data
        self.students[student_id] = {
            'name': name.strip(),
            'course_code': course_code.upper(),
            'student_id': student_id
        }
        
        return True, f"Student '{name}' created successfully with ID: {student_id}", student_id
    
    def read(self, student_id=None):
        """
        Read student records.
        
        Args:
            student_id (str, optional): Specific student ID to read. If None, returns all students.
        
        Returns:
            tuple: (success: bool, message: str, data: dict or list)
        """
        if student_id is None:
            # Return all students
            if not self.students:
                return False, "No students found in the system.", []
            return True, f"Found {len(self.students)} student(s).", list(self.students.values())
        
        # Return specific student
        student_id = student_id.upper()
        if student_id in self.students:
            return True, "Student found.", self.students[student_id]
        else:
            return False, f"Error: Student with ID '{student_id}' not found.", None
    
    def update(self, student_id, name=None, course_code=None):
        """
        Update a student record.
        
        Args:
            student_id (str): Student ID to update
            name (str, optional): New name (if provided)
            course_code (str, optional): New course code (if provided)
        
        Returns:
            tuple: (success: bool, message: str)
        """
        student_id = student_id.upper()
        
        if student_id not in self.students:
            return False, f"Error: Student with ID '{student_id}' not found."
        
        # Update name if provided
        if name is not None and name.strip():
            self.students[student_id]['name'] = name.strip()
        
        # Update course code if provided
        if course_code is not None and course_code.strip():
            self.students[student_id]['course_code'] = course_code.upper()
        
        if name is None and course_code is None:
            return False, "Error: No data provided to update."
        
        return True, f"Student '{student_id}' updated successfully."
    
    def delete(self, student_id):
        """
        Delete a student record.
        
        Args:
            student_id (str): Student ID to delete
        
        Returns:
            tuple: (success: bool, message: str)
        """
        student_id = student_id.upper()
        
        if student_id not in self.students:
            return False, f"Error: Student with ID '{student_id}' not found."
        
        student_name = self.students[student_id]['name']
        del self.students[student_id]
        
        return True, f"Student '{student_name}' (ID: {student_id}) deleted successfully."
    
    def display_students(self):
        """Display all students in a formatted table."""
        if not self.students:
            print("\n" + "="*60)
            print("No students in the system.")
            print("="*60)
            return
        
        print("\n" + "="*60)
        print("STUDENT LIST")
        print("="*60)
        print(f"{'Student ID':<15} {'Name':<25} {'Course Code':<15}")
        print("-"*60)
        
        for student_id in sorted(self.students.keys()):
            student = self.students[student_id]
            print(f"{student['student_id']:<15} {student['name']:<25} {student['course_code']:<15}")
        
        print("="*60 + "\n")


def display_menu():
    """Display the main menu."""
    print("\n" + "="*60)
    print("STUDENT MANAGEMENT SYSTEM")
    print("="*60)
    print("1. Create (Register a new student)")
    print("2. Read (View all or specific student)")
    print("3. Update (Modify student information)")
    print("4. Delete (Remove a student)")
    print("5. List All Students")
    print("6. Exit")
    print("="*60)


def main():
    """Main application loop."""
    system = StudentManagementSystem()
    
    while True:
        display_menu()
        choice = input("Enter your choice (1-6): ").strip()
        
        if choice == '1':
            # Create
            print("\n--- Register New Student ---")
            name = input("Enter student name: ").strip()
            course_code = input("Enter course code (e.g., GES, GEC): ").strip()
            
            success, message, student_id = system.create(name, course_code)
            print(message)
        
        elif choice == '2':
            # Read
            print("\n--- View Student Information ---")
            view_all = input("View all students? (y/n): ").strip().lower()
            
            if view_all == 'y':
                success, message, data = system.read()
                print(message)
                if success:
                    print(f"\n{'Student ID':<15} {'Name':<25} {'Course Code':<15}")
                    print("-"*60)
                    for student in data:
                        print(f"{student['student_id']:<15} {student['name']:<25} {student['course_code']:<15}")
            else:
                student_id = input("Enter student ID: ").strip()
                success, message, data = system.read(student_id)
                print(message)
                if success:
                    print(f"\nStudent ID: {data['student_id']}")
                    print(f"Name: {data['name']}")
                    print(f"Course Code: {data['course_code']}")
        
        elif choice == '3':
            # Update
            print("\n--- Update Student Information ---")
            student_id = input("Enter student ID to update: ").strip()
            
            new_name = input("Enter new name (or press Enter to skip): ").strip()
            new_course = input("Enter new course code (or press Enter to skip): ").strip()
            
            # Only pass non-empty values
            success, message = system.update(
                student_id,
                name=new_name if new_name else None,
                course_code=new_course if new_course else None
            )
            print(message)
        
        elif choice == '4':
            # Delete
            print("\n--- Delete Student ---")
            student_id = input("Enter student ID to delete: ").strip()
            
            # Confirm deletion
            confirm = input(f"Are you sure you want to delete student '{student_id}'? (y/n): ").strip().lower()
            if confirm == 'y':
                success, message = system.delete(student_id)
                print(message)
            else:
                print("Deletion cancelled.")
        
        elif choice == '5':
            # List All
            system.display_students()
        
        elif choice == '6':
            # Exit
            print("\nThank you for using Student Management System. Goodbye!")
            break
        
        else:
            print("Invalid choice. Please enter a number between 1 and 6.")


if __name__ == "__main__":
    main()
