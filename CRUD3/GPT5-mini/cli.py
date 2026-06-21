#!/usr/bin/env python3
from students import StudentDB


def print_menu() -> None:
    print("Student CRUD")
    print("1) Register student")
    print("2) List students")
    print("3) Update student")
    print("4) Delete student")
    print("5) Quit")


def main() -> None:
    db = StudentDB()
    while True:
        print_menu()
        choice = input("Choose an option: ").strip()
        if choice == '1':
            name = input("Student name: ").strip()
            if not name:
                print("Name cannot be empty.")
                continue
            course = input("Course code (e.g. GES): ").strip()
            if not course:
                print("Course code cannot be empty.")
                continue
            s = db.create_student(name, course)
            print(f"Registered: {s.id} - {s.name} ({s.course})")
        elif choice == '2':
            students = db.list_students()
            if not students:
                print("No students registered.")
            else:
                for s in students:
                    print(f"{s.id}: {s.name} - {s.course}")
        elif choice == '3':
            sid = input("Student ID to update: ").strip()
            s = db.get_student(sid)
            if not s:
                print("Student not found.")
                continue
            print(f"Current: {s.id}: {s.name} - {s.course}")
            new_name = input("New name (leave blank to keep): ").strip()
            new_course = input("New course code (leave blank to keep): ").strip()
            updated = db.update_student(sid, name=new_name or None, course=new_course or None)
            if updated:
                print(f"Updated: {updated.id}: {updated.name} - {updated.course}")
        elif choice == '4':
            sid = input("Student ID to delete: ").strip()
            ok = db.delete_student(sid)
            print("Deleted." if ok else "Not found.")
        elif choice == '5':
            print("Goodbye.")
            break
        else:
            print("Invalid choice.")
        print()


if __name__ == '__main__':
    main()
