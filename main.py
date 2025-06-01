from prettytable import PrettyTable
import connsql, backend
import os, hashlib, json as j, sys
from mysql.connector import ProgrammingError
from datetime import datetime
from getpass4 import getpass
from termcolor import colored

# Verifica o SO e define o comando de limpar a tela
if os.name == 'nt': CL: str = "cls"
else: CL: str = "clear"

d = datetime.now()
dia: str = d.strftime("%d")
mes: str = connsql.numeropraMes(int(d.strftime("%m")))
ano: str = d.strftime("%Y")[2:4]

TAB = f"{mes}{ano}"

def adicionarGastos(con, cursor, conf: dict, usuario: str, dia: str):
    """
    Adicionar os gastos do dia simulado
    """
    colunasStr: str = ""

    colunasValores: list = receberColunas(cols=conf[usuario]['colunas']) #pega os VALUES
    colunasValores[0] = f"'{colunasValores[0]}'" # só coloca o '' na etiqueta pra não dar erro
    subtotal: float = sum(colunasValores[1:]) #remove a coluna 'Etiqueta'

    colunasValoresStr: str = ", ".join(list(map(str, colunasValores))) #transforma tudo em string

    colunasStr: str = ", ".join(conf[usuario]['colunas']) #pega o nome das colunas pra colocar no INTO

    query: str = f"INSERT INTO {TAB} ({colunasStr}) VALUES ({dia}, {colunasValoresStr}, {subtotal})"

    cursor.execute(query)
    connsql.mostrarTabela(cursor, "*", TAB)
    con.commit()

def verificarDespesasFixas(cursor, con, conf: dict, usuario: str):
    """
    Verifica as despesas fixas que devem ser cobradas e executa uma query SQL única para cobrá-las se o dia já passou
    """
    if not 'despesasFixas' in conf[usuario]['config']: return None #se não existir nenhuma, retornar None

    despesasFixas: dict[str, list] = conf[usuario]['config']['despesasFixas']
    colunasStr: str = ", ".join(conf[usuario]['colunas'])
    praInserir: list = []

    try: cursor.execute(connsql.criarTabela(mes, ano, colunas=conf[usuario]['colunas']))
    except ProgrammingError: pass

    cobradasQuery: str = f'SELECT Etiqueta FROM {TAB} WHERE '

    #NOTE: "etiqueta": [dia, valor]
    for etiqueta, _ in despesasFixas.items():
        cobradasQuery += f'Etiqueta="FIXA: {etiqueta}" OR '
    cobradasQuery: str = cobradasQuery.rstrip(" OR ")

    cobradasResultado: list[tuple] = connsql.executar(cursor, cobradasQuery)
    cobradas: list = []

    if bool(cobradasResultado): # se tiver algum resultado
        for item in cobradasResultado:
            cobradas.append(item[0]) #adicionar etiqueta no cobradas

    for etiqueta, info in despesasFixas.items():
        etiquetaF = f"FIXA: {etiqueta}"

        if int(dia) >= info[0] and etiquetaF not in cobradas: #se chegou o dia e ela não foi cobrada ainda nem ta na tabela
            praInserir.append(f"FIXA: {etiqueta}")

    if len(praInserir) > 0: 
        #tudo isso pra executar uma "MEGAQUERY" e reduzir carga do MySQL
        zerosContados: int = colunasStr.count(",") - 2 #excluindo os 3 campos NOT NULL (Dia, Etiqueta, SUBTOTAL)
        valoresZerados = ''.join(map(str, ["0, " for _ in range(zerosContados)])).rstrip(", ")
        query: str = f"""INSERT INTO {TAB} ({colunasStr}) VALUES """

        for etiquetaF in praInserir:
            etiqueta: str = etiquetaF.lstrip("FIXA: ")
            #                       Dia                 FIXA:           0, 0...             Valor (SUBTOTAL)
            query += f'({despesasFixas[etiqueta][0]}, "{etiquetaF}", {valoresZerados}, {despesasFixas[etiqueta][1]}), '
        query = query.rstrip(", ") #remover a ', ' no fim da query final

        cursor.execute(query)
        con.commit()

        print(f'✅ Despesas fixas ({', '.join(praInserir)}) debitadas com sucesso!\n\n')

