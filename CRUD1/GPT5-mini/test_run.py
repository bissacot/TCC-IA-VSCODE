"""Quick non-interactive test: add, update, delete and print students."""
from students_db import StudentDatabase
import os


def main():
    test_db = 'students_test.json'
    if os.path.exists(test_db):
        os.remove(test_db)
    db = StudentDatabase(test_db)

    s1 = db.add_student('Alice Smith', 'GES')
    s2 = db.add_student('Bob Jones', 'GEC')
    s3 = db.add_student('Cleo', 'GES')

    print('Added:')
    for s in db.list_students():
        print(f"{s['id']} - {s['name']} ({s['course']})")

    db.update(s1['id'], name='Alice M. Smith')
    print('\nAfter update:')
    for s in db.list_students():
        print(f"{s['id']} - {s['name']} ({s['course']})")

    db.delete(s2['id'])
    print('\nAfter deletion:')
    for s in db.list_students():
        print(f"{s['id']} - {s['name']} ({s['course']})")


if __name__ == '__main__':
    main()
