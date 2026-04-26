import json
import os

STUDENTS_FILE = 'students.json'

def load_students():
	if not os.path.exists(STUDENTS_FILE):
		return []
	with open(STUDENTS_FILE, 'r', encoding='utf-8') as f:
		return json.load(f)

def save_students(students):
	with open(STUDENTS_FILE, 'w', encoding='utf-8') as f:
		json.dump(students, f, indent=2)

def generate_student_id(students, course_code):
	count = sum(1 for s in students if s['course_code'] == course_code)
	return f"{course_code}{count+1}"

def register_student(name, course_code):
	students = load_students()
	student_id = generate_student_id(students, course_code)
	student = {'name': name, 'course_code': course_code, 'student_id': student_id}
	students.append(student)
	save_students(students)
	print(f"Registered: {student}")

def list_students():
	students = load_students()
	if not students:
		print("No students registered.")
	for s in students:
		print(f"ID: {s['student_id']}, Name: {s['name']}, Course: {s['course_code']}")

def update_student(student_id, new_name=None, new_course_code=None):
	students = load_students()
	for s in students:
		if s['student_id'] == student_id:
			if new_name:
				s['name'] = new_name
			if new_course_code and new_course_code != s['course_code']:
				s['course_code'] = new_course_code
				s['student_id'] = generate_student_id(students, new_course_code)
			save_students(students)
			print(f"Updated: {s}")
			return
	print("Student not found.")

def delete_student(student_id):
	students = load_students()
	new_students = [s for s in students if s['student_id'] != student_id]
	if len(new_students) == len(students):
		print("Student not found.")
	else:
		save_students(new_students)
		print(f"Deleted student with ID: {student_id}")

def menu():
	while True:
		print("\n1. Register student\n2. List students\n3. Update student\n4. Delete student\n5. Exit")
		choice = input("Choose an option: ")
		if choice == '1':
			name = input("Enter name: ")
			course_code = input("Enter course code: ")
			register_student(name, course_code)
		elif choice == '2':
			list_students()
		elif choice == '3':
			student_id = input("Enter student ID to update: ")
			new_name = input("Enter new name (leave blank to keep): ")
			new_course_code = input("Enter new course code (leave blank to keep): ")
			update_student(student_id, new_name or None, new_course_code or None)
		elif choice == '4':
			student_id = input("Enter student ID to delete: ")
			delete_student(student_id)
		elif choice == '5':
			break
		else:
			print("Invalid option.")

if __name__ == "__main__":
	menu()
