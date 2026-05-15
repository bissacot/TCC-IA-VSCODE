from models import OrdemFabricacao, OrdemProducao, LinhaProducao, ValidationError


OF_STORE = []
OP_STORE = []
LINHA = LinhaProducao()


def criar_of():
    code = input("Informe o código da OF (YYTCC): ").strip()
    try:
        of = OrdemFabricacao(code)
        OF_STORE.append(of)
        print("OF criada:", of)
    except ValidationError as e:
        print("Erro:", e)


def criar_op():
    print("1) Informar OP completa")
    print("2) Gerar OP a partir de OF existente")
    choice = input("> ").strip()
    if choice == '1':
        code = input("Informe o código da OP completo (YYTCC+fase+subfase+modo+base): ").strip()
        try:
            op = OrdemProducao(code=code)
            OP_STORE.append(op)
            print("OP criada:", op)
            print("Recursos:", ", ".join(op.resources))
        except ValidationError as e:
            print("Erro:", e)
    elif choice == '2':
        if not OF_STORE:
            print("Nenhuma OF cadastrada. Crie uma OF primeiro.")
            return
        print("OFs cadastradas:")
        for idx, of in enumerate(OF_STORE):
            print(f"{idx+1}) {of.code} - {of}")
        idx_str = input("Selecione o número da OF: ").strip()
        try:
            idx = int(idx_str) - 1
            of = OF_STORE[idx]
        except Exception:
            print("Seleção inválida.")
            return
        fase = input("Fase (0-2): ").strip()
        subfase = input("Subfase (0-2): ").strip()
        modo = input("Modo (A/B/C): ").strip().upper()
        base = input("Recurso base (00-26): ").strip()
        try:
            op = OrdemProducao(of=of, fase=int(fase), subfase=int(subfase), modo=modo, base=int(base))
            OP_STORE.append(op)
            print("OP criada:", op)
            print("Recursos:", ", ".join(op.resources))
        except ValidationError as e:
            print("Erro:", e)
        except Exception as e:
            print("Entrada inválida:", e)
    else:
        print("Opção inválida.")


def validar_op():
    code = input("Informe o código da OP para validar: ").strip()
    try:
        op = OrdemProducao(code=code)
        print("OP válida:", op)
        print("Recursos:", ", ".join(op.resources))
    except ValidationError as e:
        print("OP inválida:", e)


def simular_op():
    code = input("Informe o código da OP para simular: ").strip()
    try:
        op = OrdemProducao(code=code)
        print(f"Simulação da OP {op.code} - recursos utilizados:")
        for r in op.resources:
            print(f" - Recurso {r}")
    except ValidationError as e:
        print("Erro na simulação:", e)


def listar_estrutura():
    print("Estrutura da linha de produção (recursos disponíveis):")
    print(", ".join(LINHA.listar_estrutura()))


def menu():
    while True:
        print("\n--- Menu ---")
        print("1) Criar OF")
        print("2) Criar OP")
        print("3) Validar OP")
        print("4) Simular OP")
        print("5) Listar estrutura")
        print("6) Sair")
        choice = input("Escolha: ").strip()
        if choice == '1':
            criar_of()
        elif choice == '2':
            criar_op()
        elif choice == '3':
            validar_op()
        elif choice == '4':
            simular_op()
        elif choice == '5':
            listar_estrutura()
        elif choice == '6':
            print("Saindo.")
            break
        else:
            print("Opção inválida.")


if __name__ == "__main__":
    print("Sistema de Codificação Compacta - ERP/MES (simulação)")
    menu()
