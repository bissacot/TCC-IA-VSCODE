import re
from typing import List, Optional


class OrdemFabricacao:
    def __init__(self, ano: int, tipo: int, cliente: int):
        self.ano = ano
        self.tipo = tipo
        self.cliente = cliente
        self.validar()

    def validar(self) -> None:
        if not (0 <= self.ano <= 99):
            raise ValueError("Ano deve estar entre 00 e 99.")
        if self.tipo not in (0, 1):
            raise ValueError("Tipo deve ser 0 (normal) ou 1 (premium).")
        if not (0 <= self.cliente <= 99):
            raise ValueError("Código do cliente deve estar entre 00 e 99.")

    @property
    def codigo(self) -> str:
        return f"{self.ano:02d}{self.tipo}{self.cliente:02d}"

    def __str__(self) -> str:
        tipo_str = "normal" if self.tipo == 0 else "premium"
        return f"OF {self.codigo} (Ano: {self.ano:02d}, Tipo: {tipo_str}, Cliente: {self.cliente:02d})"


class OrdemProducao:
    OP_REGEX = re.compile(r"^(\d{2})([01])(\d{2})([0-2])([0-2])([ABC])(\d{2})$")
    MAX_RECURSO = 26

    def __init__(self, codigo: str):
        self.codigo = codigo.strip().upper()
        self.of_codigo: Optional[str] = None
        self.fase: Optional[int] = None
        self.subfase: Optional[int] = None
        self.modo: Optional[str] = None
        self.base: Optional[int] = None
        self.erros: List[str] = []
        self._parse()

    def _parse(self) -> None:
        match = self.OP_REGEX.match(self.codigo)
        if not match:
            self.erros.append("Formato da OP inválido. Deve ser YYTCCFSSMBB.")
            return

        ano, tipo, cliente, fase, subfase, modo, base = match.groups()
        self.of_codigo = f"{ano}{tipo}{cliente}"
        self.fase = int(fase)
        self.subfase = int(subfase)
        self.modo = modo
        self.base = int(base)
        self._validar_campos()

    def _validar_campos(self) -> None:
        if self.fase is None or not (0 <= self.fase <= 2):
            self.erros.append("Fase inválida: deve ser 0, 1 ou 2.")
        if self.subfase is None or not (0 <= self.subfase <= 2):
            self.erros.append("Subfase inválida: deve ser 0, 1 ou 2.")
        if self.modo not in ("A", "B", "C"):
            self.erros.append("Modo inválido: deve ser A, B ou C.")
        if self.base is None or not (0 <= self.base <= self.MAX_RECURSO):
            self.erros.append(f"Recurso base inválido: deve estar entre 00 e {self.MAX_RECURSO:02d}.")
        if self.base is not None and self.modo in ("A", "B", "C"):
            quantidade = self._quantidade_recursos()
            if self.base + quantidade - 1 > self.MAX_RECURSO:
                self.erros.append(
                    f"Overflow de recursos: base {self.base:02d} com modo {self.modo} exige {quantidade} recursos e ultrapassa {self.MAX_RECURSO:02d}."
                )

    def _quantidade_recursos(self) -> int:
        if self.modo == "A":
            return 1
        if self.modo == "B":
            return 2
        if self.modo == "C":
            return 3
        return 0

    def validar(self) -> bool:
        return len(self.erros) == 0

    def recursos(self) -> List[str]:
        if not self.validar() or self.base is None:
            return []
        quantidade = self._quantidade_recursos()
        return [f"{r:02d}" for r in range(self.base, self.base + quantidade)]

    def descricao(self) -> str:
        retorno = [f"OP: {self.codigo}"]
        if self.of_codigo:
            retorno.append(f"  OF: {self.of_codigo}")
        if self.fase is not None:
            retorno.append(f"  Fase: {self.fase}")
        if self.subfase is not None:
            retorno.append(f"  Subfase: {self.subfase}")
        if self.modo is not None:
            retorno.append(f"  Modo: {self.modo}")
        if self.base is not None:
            retorno.append(f"  Recurso base: {self.base:02d}")
        if self.validar():
            retorno.append(f"  Recursos: {', '.join(self.recursos())}")
        return "\n".join(retorno)

    def __str__(self) -> str:
        return self.codigo


