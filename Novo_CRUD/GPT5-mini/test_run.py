from students_crud import register_student, list_students, update_student, delete_student, print_students

def main():
    print("Registering students...")
    s1 = register_student("Alice Smith", "GES")
    s2 = register_student("Bob Jones", "GEC")
    s3 = register_student("Carol White", "GES")
    print("\nStudents after registration:")
    print_students(list_students())

    print(f"\nUpdating {s1['id']} name...")
    update_student(s1['id'], "Alice Johnson")
    print_students(list_students())

    print(f"\nDeleting {s2['id']}...")
    delete_student(s2['id'])
    print_students(list_students())

if __name__ == "__main__":
    main()
