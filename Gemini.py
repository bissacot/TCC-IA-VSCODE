class StudentManager:
    def __init__(self):
        # Stores student data: {student_id: {"name": str, "course_code": str}}
        self.students = {}
        # Tracks the next sequential number for each course: {"GES": 1, "GEC": 1}
        self.course_counters = {}

    def _generate_id(self, course_code: str) -> str:
        """Generates a unique ID like GES1, GES2 based on course code."""
        code = course_code.upper()
        # Initialize counter if course code is seen for the first time
        if code not in self.course_counters:
            self.course_counters[code] = 1
        
        student_id = f"{code}{self.course_counters[code]}"
        self.course_counters[code] += 1
        return student_id

    def create_student(self, name: str, course_code: str):
        """Registers a new student."""
        student_id = self._generate_id(course_code)
        self.students[student_id] = {
            "name": name,
            "course_code": course_code.upper()
        }
        print(f"Student created successfully! ID: {student_id}")

    def list_students(self):
        """Displays all registered students."""
        if not self.students:
            print("No students registered yet.")
            return

        print("\n--- Student List ---")
        for sid, info in self.students.items():
            print(f"ID: {sid} | Name: {info['name']} | Course: {info['course_code']}")
        print("--------------------\n")

    def update_student(self, student_id: str, new_name: str = None):
        """Updates an existing student's name."""
        student_id = student_id.upper()
        if student_id in self.students:
            if new_name:
                self.students[student_id]["name"] = new_name
            print(f"Student {student_id} updated successfully.")
        else:
            print(f"Error: Student ID {student_id} not found.")

    def delete_student(self, student_id: str):
        """Removes a student record."""
        student_id = student_id.upper()
        if student_id in self.students:
            del self.students[student_id]
            print(f"Student {student_id} deleted successfully.")
        else:
            print(f"Error: Student ID {student_id} not found.")

# --- Example Usage ---
def main():
    manager = StudentManager()

    # Create
    manager.create_student("Alice Smith", "GES")
    manager.create_student("Bob Jones", "GEC")
    manager.create_student("Charlie Brown", "GES")

    # List
    manager.list_students()

    # Update
    manager.update_student("GES1", new_name="Alice Johnson")

    # Delete
    manager.delete_student("GEC1")

    # Final List
    manager.list_students()

if __name__ == "__main__":
    main()