class LinhaProducao:
    def __init__(self):
        self.ofs: List[OrdemFabricacao] = []
        self.ops: List[OrdemProducao] = []

    def criar_of(self, ano: int, tipo: int, cliente: int) -> OrdemFabricacao:
        of = OrdemFabricacao(ano, tipo, cliente)
        self.ofs.append(of)
        return of

    def gerar_op(self, of_codigo: str, fase: int, subfase: int, modo: str, base: int) -> OrdemProducao:
        codigo = f"{of_codigo}{fase}{subfase}{modo.upper()}{base:02d}"
        op = OrdemProducao(codigo)
        self.ops.append(op)
        return op

    def validar_op(self, codigo: str) -> OrdemProducao:
        op = OrdemProducao(codigo)
        return op

    def listar_estrutura(self) -> str:
        linhas = ["=== Estrutura da Linha de Produção ==="]
        if not self.ofs:
            linhas.append("Nenhuma Ordem de Fabricação cadastrada.")
        else:
            linhas.append("Ordens de Fabricação:")
            for of in self.ofs:
                linhas.append(f"- {of}")
        if not self.ops:
            linhas.append("Nenhuma Ordem de Produção cadastrada.")
        else:
            linhas.append("Ordens de Produção:")
            for op in self.ops:
                linhas.append(f"- {op.codigo} -> Recursos: {', '.join(op.recursos()) if op.validar() else 'inválida'}")
        return "\n".join(linhas)


def ler_int(mensagem: str, minimo: int, maximo: int) -> int:
    while True:
        valor = input(mensagem).strip()
        if not valor.isdigit():
            print("Entrada inválida. Digite um número inteiro.")
            continue
        numero = int(valor)
        if numero < minimo or numero > maximo:
            print(f"Valor deve estar entre {minimo} e {maximo}.")
            continue
        return numero


def ler_modo() -> str:
    while True:
        valor = input("Modo de Recurso (A/B/C): ").strip().upper()
        if valor in ("A", "B", "C"):
            return valor
        print("Modo inválido. Informe A, B ou C.")


def mostrar_menu() -> None:
    sistema = LinhaProducao()
    sons = {
        "1": "Criar Ordem de Fabricação",
        "2": "Criar Ordem de Produção",
        "3": "Validar OP",
        "4": "Simular OP",
        "5": "Listar estrutura",
        "0": "Sair",
    }
    while True:
        print("\n=== Menu de Produção ===")
        for chave, descricao in sons.items():
            print(f"{chave}. {descricao}")
        escolha = input("Escolha uma opção: ").strip()

        if escolha == "1":
            ano = ler_int("Ano da OF (00-99): ", 0, 99)
            tipo = ler_int("Tipo da linha (0=normal, 1=premium): ", 0, 1)
            cliente = ler_int("Código do cliente (00-99): ", 0, 99)
            try:
                of = sistema.criar_of(ano, tipo, cliente)
                print(f"OF criada: {of.codigo}")
            except ValueError as erro:
                print(f"Erro ao criar OF: {erro}")

        elif escolha == "2":
            if not sistema.ofs:
                print("Nenhuma OF cadastrada. Crie uma OF antes de gerar uma OP.")
                continue
            print("Ordens de Fabricação disponíveis:")
            for idx, of in enumerate(sistema.ofs, start=1):
                print(f"{idx}. {of.codigo} - Cliente {of.cliente:02d}")
            indice = ler_int("Selecione a OF por número: ", 1, len(sistema.ofs))
            of_selecionada = sistema.ofs[indice - 1]
            fase = ler_int("Fase (0-2): ", 0, 2)
            subfase = ler_int("Subfase (0-2): ", 0, 2)
            modo = ler_modo()
            base = ler_int("Recurso base (00-26): ", 0, OrdemProducao.MAX_RECURSO)
            op = sistema.gerar_op(of_selecionada.codigo, fase, subfase, modo, base)
            if op.validar():
                print(f"OP gerada: {op.codigo}")
                print(f"Recursos: {', '.join(op.recursos())}")
            else:
                print("OP inválida:")
                for erro in op.erros:
                    print(f"- {erro}")

        elif escolha == "3":
            codigo = input("Informe a OP para validar: ").strip().upper()
            op = sistema.validar_op(codigo)
            if op.validar():
                print("OP válida.")
                print(op.descricao())
            else:
                print("OP inválida:")
                for erro in op.erros:
                    print(f"- {erro}")

        elif escolha == "4":
            codigo = input("Informe a OP para simular: ").strip().upper()
            op = sistema.validar_op(codigo)
            if not op.validar():
                print("Op inválida. Não é possível simular:")
                for erro in op.erros:
                    print(f"- {erro}")
            else:
                print("Simulação da OP:")
                print(f"OP: {op.codigo}")
                print(f"OF: {op.of_codigo}")
                print(f"Fase: {op.fase} | Subfase: {op.subfase}")
                print(f"Modo: {op.modo}")
                print(f"Recursos usados: {', '.join(op.recursos())}")

        elif escolha == "5":
            print(sistema.listar_estrutura())

        elif escolha == "0":
            print("Encerrando o sistema.")
            break

        else:
            print("Opção inválida. Tente novamente.")


if __name__ == "__main__":
    mostrar_menu()
