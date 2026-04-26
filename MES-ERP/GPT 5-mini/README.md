Sistema em Python para codificação compacta de ordens (OF / OP).

Arquivos principais:
- [production.py](production.py): classes de domínio (`OrdemFabricacao`, `OrdemProducao`, `LinhaProducao`).
- [main.py](main.py): interface interativa no terminal.

Como executar:

```bash
python main.py
```

Menu disponível:
- Criar OF
- Criar OP
- Validar OP
- Simular OP
- Listar estrutura da linha de produção

Regras implementadas:
- OF formato `YYTCC`
- OP formato `YYTCC f s M BB` (10 caracteres)
- Fases e subfases: 0..2
- Modos: A (1 recurso), B (2), C (3)
- Recursos globais: 00..26 (overflow proibido)

Exemplo de uso:
- Criar OF: `25123` (ano 25, tipo 1, cliente 23)
- Criar OP ligado a essa OF: fase 1, subfase 2, modo B, base 05 → OP: `2512312B05`