def configurarDespesasFixas(conf: dict, usuario: str):
    """
    Abre um menu para que o usuário adicione/edite/remova despesas que serão adicionadas automaticamente no dia X do mês com etiqueta Y e valor Z
    """

    #NOTE: "nome": [dia, valor]
    despesasFixas: dict = conf[usuario]['config']['despesasFixas'] if 'despesasFixas' in conf[usuario]['config'] else {}

    if not 'despesasFixas' in conf[usuario]['config']: #checa se a chave NÃO existe
        opc = input(colored("\nSem despesas fixas configuradas!", "black", "on_light_blue")+"\nDeseja adicionar uma? (s/n) ")
        if opc == "s":
            etiqueta: str = input("\n✏️ Etiqueta: ")
            dia = int(input("📅 Dia: ")) # TODO: adicionar check de quantos dias o mês tem, pra não extrapolar (ex: dia 31 de fevereiro)
            valor = float(input("💳️ Valor: R$"))
            despesasFixas[etiqueta] = [dia, valor]
            
            conf[usuario]['config']['despesasFixas'] = despesasFixas
            with open('garracio.json', 'w') as f: j.dump(conf, f, indent=4)

            print(colored("\n🔄 Reinicie o programa para aplicar as alterações!", "black", "on_green"))
            sys.exit()

        else: print(colored("Abortar missão!", "red"))
    
    #imprimir tudo em uma tabelinha
    pt = PrettyTable(["id", "Etiqueta", "Dia", "Valor"])
    c: int = 1
    idEtiqueta: dict = {}
    for etiqueta, info in despesasFixas.items():
        pt.add_row([c, etiqueta, info[0], info[1]])
        idEtiqueta[c] = etiqueta
        c += 1

    print(pt)
    opc = int(input("\n⚙️ Escolha uma opção:\n \
                \n1-➕ Adicionar despesa fixa \
                \n2-✏️ Editar despesa fixa \
                \n3-➖ Remover despesa fixa\n\n=>"))
    
    if opc == 1:
        etiqueta = input("\n✏️ Etiqueta: ")
        dia = int(input("📅 Dia: "))
        valor = float(input("💳️ Valor: R$"))
        
        despesasFixas[etiqueta] = [dia, valor]
    elif opc == 2:
        id = int(input("\n🆔 Digite o id para editar: "))
        _ = int(input("\n⚙️ Editar o que?\n \
                        \n1-✏️ Etiqueta \
                        \n2-📅 Dia \
                        \n3-💳️ Valor\n\n=>"))
        if _ == 1:
            novaEtiqueta = input("\n✏️ Nova etiqueta: ")
            despesasFixas[novaEtiqueta] = despesasFixas.pop(idEtiqueta[id]) #apaga a etiqueta antiga e atribui a nova aos valores
        if _ == 2:
            novoDia = int(input("📅 Novo dia: "))
            despesasFixas[idEtiqueta[id]] = [novoDia, despesasFixas[idEtiqueta[id]][1]]
        if _ == 3: 
            novoValor = float(input("💳️ Novo valor: R$"))
            despesasFixas[idEtiqueta[id]] = [despesasFixas[idEtiqueta[id]][0], novoValor]
    elif opc == 3:
        id = int(input("\n🆔 Digite o id para deletar: "))
        despesasFixas.pop(idEtiqueta[id])

    conf[usuario]['config']['despesasFixas'] = despesasFixas
    with open('garracio.json', 'w') as f: j.dump(conf, f, indent=4)

def configurarRendaFixa(conf: dict, usuario: str):
    """
    Configura a renda fixa (salários, mesadas, etc.) e automaticamente adiciona ao resumo mensal (desativando-o)
    """
    rendaFixa: float = float(input("\n💳️ Defina uma "+colored("renda fixa", "black", "on_green")+" (Exemplo: salário) R$"))
    conf[usuario]['config']['rendaFixa'] = rendaFixa

    with open('garracio.json', 'w') as f: j.dump(conf, f, indent=4)
    return

