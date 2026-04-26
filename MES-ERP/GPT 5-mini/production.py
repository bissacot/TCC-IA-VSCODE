"""Módulo com as classes do sistema de codificação compacta.

Classes:
- OrdemFabricacao: representa a OF (YYTCC)
- OrdemProducao: interpreta e valida o código OP, gera lista de recursos
- LinhaProducao: descreve a estrutura da linha (recursos 00..26)

Regras implementadas conforme especificado.
"""

MAX_RESOURCE = 26


class OrdemFabricacao:
    """Representa uma Ordem de Fabricação no formato YYTCC.

    YY: ano (00–99)
    T: tipo da linha (0 normal, 1 premium)
    CC: código do cliente (00–99)
    """

    def __init__(self, code: str):
        if not isinstance(code, str):
            raise ValueError("Código da OF deve ser string")
        if len(code) != 5 or not code.isdigit():
            raise ValueError("Formato da OF inválido. Deve ser 'YYTCC' com 5 dígitos")
        self.code = code
        self.ano = int(code[0:2])
        self.tipo = int(code[2])
        if self.tipo not in (0, 1):
            raise ValueError("Tipo da linha inválido (0 ou 1)")
        self.cliente = int(code[3:5])

    @classmethod
    def create(cls, ano: int, tipo: int, cliente: int):
        if not (0 <= ano <= 99):
            raise ValueError("Ano deve ser 0–99")
        if tipo not in (0, 1):
            raise ValueError("Tipo deve ser 0 ou 1")
        if not (0 <= cliente <= 99):
            raise ValueError("Código do cliente deve ser 0–99")
        code = f"{ano:02d}{tipo}{cliente:02d}"
        return cls(code)

    def __repr__(self):
        return f"OrdemFabricacao({self.code})"


class OrdemProducao:
    """Representa e valida uma Ordem de Produção (OP).

    Estrutura do código OP: YYTCC f s M BB
      - YYTCC : referência da OF (5 caracteres)
      - f     : fase (0..2)
      - s     : subfase (0..2)
      - M     : modo de recurso (A/B/C)
      - BB    : recurso base (00..26)
    """

    def __init__(self, of, fase: int, subfase: int, modo: str, base: int):
        from typing import Iterable

        if not isinstance(of, OrdemFabricacao):
            raise ValueError("Parâmetro 'of' deve ser uma OrdemFabricacao")
        self.of = of

        if fase not in (0, 1, 2):
            raise ValueError("Fase inválida (deve ser 0, 1 ou 2)")
        self.fase = int(fase)

        if subfase not in (0, 1, 2):
            raise ValueError("Subfase inválida (deve ser 0, 1 ou 2)")
        self.subfase = int(subfase)

        if not isinstance(modo, str) or modo.upper() not in ("A", "B", "C"):
            raise ValueError("Modo inválido (deve ser 'A', 'B' ou 'C')")
        self.modo = modo.upper()

        if not (isinstance(base, int) and 0 <= base <= MAX_RESOURCE):
            raise ValueError(f"Recurso base inválido (deve ser 00–{MAX_RESOURCE:02d})")
        self.base = int(base)

        # gera a lista de recursos e valida overflow
        self.recursos = self._gerar_recursos()

    @classmethod
    def from_code(cls, op_code: str):
        """Cria uma OrdemProducao a partir do código OP textual e valida-o."""
        if not isinstance(op_code, str):
            raise ValueError("OP deve ser uma string")
        if len(op_code) != 10:
            raise ValueError("Formato da OP inválido: tamanho esperado 10 caracteres")

        of_code = op_code[0:5]
        fase_c = op_code[5]
        sub_c = op_code[6]
        modo_c = op_code[7]
        base_s = op_code[8:10]

        # validações básicas
        from builtins import int as _int
        try:
            fase = _int(fase_c)
            subfase = _int(sub_c)
        except Exception:
            raise ValueError("Fase e subfase devem ser dígitos (0–2)")

        try:
            base = _int(base_s)
        except Exception:
            raise ValueError("Recurso base inválido (deve ser número) )")

        of = OrdemFabricacao(of_code)
        return cls(of, fase, subfase, modo_c, base)

    def _gerar_recursos(self):
        mapa = {"A": 1, "B": 2, "C": 3}
        qtd = mapa[self.modo]
        fim = self.base + (qtd - 1)
        if fim > MAX_RESOURCE:
            raise ValueError("Recursos extrapolam o limite máximo (26). Overflow detectado.")
        return [self.base + i for i in range(qtd)]

    def recursos_str(self):
        return [f"{r:02d}" for r in self.recursos]

    def to_code(self):
        return f"{self.of.code}{self.fase}{self.subfase}{self.modo}{self.base:02d}"

    def validate(self):
        # Já validado no construtor; mantemos método para interface
        return True

    def simulate(self):
        steps = []
        for r in self.recursos:
            steps.append(f"Usando recurso {r:02d}")
        return steps


class LinhaProducao:
    """Representa a estrutura da linha de produção (recursos globais 00..26)."""

    def __init__(self, tipo: int = 0):
        if tipo not in (0, 1):
            raise ValueError("Tipo da linha inválido (0 ou 1)")
        self.tipo = tipo
        self.recursos = [f"{i:02d}" for i in range(0, MAX_RESOURCE + 1)]

    def list_structure(self):
        return {
            "tipo": self.tipo,
            "total_recursos": len(self.recursos),
            "recursos": list(self.recursos),
        }


if __name__ == "__main__":
    print("Módulo de domínio. Importe as classes em um script (ex: main.py).")
