"""Quick demo showcasing the registry usage."""
from students import StudentRegistry


def demo():
    reg = StudentRegistry()
    print("Registering students...")
    a = reg.create_student("Alice", "GES")
    b = reg.create_student("Bob", "GES")
    c = reg.create_student("Carol", "GEC")
    print("Current list:")
    for s in reg.list_students():
        print(s)
    print("Update Bob to GEC and new name 'Bobby'")
    reg.update_student(b.student_id, name="Bobby", course="GEC")
    for s in reg.list_students():
        print(s)
    print("Delete Alice")
    reg.delete_student(a.student_id)
    for s in reg.list_students():
        print(s)


if __name__ == "__main__":
    demo()