def configurarSenhaMestra(conf: dict):
    """
    Configurar a senha-mestra global a ser utilizada
    """
    senhaMestra = getpass("\n🔑 Qual será a nova senha mestra? ").encode()
    with open('garracio.json', 'w') as f:
        conf['senhaMestra'] = hashlib.sha256(senhaMestra).hexdigest()
        j.dump(conf, f, indent=4)
    return

def configurarRMminmax(conf, usuario):
    """
    Configura intervalo de dias (mínimo e máximo) para fazer o resumo mensal
    """

    minDia, maxDia = input("\n⚙️ Digite o intervalo de tempo em dias para fazer o resumo mensal.\
                        \nFormato: <min-max> (incluindo os dois): ").split("-")
    
    conf[usuario]['config']['rmMinMax'] = [int(minDia), int(maxDia)]

    with open("garracio.json", "w") as f: j.dump(conf, f, indent=4)
    return

def resumoFeito(con, cursor, conf, usuario, dia, mes, ano, semCheck=False):
    """
    Verifica se o resumo mensal foi feito
    semCheck=False: Se a função vai fazer os 'checks' do intervalo de dias e se o resumo mensal foi feito
    """
    TAB: str = f"{mes}{ano}"
    saidas: float = 0
    rendaFixa: float = conf[usuario]['config']['rendaFixa']

    if TAB + "R" in connsql.mostrarTabelas(cursor): return True

    if semCheck:
        taNoIntervalo = True
        resumoMensalFeito = False
    else:
        taNoIntervalo: bool = (int(dia) >= conf[usuario]['config']['rmMinMax'][0] and
                               int(dia) <= conf[usuario]['config']['rmMinMax'][1])

        resumoMensalFeito: bool = conf[usuario]['config']['resumoMensalFeito']
     

    if taNoIntervalo and not resumoMensalFeito and rendaFixa > 0: #caso o usuário receba salário e tenha configurado nas opções
        try: cursor.execute(connsql.criarTabela(mes, ano, res=True))
        except ProgrammingError: pass

        subtotais = connsql.executar(cursor, f"SELECT SUBTOTAL FROM {TAB}")
        for subtotal in subtotais[0]: saidas += subtotal
        total: float = rendaFixa - saidas

        cursor.execute(f"INSERT INTO {TAB}R VALUES ({rendaFixa}, {saidas}, {total})")
    
        print(colored("\n✅ Resumo mensal feito automaticamente!", "black", "on_green"))
        connsql.mostrarTabela(cursor, "*", f"{TAB}R", ordenar=False)
        print(colored("\nOBS: Para desativar a automação, defina sua renda fixa nas opções para 0.\n\n", "black", "on_light_blue"))

        con.commit()
        return True

    elif taNoIntervalo and not resumoMensalFeito and rendaFixa == 0:
        
        opc = input("\n📝 Deseja resumir seu mês? (s/n) ")
        if opc.lower() == 's':
            entra = float(input("💵 Quanto você ganhou esse mês? R$"))
        
            #caso a tabela já exista
            try: cursor.execute(connsql.criarTabela(mes, ano, res=True))
            except ProgrammingError: pass

            subtotal: list[tuple] = connsql.executar(cursor, f"SELECT SUBTOTAL FROM {TAB}")
            
            #descobri o que o 'for' faz, mas deixei assim pq achei engraçado kkkkkkk
            #a variável 'subtotal' = [(subtotal,)] então os dois 'for' são pra entrar na lista e tupla respectivamente
            #e pegar o valor subtotal de cada dia lá de dentro kkkkkkkkkkkkkkkkkk. então da pra remover o primeiro 'for' e
            #só colocar subtotal[0], que no caso é o primeiro "nível": []

            for i in subtotal: #só Deus sabe o que esse for faz!
                for k in i:
                    saidas += k
            total: float = entra - saidas #calcula o total com base nas entradas e saídas

            cursor.execute(f"INSERT INTO {TAB}R VALUES ({entra}, {saidas}, {total})")
            connsql.mostrarTabela(cursor, "*", f"{TAB}R", ordenar=False)
            con.commit()
    
            return True # Retorna True se o resumo foi feito
        else: return False #se o usuário não quiser


    return True # Retorna True se não era dia de fazer o resumo ou semCheck era True e o usuário não quis


