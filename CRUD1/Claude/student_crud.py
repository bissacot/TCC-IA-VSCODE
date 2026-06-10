"""
Student CRUD Application
Manages student registration with auto-generated student IDs
"""

class StudentCRUD:
    def __init__(self):
        """Initialize the student database and course counters."""
        self.students = []  # List to store student records
        self.course_counters = {}  # Dictionary to track student count per course
    
    def generate_student_id(self, course_code):
        """
        Generate a unique student ID based on course code.
        
        Args:
            course_code (str): The course code (e.g., 'GES', 'GEC')
        
        Returns:
            str: The generated student ID (e.g., 'GES1', 'GES2')
        """
        course_code = course_code.upper()
        
        if course_code not in self.course_counters:
            self.course_counters[course_code] = 0
        
        self.course_counters[course_code] += 1
        return f"{course_code}{self.course_counters[course_code]}"
    
    def create_student(self, name, course_code):
        """
        Create and register a new student.
        
        Args:
            name (str): The student's name
            course_code (str): The course code
        
        Returns:
            dict: The created student record with auto-generated ID
        """
        if not name or not course_code:
            raise ValueError("Name and course code cannot be empty")
        
        student_id = self.generate_student_id(course_code)
        student = {
            'student_id': student_id,
            'name': name,
            'course_code': course_code.upper()
        }
        
        self.students.append(student)
        return student
    
    def read_all_students(self):
        """
        Retrieve all registered students.
        
        Returns:
            list: List of all student records
        """
        return self.students.copy()
    
    def read_student_by_id(self, student_id):
        """
        Retrieve a student by their ID.
        
        Args:
            student_id (str): The student ID to search for
        
        Returns:
            dict: The student record if found, None otherwise
        """
        for student in self.students:
            if student['student_id'].upper() == student_id.upper():
                return student
        return None
    
    def read_students_by_course(self, course_code):
        """
        Retrieve all students from a specific course.
        
        Args:
            course_code (str): The course code to filter by
        
        Returns:
            list: List of students in the specified course
        """
        course_code = course_code.upper()
        return [s for s in self.students if s['course_code'] == course_code]
    
    def update_student(self, student_id, name=None, course_code=None):
        """
        Update an existing student's information.
        
        Args:
            student_id (str): The student ID to update
            name (str, optional): New name for the student
            course_code (str, optional): New course code for the student
        
        Returns:
            dict: The updated student record if found, None otherwise
        """
        student = self.read_student_by_id(student_id)
        
        if student is None:
            return None
        
        if name:
            student['name'] = name
        
        if course_code:
            student['course_code'] = course_code.upper()
        
        return student
    
    def delete_student(self, student_id):
        """
        Delete a student from the database.
        
        Args:
            student_id (str): The student ID to delete
        
        Returns:
            bool: True if student was deleted, False if not found
        """
        for i, student in enumerate(self.students):
            if student['student_id'].upper() == student_id.upper():
                self.students.pop(i)
                return True
        return False
    
    def display_students(self, students=None):
        """
        Display students in a formatted table.
        
        Args:
            students (list, optional): List of students to display. If None, displays all.
        """
        if students is None:
            students = self.students
        
        if not students:
            print("\nNo students to display.")
            return
        
        print("\n" + "="*60)
        print(f"{'Student ID':<15} {'Name':<25} {'Course Code':<15}")
        print("="*60)
        for student in students:
            print(f"{student['student_id']:<15} {student['name']:<25} {student['course_code']:<15}")
        print("="*60 + "\n")


def main():
    """Main function to run the student CRUD application."""
    crud = StudentCRUD()
    
    while True:
        print("\n" + "="*60)
        print("STUDENT CRUD SYSTEM")
        print("="*60)
        print("1. Register a new student (Create)")
        print("2. List all students (Read)")
        print("3. Search student by ID (Read)")
        print("4. List students by course (Read)")
        print("5. Update student information (Update)")
        print("6. Delete a student (Delete)")
        print("7. Exit")
        print("="*60)
        
        choice = input("Select an option (1-7): ").strip()
        
        try:
            if choice == '1':
                # Create
                name = input("Enter student name: ").strip()
                course_code = input("Enter course code (e.g., GES, GEC): ").strip()
                
                student = crud.create_student(name, course_code)
                print(f"\n✓ Student registered successfully!")
                print(f"  Student ID: {student['student_id']}")
                print(f"  Name: {student['name']}")
                print(f"  Course Code: {student['course_code']}")
            
            elif choice == '2':
                # Read All
                students = crud.read_all_students()
                if students:
                    crud.display_students(students)
                else:
                    print("\nNo students registered yet.")
            
            elif choice == '3':
                # Read by ID
                student_id = input("Enter student ID to search: ").strip()
                student = crud.read_student_by_id(student_id)
                
                if student:
                    crud.display_students([student])
                else:
                    print(f"\n✗ Student with ID '{student_id}' not found.")
            
            elif choice == '4':
                # Read by Course
                course_code = input("Enter course code to filter: ").strip()
                students = crud.read_students_by_course(course_code)
                
                if students:
                    crud.display_students(students)
                else:
                    print(f"\nNo students found in course '{course_code.upper()}'.")
            
            elif choice == '5':
                # Update
                student_id = input("Enter student ID to update: ").strip()
                student = crud.read_student_by_id(student_id)
                
                if not student:
                    print(f"\n✗ Student with ID '{student_id}' not found.")
                    continue
                
                print(f"\nCurrent information:")
                crud.display_students([student])
                
                print("Leave blank to keep current value:")
                new_name = input("New name: ").strip()
                new_course = input("New course code: ").strip()
                
                updated_student = crud.update_student(student_id, new_name or None, new_course or None)
                print(f"\n✓ Student updated successfully!")
                crud.display_students([updated_student])
            
            elif choice == '6':
                # Delete
                student_id = input("Enter student ID to delete: ").strip()
                
                student = crud.read_student_by_id(student_id)
                if not student:
                    print(f"\n✗ Student with ID '{student_id}' not found.")
                    continue
                
                confirm = input(f"Are you sure you want to delete {student['name']} ({student_id})? (yes/no): ").strip().lower()
                
                if confirm == 'yes':
                    if crud.delete_student(student_id):
                        print(f"\n✓ Student '{student_id}' deleted successfully!")
                    else:
                        print(f"\n✗ Failed to delete student.")
                else:
                    print("Deletion cancelled.")
            
            elif choice == '7':
                print("\n✓ Exiting the application. Goodbye!")
                break
            
            else:
                print("\n✗ Invalid option. Please select a number between 1 and 7.")
        
        except ValueError as e:
            print(f"\n✗ Error: {e}")
        except Exception as e:
            print(f"\n✗ Unexpected error: {e}")


if __name__ == "__main__":
    main()
