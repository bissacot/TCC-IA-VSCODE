from students import StudentDB


def demo():
    db = StudentDB(storage_path=':memory:')
    s1 = db.create_student('Alice', 'GES')
    s2 = db.create_student('Bob', 'GES')
    s3 = db.create_student('Carol', 'GEC')
    print('After creation:')
    for s in db.list_students():
        print(f"{s.id}: {s.name} - {s.course}")

    # Update Bob's name and course (this assigns a new ID)
    updated = db.update_student(s2.id, name='Robert', course='GEC')
    print('\nAfter update:')
    for s in db.list_students():
        print(f"{s.id}: {s.name} - {s.course}")

    # Delete Alice
    db.delete_student(s1.id)
    print('\nAfter delete:')
    for s in db.list_students():
        print(f"{s.id}: {s.name} - {s.course}")


if __name__ == '__main__':
    demo()