def login(conf: dict, usuario="arg"):
    """
    Lógica de login e criação de usuários para o Garracio
    usuario="arg": Se for "arg", perguntar o usuário, se não, apenas pedir a senha
    """
    global dia

    os.system(CL)
    
    if usuario == "arg":
        usuarios: str = ", ".join(conf['usuarios']) if conf['usuarios'] != [] else colored("Não há usuários cadastrados!", "white", "on_red")
        print(f"🧑 Usuários disponíveis: {usuarios}")
        usuario = input("🧑 Login: ").capitalize()

    if usuario in conf['usuarios']:
        connsql.config['database'] = usuario #verifica se o usuário existe
        while True: #checa a senha
            if conf['senhaMestra']:
                _ = getpass("🔒️ Senha-Mestra: ")
                if _ == "": print(colored("Abortar‼️", "red")); sys.exit()
                if hashlib.sha256(_.encode()).hexdigest() == conf['senhaMestra']:
                    print("🔓️ Login realizado!\n")
                    break
                else:
                    print("❌ Senha incorreta.")
                    continue
            else: configurarSenhaMestra(conf)

    else: #criar usuário
        _ = input("🤔 Usuário não encontrado!\n➕ Deseja criá-lo (s/n)? ")

        if _.lower() == 's':
            conf['usuarios'].append(usuario)
            conf[usuario] = {
                "config": {
                    "resumoMensalFeito": True,
                    "rmMinMax": [
                        28,
                        31
                    ],
                    "rendaFixa": 0.0
                },
                "colunas": [
                    "Dia",
                    "Etiqueta",
                    "Educação",
                    "Saúde",
                    "Lazer",
                    "Outros",
                    "SUBTOTAL"
                ]
            }
            with open('garracio.json', 'w') as f: j.dump(conf, f, indent=4) #registra o usuário no arquivo json

            #cria o banco de dados do usuário
            connsql.config['database'] = "ADM"
            con, cursor = connsql.conectar()
            cursor.execute(f"CREATE DATABASE {usuario}")

            configurarColunas(conf, usuario)

            con, cursor = None, None 
            opcoes(conf, usuario, con, cursor, dia, mes, ano) #mandar o usuário pro menu de opções
            
            os.system(CL)
            print(colored("🔄 Reinicie o programa para aplicar as alterações!", "black", "on_green"))
        elif _.lower() == 'n':
            print(colored("Abortar missão!", "red"))
        sys.exit()

    try: con, cursor = connsql.conectar()
    except:
        print(colored("Erro ao conectar ao banco de dados!", "black", "on_red"))
        print(colored("O MySQL está sendo executado?", "black", "on_light_blue"))
        sys.exit()

    return usuario, con, cursor

def inicializar(usuario_arg="arg"): # Renomeado para evitar conflito
    """
    Inicializa as configurações, usuário e verifica se é dia de RM
    """
    #carrega o arquivo de configuração na variável 'conf'
    with open("garracio.json", "r") as f: conf = j.load(f)
    usuario, con, cursor = login(conf, usuario=usuario_arg)
    
    verificarDespesasFixas(cursor, con, conf, usuario)

    # Atualiza o estado do resumo mensal
    conf[usuario]['config']['resumoMensalFeito'] = resumoFeito(con, cursor, conf, usuario, dia, mes, ano)
    if dia == "01" and conf[usuario]['config']['resumoMensalFeito']:
        conf[usuario]['config']['resumoMensalFeito'] = False

    with open("garracio.json", "w") as f: j.dump(conf, f, indent=4)

    return conf, usuario, con, cursor, dia, mes, ano # Retorna todos os valores


def receberColunas(cols=connsql.COLUNAS_PADRAO):
    """
    Pega as saídas do usuário com base nas colunas configuradas
    """
    valores: list = []
    
    for i in cols:
        if i == "Etiqueta":
            _ = input(f"\n✏️ Etiqueta: ")
            valores.append(_)
        elif i not in ["Dia", "SUBTOTAL"]:
            _ = float(input(f"💳️ {i} R$"))
            valores.append(_)
    return valores

