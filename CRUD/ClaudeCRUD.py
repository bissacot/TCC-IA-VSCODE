import json
from pathlib import Path
from typing import Optional, List, Dict

class Student:
    """Representa um estudante com ID, nome e código do curso."""
    
    def __init__(self, name: str, course_code: str, student_id: str):
        self.name = name
        self.course_code = course_code
        self.student_id = student_id
    
    def to_dict(self) -> Dict:
        """Converte estudante para dicionário."""
        return {
            "student_id": self.student_id,
            "name": self.name,
            "course_code": self.course_code
        }
    
    def __repr__(self) -> str:
        return f"ID: {self.student_id} | Nome: {self.name} | Curso: {self.course_code}"


class StudentManager:
    """Gerencia operações CRUD de estudantes."""
    
    def __init__(self, data_file: str = "students.json"):
        self.data_file = Path(data_file)
        self.students: Dict[str, Student] = {}
        self.course_counters: Dict[str, int] = {}
        self.load_students()
    
    def load_students(self) -> None:
        """Carrega estudantes do arquivo JSON."""
        if self.data_file.exists():
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for student_data in data.get("students", []):
                        student = Student(
                            student_data["name"],
                            student_data["course_code"],
                            student_data["student_id"]
                        )
                        self.students[student.student_id] = student
                        # Reconstruir contadores
                        course = student.course_code
                        count = int(student.student_id.replace(course, ""))
                        self.course_counters[course] = max(
                            self.course_counters.get(course, 0), count
                        )
            except Exception as e:
                print(f"Erro ao carregar dados: {e}")
    
    def save_students(self) -> None:
        """Salva estudantes no arquivo JSON."""
        try:
            data = {
                "students": [student.to_dict() for student in self.students.values()]
            }
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Erro ao salvar dados: {e}")
    
    def _generate_student_id(self, course_code: str) -> str:
        """Gera um ID único para o estudante baseado no código do curso."""
        if course_code not in self.course_counters:
            self.course_counters[course_code] = 0
        
        self.course_counters[course_code] += 1
        return f"{course_code}{self.course_counters[course_code]}"
    
    def create_student(self, name: str, course_code: str) -> Student:
        """Cria e registra um novo estudante. Retorna o objeto Student criado."""
        if not name or not course_code:
            raise ValueError("Nome e código do curso são obrigatórios.")
        
        course_code = course_code.upper()
        student_id = self._generate_student_id(course_code)
        student = Student(name, course_code, student_id)
        self.students[student_id] = student
        self.save_students()
        return student
    
    def read_all_students(self) -> List[Student]:
        """Retorna lista de todos os estudantes."""
        return sorted(self.students.values(), key=lambda s: s.student_id)
    
    def read_student(self, student_id: str) -> Optional[Student]:
        """Busca um estudante pelo ID."""
        return self.students.get(student_id)
    
    def read_by_course(self, course_code: str) -> List[Student]:
        """Retorna todos os estudantes de um curso específico."""
        course_code = course_code.upper()
        return [s for s in self.students.values() if s.course_code == course_code]
    
    def update_student(self, student_id: str, name: Optional[str] = None, 
                      course_code: Optional[str] = None) -> Optional[Student]:
        """Atualiza os dados de um estudante. Nota: student_id não pode ser alterado."""
        student = self.students.get(student_id)
        if not student:
            raise ValueError(f"Estudante com ID {student_id} não encontrado.")
        
        if name:
            student.name = name
        if course_code:
            student.course_code = course_code.upper()
        
        self.save_students()
        return student
    
    def delete_student(self, student_id: str) -> bool:
        """Deleta um estudante pelo ID. Retorna True se deletado com sucesso."""
        if student_id in self.students:
            del self.students[student_id]
            self.save_students()
            return True
        return False
    
    def get_statistics(self) -> Dict:
        """Retorna estatísticas sobre os estudantes."""
        stats = {}
        for course_code in self.course_counters:
            count = sum(1 for s in self.students.values() if s.course_code == course_code)
            stats[course_code] = count
        return stats


def print_menu():
    """Exibe o menu principal."""
    print("\n" + "="*50)
    print("       SISTEMA DE GESTÃO DE ESTUDANTES")
    print("="*50)
    print("1. Registrar novo estudante")
    print("2. Listar todos os estudantes")
    print("3. Listar estudantes por curso")
    print("4. Atualizar dados de um estudante")
    print("5. Deletar um estudante")
    print("6. Ver estatísticas")
    print("0. Sair")
    print("="*50)


def main():
    """Função principal com interface interativa."""
    manager = StudentManager()
    
    while True:
        print_menu()
        choice = input("Escolha uma opção: ").strip()
        
        if choice == "1":
            # Registrar novo estudante
            name = input("Nome do estudante: ").strip()
            course_code = input("Código do curso (ex: GES, GEC): ").strip()
            try:
                student = manager.create_student(name, course_code)
                print(f"✓ Estudante registrado com sucesso: {student}")
            except ValueError as e:
                print(f"✗ Erro: {e}")
        
        elif choice == "2":
            # Listar todos os estudantes
            students = manager.read_all_students()
            if students:
                print("\n" + "-"*50)
                print("TODOS OS ESTUDANTES:")
                print("-"*50)
                for student in students:
                    print(student)
                print("-"*50)
            else:
                print("Nenhum estudante registrado.")
        
        elif choice == "3":
            # Listar por curso
            course_code = input("Código do curso: ").strip()
            students = manager.read_by_course(course_code)
            if students:
                print("\n" + "-"*50)
                print(f"ESTUDANTES DO CURSO {course_code.upper()}:")
                print("-"*50)
                for student in students:
                    print(student)
                print("-"*50)
            else:
                print(f"Nenhum estudante encontrado para o curso {course_code.upper()}.")
        
        elif choice == "4":
            # Atualizar estudante
            student_id = input("ID do estudante a atualizar: ").strip()
            student = manager.read_student(student_id)
            if student:
                print(f"Estudante encontrado: {student}")
                name = input("Novo nome (deixe em branco para não alterar): ").strip()
                course_code = input("Novo código de curso (deixe em branco para não alterar): ").strip()
                try:
                    updated = manager.update_student(student_id, name or None, course_code or None)
                    print(f"✓ Estudante atualizado: {updated}")
                except ValueError as e:
                    print(f"✗ Erro: {e}")
            else:
                print(f"✗ Estudante com ID {student_id} não encontrado.")
        
        elif choice == "5":
            # Deletar estudante
            student_id = input("ID do estudante a deletar: ").strip()
            if manager.delete_student(student_id):
                print(f"✓ Estudante {student_id} deletado com sucesso.")
            else:
                print(f"✗ Estudante com ID {student_id} não encontrado.")
        
        elif choice == "6":
            # Estatísticas
            stats = manager.get_statistics()
            if stats:
                print("\n" + "-"*50)
                print("ESTATÍSTICAS POR CURSO:")
                print("-"*50)
                for course, count in sorted(stats.items()):
                    print(f"{course}: {count} estudante(s)")
                print(f"Total: {sum(stats.values())} estudante(s)")
                print("-"*50)
            else:
                print("Nenhum estudante registrado.")
        
        elif choice == "0":
            print("Encerrando o programa. Até logo!")
            break
        
        else:
            print("✗ Opção inválida. Tente novamente.")


if __name__ == "__main__":
    main()
