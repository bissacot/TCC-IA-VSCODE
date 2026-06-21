"""
Student CRUD System
Manages students with automatic ID generation based on course code
"""

students = []


def generate_student_id(course_code):
    """Generate a unique student ID based on course code."""
    # Count existing students with the same course code
    count = sum(1 for student in students if student['course_code'] == course_code)
    return f"{course_code}{count + 1}"


def create_student(name, course_code):
    """Create a new student and add to the system."""
    student_id = generate_student_id(course_code)
    
    student = {
        'student_id': student_id,
        'name': name,
        'course_code': course_code
    }
    
    students.append(student)
    print(f"✓ Student created successfully!")
    print(f"  Student ID: {student_id}, Name: {name}, Course: {course_code}\n")
    return student


def read_all_students():
    """List all registered students."""
    if not students:
        print("No students registered yet.\n")
        return
    
    print("\n" + "="*60)
    print("REGISTERED STUDENTS")
    print("="*60)
    for student in students:
        print(f"ID: {student['student_id']:<8} | Name: {student['name']:<20} | Course: {student['course_code']}")
    print("="*60 + "\n")


def read_student_by_id(student_id):
    """Read a specific student by ID."""
    for student in students:
        if student['student_id'] == student_id:
            print(f"\nStudent Found:")
            print(f"  Student ID: {student['student_id']}")
            print(f"  Name: {student['name']}")
            print(f"  Course: {student['course_code']}\n")
            return student
    
    print(f"Student with ID '{student_id}' not found.\n")
    return None


def update_student(student_id, new_name=None, new_course_code=None):
    """Update student information."""
    for student in students:
        if student['student_id'] == student_id:
            old_name = student['name']
            old_course = student['course_code']
            
            if new_name:
                student['name'] = new_name
            if new_course_code:
                student['course_code'] = new_course_code
            
            print(f"✓ Student updated successfully!")
            if new_name:
                print(f"  Name: {old_name} → {new_name}")
            if new_course_code:
                print(f"  Course: {old_course} → {new_course_code}")
            print()
            return student
    
    print(f"Student with ID '{student_id}' not found.\n")
    return None


def delete_student(student_id):
    """Delete a student from the system."""
    global students
    
    for i, student in enumerate(students):
        if student['student_id'] == student_id:
            deleted_student = students.pop(i)
            print(f"✓ Student deleted successfully!")
            print(f"  Removed: {deleted_student['name']} ({student_id})\n")
            return True
    
    print(f"Student with ID '{student_id}' not found.\n")
    return False


def display_menu():
    """Display the main menu."""
    print("\n" + "="*60)
    print("STUDENT CRUD SYSTEM")
    print("="*60)
    print("1. Register a new student (Create)")
    print("2. List all students (Read)")
    print("3. Search student by ID (Read)")
    print("4. Update student information (Update)")
    print("5. Delete a student (Delete)")
    print("6. Exit")
    print("="*60)


def main():
    """Main application loop."""
    while True:
        display_menu()
        choice = input("Enter your choice (1-6): ").strip()
        
        if choice == '1':
            print("\n--- Register New Student ---")
            name = input("Enter student name: ").strip()
            course_code = input("Enter course code (e.g., GES, GEC): ").strip().upper()
            
            if name and course_code:
                create_student(name, course_code)
            else:
                print("Invalid input. Please try again.\n")
        
        elif choice == '2':
            read_all_students()
        
        elif choice == '3':
            print("\n--- Search Student ---")
            student_id = input("Enter student ID to search: ").strip().upper()
            read_student_by_id(student_id)
        
        elif choice == '4':
            print("\n--- Update Student ---")
            student_id = input("Enter student ID to update: ").strip().upper()
            
            if read_student_by_id(student_id):
                print("Leave blank to skip a field.")
                new_name = input("Enter new name (or press Enter to skip): ").strip()
                new_course = input("Enter new course code (or press Enter to skip): ").strip().upper()
                
                update_student(
                    student_id,
                    new_name if new_name else None,
                    new_course if new_course else None
                )
        
        elif choice == '5':
            print("\n--- Delete Student ---")
            student_id = input("Enter student ID to delete: ").strip().upper()
            confirm = input(f"Are you sure you want to delete student {student_id}? (yes/no): ").strip().lower()
            
            if confirm == 'yes':
                delete_student(student_id)
            else:
                print("Deletion cancelled.\n")
        
        elif choice == '6':
            print("\nThank you for using Student CRUD System. Goodbye!\n")
            break
        
        else:
            print("Invalid choice. Please enter a number between 1 and 6.\n")


# Demo with sample data
def run_demo():
    """Run a demonstration of the CRUD system."""
    print("\n" + "="*60)
    print("STUDENT CRUD SYSTEM - DEMO")
    print("="*60 + "\n")
    
    # Create students
    print("--- Creating Students ---")
    create_student("Alice Johnson", "GES")
    create_student("Bob Smith", "GES")
    create_student("Carol Davis", "GEC")
    create_student("David Wilson", "GEC")
    create_student("Eve Brown", "GES")
    
    # Read all students
    print("--- Reading All Students ---")
    read_all_students()
    
    # Read specific student
    print("--- Reading Specific Student ---")
    read_student_by_id("GES2")
    
    # Update student
    print("--- Updating Student ---")
    update_student("GEC1", new_name="Carol Smith", new_course_code="GEB")
    
    # Read all students after update
    print("--- Reading All Students After Update ---")
    read_all_students()
    
    # Delete student
    print("--- Deleting Student ---")
    delete_student("GES3")
    
    # Final list
    print("--- Final Student List ---")
    read_all_students()


if __name__ == "__main__":
    # Uncomment the line below to run the demo
    # run_demo()
    
    # Run the interactive menu
    main()