def configurarColunas(conf, usuario):
    """
    Configura as colunas para um usuário específico
    """
    cols = ["Dia", "Etiqueta"]

    colsPadrao: list = ["Dia"] + connsql.COLUNAS_PADRAO + ["SUBTOTAL"]
    colsPadraoPT = PrettyTable() # o PT é PrettyTable tá pelo amor de Deus CUMPANHERO
    colsPadraoPT.field_names = colsPadrao

    colsAtuaisPT = PrettyTable()
    colsAtuaisPT.field_names = conf[usuario]['colunas']

    print(colored("\nColunas padrão: \n", "white", "on_grey"), colsPadraoPT)
    print(colored("Colunas atuais: \n", "black", "on_white"), colsAtuaisPT)

    cols_str = input("\nDigite as colunas " + colored("em ordem, separadas por '; '", "red") +
                     "\n(não é necessário incluir 'Dia', 'Etiqueta' e 'SUBTOTAL'): ")

    cols_usuario: list = cols_str.split("; ")

    cols.extend(col for col in cols_usuario if col not in cols)
    
    for i in range(len(cols)): #deixar tudo com letra maiúscula
        cols[i] = cols[i].capitalize()
    cols.append("SUBTOTAL") #'SUBTOTAL' obrigatório

    conf[usuario]['colunas'] = cols


    with open("garracio.json", "w") as f: j.dump(conf, f, indent=4)
    return conf
 
def opcoes(conf: dict, usuario: str, con, cursor, dia: str, mes: str, ano: str):
    _ = int(input(f"\n⚙️ Selecione uma configuração:\n\
                \n1-📅 Alterar data\
                \n2-📆 Realizar o resumo mensal\
                \n3-💴 Configurar renda fixa\
                \n4-💳️ Configurar despesas fixas\
                \n5-⌛️ Configurar intervalo de dias para o resumo mensal\
                \n6-🧑 Mudar usuário\
                \n7-🔑 Alterar Senha-Mestra\
                \n8-📑 Configurar colunas para {usuario}\
                \n\n=>"))

    if _ == 1:
        print("📅 Formato: dd/mm/aaaa")
        diaNovo = input("📅 Dia: ")
        mesNovo = connsql.numeropraMes(int(input("📅 Mês: ")))
        anoNovo = input("📅 Ano: ")[2:4]
        # Retorna os novos valores para quem chamou (main)
        return conf, usuario, con, cursor, diaNovo, mesNovo, anoNovo, True # O último True indica que a data foi alterada
    elif _ == 2:
        if not (con or cursor): print(colored("🔄 Reinicie para acessar essa configuração!", "black", "on_green")); sys.exit()
        resumoFeito(con, cursor, conf, usuario, dia, mes, ano, semCheck=True)
    elif _ == 3:
        configurarRendaFixa(conf, usuario)
    elif _ == 4:
        configurarDespesasFixas(conf, usuario)
    elif _ == 5:
        configurarRMminmax(conf, usuario)
    elif _ == 6:
        return None, None, None, None, None, None, None, False, True # Último True para indicar que o usuário mudou
    elif _ == 7:
        configurarSenhaMestra(conf)
    elif _ == 8:
        with open("garracio.json", "r") as f: conf = j.load(f)
        configurarColunas(conf, usuario)
        connsql.reconstruirTabela(cursor, conf, usuario, mes, ano)
    
    return conf, usuario, con, cursor, dia, mes, ano, False, False # Retorna os valores originais e False para indicar que a data não foi alterada


