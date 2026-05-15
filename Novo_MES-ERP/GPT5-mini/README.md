# Sistema de Codificação Compacta (ERP/MES) — Simulação

Este pequeno projeto implementa um modelo de codificação compacto para ordens de produção.

Funcionalidades:
- Criar Ordem de Fabricação (OF)
- Gerar / Validar Ordem de Produção (OP)
- Converter OP em lista de recursos
- Listar estrutura de recursos (00..26)
- Simular execução de uma OP

Como executar:

1. Tenha Python 3 instalado.
2. Execute no terminal:

```bash
python main.py
```

Exemplo de OP válida: `2512312B05`

Formato resumido:
- OF: `YYTCC` (5 dígitos)
- OP: `YYTCC` + `fase` + `subfase` + `modo` + `base(2)` → total 10 caracteres

Regras principais:
- fases e subfases: 0..2
- recursos: 00..26
- modo: A=1 recurso, B=2, C=3 (acumulativo)
