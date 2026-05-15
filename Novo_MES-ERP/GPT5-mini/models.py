"""
models.py

Classes do sistema de codificação compacta (ERP/MES) para linha de produção.

 - OrdemFabricacao: valida e representa OF (YYTCC)
 - OrdemProducao: interpreta/valida OP e gera lista de recursos
 - LinhaProducao: representa a estrutura de recursos (00..26)
"""

class ValidationError(Exception):
    pass


class OrdemFabricacao:
    def __init__(self, code: str):
        if not isinstance(code, str):
            raise ValidationError("OF deve ser uma string.")
        if len(code) != 5 or not code.isdigit():
            raise ValidationError("Formato inválido para OF. Deve ser YYTCC (5 dígitos).")
        yy = int(code[0:2])
        t = code[2]
        if t not in ('0', '1'):
            raise ValidationError("Tipo da linha (T) inválido. Deve ser 0 ou 1.")
        cc = int(code[3:5])
        self.code = code
        self.yy = yy
        self.tipo = int(t)
        self.cliente = cc

    def __str__(self):
        return f"OF {self.code} (ano={self.yy:02d}, tipo={self.tipo}, cliente={self.cliente:02d})"


class OrdemProducao:
    def __init__(self, code: str = None, of: 'OrdemFabricacao' = None, fase: int = None, subfase: int = None, modo: str = None, base: int = None):
        if code:
            self.code = code
            self._parse_code(code)
        else:
            if of is None:
                raise ValidationError("Ordem de Fabricação (OF) é necessária para criar uma OP.")
            self.of = of if isinstance(of, OrdemFabricacao) else OrdemFabricacao(of)
            try:
                self.fase = int(fase)
                self.subfase = int(subfase)
                self.modo = modo.upper()
                self.base = int(base)
            except Exception:
                raise ValidationError("Campos inválidos ao criar OP a partir de partes.")
            self._validate_fields()
            self.code = self._generate_code()
        self.resources = self._generate_resources()

    def _parse_code(self, code: str):
        if len(code) != 10:
            raise ValidationError("OP deve ter 10 caracteres: YYTCC + fase + subfase + modo + base(2). Ex: 2512312B05")
        of_code = code[:5]
        self.of = OrdemFabricacao(of_code)
        try:
            self.fase = int(code[5])
            self.subfase = int(code[6])
        except ValueError:
            raise ValidationError("Fase e subfase devem ser dígitos (0-2).")
        self.modo = code[7].upper()
        base_str = code[8:10]
        if not base_str.isdigit():
            raise ValidationError("Base de recurso deve ser dois dígitos (00-26).")
        self.base = int(base_str)
        self._validate_fields()

    def _validate_fields(self):
        if not (0 <= self.fase <= 2):
            raise ValidationError("Fase inválida, deve ser 0-2.")
        if not (0 <= self.subfase <= 2):
            raise ValidationError("Subfase inválida, deve ser 0-2.")
        if self.modo not in ('A', 'B', 'C'):
            raise ValidationError("Modo inválido, deve ser A, B ou C.")
        if not (0 <= self.base <= 26):
            raise ValidationError("Recurso base inválido, deve estar entre 00 e 26.")
        count = {'A': 1, 'B': 2, 'C': 3}[self.modo]
        if self.base + count - 1 > 26:
            raise ValidationError(f"Recursos excedem 26 com base {self.base:02d} e modo {self.modo}.")

    def _generate_code(self) -> str:
        return f"{self.of.code}{self.fase}{self.subfase}{self.modo}{self.base:02d}"

    def _generate_resources(self):
        counts = {'A': 1, 'B': 2, 'C': 3}
        count = counts[self.modo]
        res = list(range(self.base, self.base + count))
        return [f"{r:02d}" for r in res]

    def __str__(self):
        return f"OP {self.code} -> OF {self.of.code}, fase {self.fase}, subfase {self.subfase}, modo {self.modo}, base {self.base:02d}"


class LinhaProducao:
    def __init__(self, max_recurso: int = 26):
        self.max_recurso = max_recurso
        self._resources = [f"{i:02d}" for i in range(0, max_recurso + 1)]

    def listar_estrutura(self):
        return self._resources.copy()

    def simular(self, op: OrdemProducao):
        return op.resources.copy()