def main(conf, usuario, con, cursor, dia, mes, ano, tipoExecucao=0): # Todos os valores são passados como argumento
    """
    Função principal
    tipoExecucao:
        - Perguntar (0)
        - CLI (1)
        - Web (2)
    """
    
    connsql.sincronizar(cursor)

    if tipoExecucao == 0:
        tipoExecucao = int(input(f"{usuario}, selecione a interface:\
                                \n1-⌨️Executar diretamente (pela linha de comando)\
                                \n2-🖥️Executar interface web (EXPERIMENTAL)\
                                \n\n=>"))
    
    if tipoExecucao == 1:
        TAB = f"{mes}{ano}"
        print(colored(f"👋 Olá {usuario}", "yellow") + ", bem vindo ao " + colored("Garracio", "black", "on_green")+"!")
        print(colored(f"📅 Data atual: {datetime.now().strftime('%d/%m/%Y')}", "white", "on_black"))
        print(colored(f"📅 Data simulada: {dia} de {mes}, {'20'+ano}\n", "black", "on_blue"))
        opc = int(input("\n\nO que deseja fazer hoje❓️\n \
                    \n1-➕ Adicionar gastos de hoje\
                    \n2-➖ Remover os gastos de um dia\
                    \n3-🔎 Consultar um dia\
                    \n4-📊 Ver tabela do mês\
                    \n5-🧾 Ver outra tabela\
                    \n\n0-⚙️ Opções\
                    \n9-⬅️ Sair\
                    \n\n=>"))

        #tenta criar a tabela do mês caso não exista
        try: cursor.execute(connsql.criarTabela(mes, ano, colunas=conf[usuario]['colunas']))
        except ProgrammingError: pass

        match(opc):
            case 1: # Adicionar gastos de hoje
                adicionarGastos(con, cursor, conf, usuario, dia)
            case 2: # Remover gastos de um dia
                connsql.mostrarTabela(cursor, "*", TAB)
                id_remover = input("✏️ Digite o ID da linha que você quer remover: ")
                cursor.execute(f"DELETE FROM {TAB} WHERE ID={id_remover}")
                con.commit()
            case 3: # Consultar dia
                connsql.executareMostrar(cursor, f"SELECT Dia FROM {TAB} ORDER BY Dia ASC")
                d_consultar = int(input("\n📅 Qual dia você deseja ver? "))
                connsql.executareMostrar(cursor, f"SELECT * FROM {TAB} WHERE Dia={d_consultar} ORDER BY Dia ASC")
            case 4: # Ver mês
                connsql.mostrarTabela(cursor, "*", TAB)
            case 5: # Ver outra tabela
                tabelasEnum = connsql.mostrarTabelas(cursor, enumerarId=True)
                id = int(input("✏️ Digite o 'id' da tabela: "))
                tabela = tabelasEnum[id]

                if not "R" in tabela: connsql.mostrarTabela(cursor, "*", tabela)
                else: connsql.mostrarTabela(cursor, "*", tabela, ordenar=False)
            case 9: # Sair
                print(f"\n👋 Tchau, {usuario}.\n"+colored("Não se esqueça de mim!!", "black", "on_red"))
                sys.exit()
            case 0: # Opções
                # A função opcoes agora retorna os valores, e main os atualiza
                os.system(CL)
                conf, usuario, con, cursor, dia, mes, ano, dataAlterada, usuarioMudou = opcoes(conf, usuario, con, cursor, dia, mes, ano)
                if dataAlterada or usuarioMudou:
                    if usuarioMudou:
                        conf, usuario, con, cursor, dia, mes, ano = inicializar(usuario_arg="arg") 
                    main(conf, usuario, con, cursor, dia, mes, ano, tipoExecucao=tipoExecucao)

    elif tipoExecucao == 2:
            backend.iniciar(host=connsql.config['host'], usuario=usuario)


if __name__ == "__main__":
    # Inicialização inicial para obter todos os dados
    if any(arg in sys.argv for arg in ["--help", "-h", "help", "?"]): #mensagem de ajuda 
        print(sys.argv)
        print("Uso: [ARGS] usuario\n\nARGS:\
        \n\t-cli: Executar interface em linha de comando \
        \n\n\t-web: Executar interface na web (EXPERIMENTAL!) \
        \n\nusuario: Nome do usuário (inicial maiúscula) para login\n")
        sys.exit() 

    # Determina o usuário a partir dos argumentos ou usa a inicialização padrão
    if sys.argv[-1] not in connsql.EXCECOES:
        conf, usuario, con, cursor, dia, mes, ano = inicializar(usuario_arg=sys.argv[-1].capitalize())
    else:
        conf, usuario, con, cursor, dia, mes, ano = inicializar()

    # Passa as variáveis para a função main
    if "-web" in sys.argv:
        main(conf, usuario, con, cursor, dia, mes, ano, tipoExecucao=2)
    elif "-cli" in sys.argv:
        main(conf, usuario, con, cursor, dia, mes, ano, tipoExecucao=1)
    else:
        main(conf, usuario, con, cursor, dia, mes, ano)
