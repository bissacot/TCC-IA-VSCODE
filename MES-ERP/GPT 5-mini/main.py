from production import OrdemFabricacao, OrdemProducao, LinhaProducao


def prompt(msg: str) -> str:
    return input(msg).strip()


def criar_of(store_ofs: dict):
    code = prompt("Insira o código da OF (YYTCC) ou ENTER para criar passo a passo: ")
    try:
        if code:
            of = OrdemFabricacao(code)
        else:
            ano = int(prompt("Ano (00-99): ") or 0)
            tipo = int(prompt("Tipo da linha (0 normal, 1 premium): "))
            cliente = int(prompt("Código do cliente (0-99): "))
            of = OrdemFabricacao.create(ano, tipo, cliente)
        store_ofs[of.code] = of
        print(f"OF criada: {of.code}")
    except Exception as e:
        print("Erro ao criar OF:", e)


def criar_op(store_ofs: dict, store_ops: list):
    if not store_ofs:
        print("Nenhuma OF encontrada. Crie uma OF primeiro.")
        return
    print("OFs disponíveis:")
    for c in store_ofs:
        print(" -", c)
    of_code = prompt("Informe a OF (YYTCC) para vincular: ")
    if of_code not in store_ofs:
        print("OF não encontrada.")
        return
    try:
        fase = int(prompt("Fase (0-2): "))
        sub = int(prompt("Subfase (0-2): "))
        modo = prompt("Modo (A/B/C): ").upper()
        base = int(prompt("Recurso base (00-26): "))
        op = OrdemProducao(store_ofs[of_code], fase, sub, modo, base)
        store_ops.append(op)
        print("OP gerada:", op.to_code())
    except Exception as e:
        print("Erro ao criar OP:", e)


def validar_op():
    code = prompt("Informe o código OP a validar (ex: 2512312B05): ")
    try:
        op = OrdemProducao.from_code(code)
        print("OP válida.")
        print("Recursos:", ", ".join(op.recursos_str()))
        print("Código (normalizado):", op.to_code())
    except Exception as e:
        print("OP inválida:", e)


def simular_op():
    code = prompt("Informe o código OP para simular: ")
    try:
        op = OrdemProducao.from_code(code)
        print("Simulação da OP:", op.to_code())
        for step in op.simulate():
            print("  -", step)
    except Exception as e:
        print("Erro na simulação:", e)


def listar_estrutura():
    tipo_s = prompt("Tipo de linha para listar (0 normal, 1 premium) [padrão 0]: ")
    try:
        tipo = int(tipo_s) if tipo_s else 0
        lp = LinhaProducao(tipo)
        s = lp.list_structure()
        print(f"Tipo: {s['tipo']}")
        print(f"Total de recursos: {s['total_recursos']}")
        print("Recursos:", ", ".join(s['recursos']))
    except Exception as e:
        print("Erro ao listar estrutura:", e)


def menu():
    print("\n=== Sistema de OP / OF - Menu ===")
    print("1 - Criar Ordem de Fabricação (OF)")
    print("2 - Criar Ordem de Produção (OP)")
    print("3 - Validar OP")
    print("4 - Simular OP")
    print("5 - Listar estrutura da linha de produção")
    print("0 - Sair")


def main():
    store_ofs = {}
    store_ops = []
    while True:
        menu()
        choice = prompt("Escolha uma opção: ")
        if choice == "1":
            criar_of(store_ofs)
        elif choice == "2":
            criar_op(store_ofs, store_ops)
        elif choice == "3":
            validar_op()
        elif choice == "4":
            simular_op()
        elif choice == "5":
            listar_estrutura()
        elif choice == "0":
            print("Saindo.")
            break
        else:
            print("Opção inválida.")


if __name__ == "__main__":
    main()
