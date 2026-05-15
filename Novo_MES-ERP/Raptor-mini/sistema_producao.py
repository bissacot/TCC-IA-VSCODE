import re


class OrdemFabricacao:
    def __init__(self, ano: str, tipo_linha: str, codigo_cliente: str):
        self.ano = self._validate_ano(ano)
        self.tipo_linha = self._validate_tipo(tipo_linha)
        self.codigo_cliente = self._validate_cliente(codigo_cliente)

    @classmethod
    def from_codigo(cls, codigo: str):
        if not re.fullmatch(r"\d{5}", codigo):
            raise ValueError("Código da OF deve ter 5 dígitos no formato YYTCC.")
        ano = codigo[0:2]
        tipo = codigo[2]
        cliente = codigo[3:5]
        return cls(ano, tipo, cliente)

    @staticmethod
    def _validate_ano(ano: str) -> str:
        if not re.fullmatch(r"\d{2}", ano):
            raise ValueError("Ano deve ser dois dígitos entre 00 e 99.")
        return ano

    @staticmethod
    def _validate_tipo(tipo: str) -> str:
        if tipo not in {"0", "1"}:
            raise ValueError("Tipo da linha deve ser 0 (normal) ou 1 (premium).")
        return tipo

    @staticmethod
    def _validate_cliente(cliente: str) -> str:
        if not re.fullmatch(r"\d{2}", cliente):
            raise ValueError("Código do cliente deve ter dois dígitos.")
        return cliente

    @property
    def codigo(self) -> str:
        return f"{self.ano}{self.tipo_linha}{self.codigo_cliente}"

    def __str__(self):
        tipo = "normal" if self.tipo_linha == "0" else "premium"
        return f"OF {self.codigo} (ano {self.ano}, tipo {tipo}, cliente {self.codigo_cliente})"


class OrdemProducao:
    VALID_MODOS = {"A": 1, "B": 2, "C": 3}
    VALID_FASES = {"0", "1", "2"}
    VALID_SUBFASES = {"0", "1", "2"}
    VALID_RECURSOS = set(str(i).zfill(2) for i in range(27))

    def __init__(self, codigo_op: str = None, ordem_fabr: OrdemFabricacao = None,
                 fase: str = None, subfase: str = None, modo: str = None, recurso_base: str = None):
        if codigo_op is not None:
            self.codigo_op = codigo_op.strip().upper()
            self.ordem_fabr, self.fase, self.subfase, self.modo, self.recurso_base = self._parse_codigo(self.codigo_op)
        else:
            if None in (ordem_fabr, fase, subfase, modo, recurso_base):
                raise ValueError("É necessário fornecer todos os parâmetros para criar uma OP manualmente.")
            self.ordem_fabr = ordem_fabr
            self.fase = self._validate_fase(fase)
            self.subfase = self._validate_subfase(subfase)
            self.modo = self._validate_modo(modo)
            self.recurso_base = self._validate_recurso(recurso_base)
            self.codigo_op = f"{self.ordem_fabr.codigo}{self.fase}{self.subfase}{self.modo}{self.recurso_base}"
        self.recursos = self._gerar_recursos()
        self._validar_recursos()

    @classmethod
    def _parse_codigo(cls, codigo_op: str):
        if not re.fullmatch(r"\d{5}[0-2][0-2][ABC][0-2][0-9]", codigo_op):
            raise ValueError("Formato inválido da OP. Deve ser YYTCCfsMBB onde f/subfase 0-2, M em A/B/C e BB de 00 a 26.")
        codigo_of = codigo_op[:5]
        fase = codigo_op[5]
        subfase = codigo_op[6]
        modo = codigo_op[7]
        recurso_base = codigo_op[8:10]
        ordem_fabr = OrdemFabricacao.from_codigo(codigo_of)
        return ordem_fabr, fase, subfase, modo, recurso_base

    @staticmethod
    def _validate_fase(fase: str) -> str:
        if fase not in OrdemProducao.VALID_FASES:
            raise ValueError("Fase inválida. Deve ser 0, 1 ou 2.")
        return fase

    @staticmethod
    def _validate_subfase(subfase: str) -> str:
        if subfase not in OrdemProducao.VALID_SUBFASES:
            raise ValueError("Subfase inválida. Deve ser 0, 1 ou 2.")
        return subfase

    @staticmethod
    def _validate_modo(modo: str) -> str:
        if modo not in OrdemProducao.VALID_MODOS:
            raise ValueError("Modo inválido. Deve ser A, B ou C.")
        return modo

    @staticmethod
    def _validate_recurso(recurso: str) -> str:
        if recurso not in OrdemProducao.VALID_RECURSOS:
            raise ValueError("Recurso base inválido. Deve ser um valor entre 00 e 26.")
        return recurso

    def _gerar_recursos(self):
        quantidade = OrdemProducao.VALID_MODOS[self.modo]
        base = int(self.recurso_base)
        recursos = [base + i for i in range(quantidade)]
        return [str(x).zfill(2) for x in recursos]

    def _validar_recursos(self):
        for recurso in self.recursos:
            if recurso not in OrdemProducao.VALID_RECURSOS:
                raise ValueError(f"Recursos inválidos gerados: {self.recursos}. Overflow ou base inválida.")

    def validar(self) -> bool:
        try:
            self._validate_fase(self.fase)
            self._validate_subfase(self.subfase)
            self._validate_modo(self.modo)
            self._validate_recurso(self.recurso_base)
            self._validar_recursos()
            return True
        except ValueError:
            return False

    def listar_recursos(self) -> str:
        return ", ".join(self.recursos)

    def simular(self) -> str:
        return (f"Simulação da OP {self.codigo_op}:\n"
                f"  Ordem de Fabricação: {self.ordem_fabr.codigo}\n"
                f"  Fase: {self.fase}\n"
                f"  Subfase: {self.subfase}\n"
                f"  Modo de recurso: {self.modo} ({OrdemProducao.VALID_MODOS[self.modo]} recurso(s))\n"
                f"  Recursos usados: {self.listar_recursos()}")

    def __str__(self):
        return f"OP {self.codigo_op} -> recursos [{self.listar_recursos()}]"


