"""Simple CLI for student CRUD operations using StudentDatabase."""
from students_db import StudentDatabase


def print_students(students):
    if not students:
        print("No students registered.")
        return
    print(f"{'ID':<10} {'Course':<8} {'Name'}")
    print('-' * 40)
    for s in students:
        print(f"{s['id']:<10} {s['course']:<8} {s['name']}")


def main():
    db = StudentDatabase('students.json')

    while True:
        print('\nStudent CRUD')
        print('1) Register student')
        print('2) List students')
        print('3) Update student')
        print('4) Delete student')
        print('5) Exit')
        choice = input('Select an option: ').strip()

        if choice == '1':
            name = input('Student name: ').strip()
            course = input('Course code (e.g., GES): ').strip().upper()
            try:
                student = db.add_student(name, course)
                print(f"Registered: {student['id']} - {student['name']} ({student['course']})")
            except Exception as e:
                print('Error:', e)

        elif choice == '2':
            students = db.list_students()
            print_students(students)

        elif choice == '3':
            sid = input('Student ID to update: ').strip()
            student = db.get(sid)
            if not student:
                print('Student not found.')
                continue
            print(f"Current: {student['id']} - {student['name']} ({student['course']})")
            new_name = input(f"New name [{student['name']}]: ").strip()
            new_course = input(f"New course [{student['course']}]: ").strip()
            try:
                updated = db.update(sid, name=new_name or None, course=new_course or None)
                print('Updated:', updated)
            except Exception as e:
                print('Error:', e)

        elif choice == '4':
            sid = input('Student ID to delete: ').strip()
            confirm = input('Type yes to confirm deletion: ').strip().lower()
            if confirm == 'yes':
                if db.delete(sid):
                    print('Deleted.')
                else:
                    print('Student not found.')
            else:
                print('Deletion cancelled.')

        elif choice == '5':
            print('Goodbye.')
            break

        else:
            print('Invalid option. Try again.')


if __name__ == '__main__':
    main()
