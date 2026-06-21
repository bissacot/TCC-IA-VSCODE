from student_manager import StudentManager


def prompt(prompt_text: str) -> str:
    return input(prompt_text).strip()


def print_student(s):
    print(f"ID: {s.id} | Name: {s.name} | Course: {s.course}")


def main():
    mgr = StudentManager()
    print("Student CRUD CLI. Commands: create, list, update, delete, exit")
    while True:
        cmd = prompt('\n> ').lower()
        if cmd in ('exit', 'quit'):
            break
        if cmd == 'create':
            name = prompt('Name: ')
            course = prompt('Course code: ').upper()
            student = mgr.create_student(name, course)
            print('Created student:')
            print_student(student)
        elif cmd == 'list':
            students = mgr.list_students()
            if not students:
                print('No students registered.')
            for s in students:
                print_student(s)
        elif cmd == 'update':
            sid = prompt('Student ID to update: ').upper()
            student = mgr.get_student(sid)
            if not student:
                print('Student not found')
                continue
            name = prompt(f'New name (leave empty to keep "{student.name}"): ')
            course = prompt(f'New course (leave empty to keep "{student.course}"): ').upper()
            name = name or None
            course = course or None
            updated = mgr.update_student(sid, name=name, course=course)
            print('Updated:')
            print_student(updated)
        elif cmd == 'delete':
            sid = prompt('Student ID to delete: ').upper()
            ok = mgr.delete_student(sid)
            print('Deleted' if ok else 'Not found')
        else:
            print('Unknown command')


if __name__ == '__main__':
    main()