class LinhaProducao:
    def __init__(self):
        self.ords_fabr = []
        self.ords_prod = []

    def criar_of(self, codigo: str) -> OrdemFabricacao:
        ordem = OrdemFabricacao.from_codigo(codigo)
        if any(of.codigo == ordem.codigo for of in self.ords_fabr):
            raise ValueError("OF já existe na linha de produção.")
        self.ords_fabr.append(ordem)
        return ordem

    def criar_op(self, codigo_op: str) -> OrdemProducao:
        op = OrdemProducao(codigo_op=codigo_op)
        if any(existing.codigo_op == op.codigo_op for existing in self.ords_prod):
            raise ValueError("OP já existe na linha de produção.")
        self.ords_prod.append(op)
        return op

    def listar_estrutura(self) -> str:
        linhas = ["Estrutura da linha de produção:"]
        linhas.append("- OFs (Ordens de Fabricação):")
        if not self.ords_fabr:
            linhas.append("  Nenhuma OF registrada.")
        else:
            for of in self.ords_fabr:
                linhas.append(f"  - {of}")
        linhas.append("- OPs (Ordens de Produção):")
        if not self.ords_prod:
            linhas.append("  Nenhuma OP registrada.")
        else:
            for op in self.ords_prod:
                linhas.append(f"  - {op}")
        linhas.append("- Fases válidas: 0, 1, 2")
        linhas.append("- Subfases válidas: 0, 1, 2")
        linhas.append("- Modos de recurso: A=1, B=2, C=3")
        linhas.append("- Recursos válidos: 00 a 26")
        return "\n".join(linhas)

    def obter_of(self, codigo: str):
        for of in self.ords_fabr:
            if of.codigo == codigo:
                return of
        return None


def ler_entrada(msg: str, padrao=None):
    while True:
        valor = input(msg).strip().upper()
        if padrao is None or re.fullmatch(padrao, valor):
            return valor
        print("Entrada inválida. Tente novamente.")


def criar_of_interativo(linha: LinhaProducao):
    print("\n=== Criar Ordem de Fabricação (OF) ===")
    codigo = ler_entrada("Digite o código OF (YYTCC): ", r"\d{5}")
    try:
        ordem = linha.criar_of(codigo)
        print(f"OF criada: {ordem}")
    except ValueError as e:
        print(f"Erro: {e}")


def criar_op_interativo(linha: LinhaProducao):
    print("\n=== Criar Ordem de Produção (OP) ===")
    codigo_op = ler_entrada("Digite o código OP (YYTCCfsMBB): ", r"\d{5}[0-2][0-2][ABC][0-2][0-9]")
    try:
        op = linha.criar_op(codigo_op)
        print(f"OP criada: {op}")
    except ValueError as e:
        print(f"Erro: {e}")


def validar_op_interativo():
    print("\n=== Validar Ordem de Produção (OP) ===")
    codigo_op = ler_entrada("Digite o código OP para validar: ", r"\d{5}[0-2][0-2][ABC][0-2][0-9]")
    try:
        op = OrdemProducao(codigo_op=codigo_op)
        print(f"OP válida: {op.codigo_op}")
        print(f"Recursos: {op.listar_recursos()}")
    except ValueError as e:
        print(f"OP inválida: {e}")


def simular_op_interativo():
    print("\n=== Simular Ordem de Produção (OP) ===")
    codigo_op = ler_entrada("Digite o código OP para simular: ", r"\d{5}[0-2][0-2][ABC][0-2][0-9]")
    try:
        op = OrdemProducao(codigo_op=codigo_op)
        print(op.simular())
    except ValueError as e:
        print(f"Não foi possível simular: {e}")


def menu():
    linha = LinhaProducao()
    opcoes = {
        "1": ("Criar OF", criar_of_interativo),
        "2": ("Criar OP", criar_op_interativo),
        "3": ("Validar OP", validar_op_interativo),
        "4": ("Simular OP", simular_op_interativo),
        "5": ("Listar estrutura", lambda l: print(l.listar_estrutura())),
        "0": ("Sair", None)
    }
    while True:
        print("\n=== Menu do Sistema de Produção ===")
        for chave, (desc, _) in opcoes.items():
            print(f"{chave} - {desc}")
        escolha = input("Escolha uma opção: ").strip()
        if escolha == "0":
            print("Encerrando o sistema. Até logo!")
            break
        acao = opcoes.get(escolha)
        if acao:
            _, func = acao
            func(linha)
        else:
            print("Opção inválida. Tente novamente.")


if __name__ == "__main__":
    menu()
