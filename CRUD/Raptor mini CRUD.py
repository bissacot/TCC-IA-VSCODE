import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List, Optional

DATA_FILE = Path("students.json")

@dataclass
class Student:
    student_id: str
    name: str
    course_code: str


def load_students() -> List[Student]:
    if not DATA_FILE.exists():
        return []

    try:
        raw = DATA_FILE.read_text(encoding="utf-8")
        data = json.loads(raw)
        return [Student(**item) for item in data]
    except Exception as exc:
        print(f"Erro ao carregar estudantes: {exc}")
        return []


def save_students(students: List[Student]) -> None:
    try:
        DATA_FILE.write_text(json.dumps([asdict(student) for student in students], indent=2, ensure_ascii=False), encoding="utf-8")
    except Exception as exc:
        print(f"Erro ao salvar estudantes: {exc}")


def next_student_id(course_code: str, students: List[Student]) -> str:
    course = course_code.strip().upper()
    highest = 0
    for student in students:
        if student.course_code == course and student.student_id.startswith(course):
            suffix = student.student_id[len(course):]
            if suffix.isdigit():
                highest = max(highest, int(suffix))
    return f"{course}{highest + 1}"


def register_student(name: str, course_code: str) -> Student:
    students = load_students()
    student_id = next_student_id(course_code, students)
    student = Student(student_id=student_id, name=name.strip(), course_code=course_code.strip().upper())
    students.append(student)
    save_students(students)
    return student


def list_students(course_code: Optional[str] = None) -> List[Student]:
    students = load_students()
    if course_code:
        course = course_code.strip().upper()
        return [student for student in students if student.course_code == course]
    return students


def find_student(student_id: str) -> Optional[Student]:
    students = load_students()
    for student in students:
        if student.student_id == student_id.strip().upper():
            return student
    return None


def update_student(student_id: str, new_name: Optional[str] = None, new_course_code: Optional[str] = None) -> Optional[Student]:
    students = load_students()
    for index, student in enumerate(students):
        if student.student_id == student_id.strip().upper():
            if new_name:
                student.name = new_name.strip()
            if new_course_code:
                student.course_code = new_course_code.strip().upper()
            students[index] = student
            save_students(students)
            return student
    return None


def delete_student(student_id: str) -> bool:
    students = load_students()
    cleaned = [student for student in students if student.student_id != student_id.strip().upper()]
    if len(cleaned) == len(students):
        return False
    save_students(cleaned)
    return True


def statistics() -> Dict[str, int]:
    students = load_students()
    stats: Dict[str, int] = {}
    for student in students:
        stats[student.course_code] = stats.get(student.course_code, 0) + 1
    return stats


def print_menu() -> None:
    print("\n" + "=" * 42)
    print("CRUD DE ESTUDANTES")
    print("=" * 42)
    print("1. Registrar estudante")
    print("2. Listar todos")
    print("3. Listar por curso")
    print("4. Atualizar estudante")
    print("5. Deletar estudante")
    print("6. Ver estatísticas")
    print("0. Sair")
    print("=" * 42)


def main() -> None:
    while True:
        print_menu()
        choice = input("Escolha uma opção: ").strip()

        if choice == "1":
            name = input("Nome: ").strip()
            course = input("Código do curso (ex: GES, GEC): ").strip()
            if not name or not course:
                print("Nome e código do curso são obrigatórios.")
                continue
            student = register_student(name, course)
            print(f"Estudante registrado: {student}")

        elif choice == "2":
            students = list_students()
            if not students:
                print("Nenhum estudante cadastrado.")
            else:
                for student in students:
                    print(student)

        elif choice == "3":
            course = input("Código do curso: ").strip()
            students = list_students(course)
            if not students:
                print(f"Nenhum estudante encontrado para o curso {course.upper()}.")
            else:
                for student in students:
                    print(student)

        elif choice == "4":
            student_id = input("ID do estudante: ").strip()
            if not find_student(student_id):
                print(f"Estudante {student_id} não encontrado.")
                continue
            new_name = input("Novo nome (ou deixe em branco): ").strip()
            new_course = input("Novo código do curso (ou deixe em branco): ").strip()
            updated = update_student(student_id, new_name or None, new_course or None)
            if updated:
                print(f"Atualizado: {updated}")
            else:
                print("Falha ao atualizar estudante.")

        elif choice == "5":
            student_id = input("ID do estudante a deletar: ").strip()
            if delete_student(student_id):
                print(f"Estudante {student_id} deletado.")
            else:
                print(f"Estudante {student_id} não encontrado.")

        elif choice == "6":
            stats = statistics()
            if not stats:
                print("Nenhum estudante cadastrado.")
            else:
                for course, total in sorted(stats.items()):
                    print(f"{course}: {total}")

        elif choice == "0":
            print("Saindo...")
            break

        else:
            print("Opção inválida. Tente novamente.")


if __name__ == "__main__":
    main()
