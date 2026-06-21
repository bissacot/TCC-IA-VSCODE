"""Simple CLI for interacting with StudentRegistry."""
import argparse
from students import StudentRegistry


def main():
    parser = argparse.ArgumentParser(description="Student registry CLI")
    sub = parser.add_subparsers(dest="cmd")

    add = sub.add_parser("add", help="Add a student")
    add.add_argument("name")
    add.add_argument("course")

    listp = sub.add_parser("list", help="List students")
    listp.add_argument("-c", "--course", help="Filter by course code", default=None)

    getp = sub.add_parser("get", help="Get a student by ID")
    getp.add_argument("id")

    upp = sub.add_parser("update", help="Update a student")
    upp.add_argument("id")
    upp.add_argument("-n", "--name", help="New name", default=None)
    upp.add_argument("-c", "--course", help="New course code", default=None)

    delp = sub.add_parser("delete", help="Delete a student")
    delp.add_argument("id")

    args = parser.parse_args()
    reg = StudentRegistry()

    if args.cmd == "add":
        s = reg.create_student(args.name, args.course)
        print(f"Created: {s.student_id} - {s.name} ({s.course_code})")
    elif args.cmd == "list":
        students = reg.list_students(args.course)
        if not students:
            print("No students found")
            return
        for s in students:
            print(f"{s.student_id}: {s.name} [{s.course_code}]")
    elif args.cmd == "get":
        s = reg.get_student(args.id)
        if not s:
            print("Not found")
            return
        print(f"{s.student_id}: {s.name} ({s.course_code})")
    elif args.cmd == "update":
        s = reg.update_student(args.id, name=args.name, course_code=args.course)
        if not s:
            print("Not found or nothing changed")
            return
        print(f"Updated: {s.student_id}: {s.name} ({s.course_code})")
    elif args.cmd == "delete":
        ok = reg.delete_student(args.id)
        print("Deleted" if ok else "Not found")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
