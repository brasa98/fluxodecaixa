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

dataLista: list = [dia, mes, ano]

TAB = f"{mes}{ano}"

def inputInteligente(*args, **kwargs):
    ret = kwargs.pop('ret')
    limpar = kwargs.pop('limpar', False)
    strVazia = kwargs.pop('strVazia', True)

    while True:
        try:
            entradaStr = input(*args, **kwargs)
            if not strVazia and entradaStr == '': raise ValueError
            return ret(entradaStr)
        except ValueError:
            if limpar: os.system(CL)
            if not ret == str: print(colored("\nDigite um número!\n", "red"))
            else: print(colored("\nDigite algo!\n", "red"))


def adicionarGastos(con, cursor, conf: dict, dia: str,  usuario: str):
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

def alterarEntrada(con, cursor, tabela, id=None, col=None):
    """
    Altera uma entrada em uma tabela
    id=None: A tabela é de resumo
    col=None: A tabela é normal
    """
    nomeColuna, query = "", ""
    if id:
        nomeColuna = inputInteligente("✏️ Digite o nome da coluna para alterar o valor: ", ret=str, strVazia=False)

        if nomeColuna.upper() in ("ID", "SUBTOTAL"):
            print(colored("Impossível alterar o id e o subtotal!", "red"))
            return

        if nomeColuna == "Dia": tipoVal = int
        elif nomeColuna == "Etiqueta": tipoVal = str
        else: tipoVal = float

        valorColuna = inputInteligente("✏️ Digite o novo valor: ", ret=tipoVal)

        if nomeColuna != "Etiqueta": query: str = f'UPDATE {tabela} SET {nomeColuna}={valorColuna} WHERE ID={id}'
        else: query: str = f'UPDATE {tabela} SET {nomeColuna}="{valorColuna}" WHERE ID={id}'

    elif col:
        nomeColuna = col
        if nomeColuna.upper() == "TOTAL":
            print(colored("Impossível alterar o TOTAL!", "red"))
            return
        
        valorColuna = inputInteligente("✏️ Digite o novo valor: ", ret=float)

        valores = connsql.executar(cursor, f"SELECT * FROM {tabela}")
        novoTotal = valores[0][0] - valores[0][1]

        cursor.execute(f'UPDATE {tabela} SET TOTAL={novoTotal}')

        query: str = f'UPDATE {tabela} SET {nomeColuna}={valorColuna}'

    cursor.execute(query)
    con.commit()

    os.system(CL)

    if id:
        print(colored(f"\n✅ Valor da coluna '{nomeColuna}' no id {id} alterada com sucesso!", "black", "on_green"))
    else:
        print(colored(f"\n✅ Valor da coluna '{nomeColuna}' alterada com sucesso!", "black", "on_green"))

    connsql.mostrarTabela(cursor, "*", tabela, ordenar=not col) #TODO: destacar valor da coluna recém-alterada
    print()

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

        print(f"✅ Despesas fixas ({', '.join(praInserir)}) debitadas com sucesso!\n\n")

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
            dia = inputInteligente("📅 Dia: ", ret=int) # TODO: adicionar check de quantos dias o mês tem, pra não extrapolar (ex: dia 31 de fevereiro)
            valor = inputInteligente("💳️ Valor: R$", ret=float)
            despesasFixas[etiqueta] = [dia, valor]
            
            conf[usuario]['config']['despesasFixas'] = despesasFixas
            with open('garracio.json', 'w') as f: j.dump(conf, f, indent=4)

            print(colored("\n🔄 Reinicie o programa para aplicar as alterações!", "black", "on_green"))
            sys.exit()

        else: print(colored("Abortar missão!", "red"))
    
    #imprimir tudo em uma tabelinha
    def imprimir():
        pt = PrettyTable(["id", "Etiqueta", "Dia", "Valor"])
        c: int = 1
        idEtiqueta: dict = {}
        for etiqueta, info in despesasFixas.items():
            pt.add_row([c, etiqueta, info[0], info[1]])
            idEtiqueta[c] = etiqueta
            c += 1
        return idEtiqueta, pt
    
    idEtiqueta, pt = imprimir()
    print(pt)

    opc = inputInteligente("\n⚙️ Escolha uma opção:\n \
                \n[1] ➕ Adicionar despesa fixa \
                \n[2] ✏️ Editar despesa fixa \
                \n[3] ➖ Remover despesa fixa\n\n=>", ret=int, limpar=True)
    
    if opc == 1:
        etiqueta = input("\n✏️ Etiqueta: ")
        dia = inputInteligente("📅 Dia: ", ret=int)
        valor = inputInteligente("💳️ Valor: R$", ret=float)
        
        despesasFixas[etiqueta] = [dia, valor]
    elif opc == 2:
        id = inputInteligente("\n🆔 Digite o id para editar: ", ret=int)
        _ = inputInteligente("\n⚙️ Editar o que?\n \
                        \n[1] ✏️ Etiqueta \
                        \n[2] 📅 Dia \
                        \n[3] 💳️ Valor\n\n=>", ret=int, limpar=True)
        if _ == 1:
            novaEtiqueta = input("\n✏️ Nova etiqueta: ")
            despesasFixas[novaEtiqueta] = despesasFixas.pop(idEtiqueta[id]) #apaga a etiqueta antiga e atribui a nova aos valores
        if _ == 2:
            novoDia = inputInteligente("📅 Novo dia: ", ret=int)
            despesasFixas[idEtiqueta[id]] = [novoDia, despesasFixas[idEtiqueta[id]][1]]
        if _ == 3: 
            novoValor = inputInteligente("💳️ Novo valor: R$", ret=float)
            despesasFixas[idEtiqueta[id]] = [despesasFixas[idEtiqueta[id]][0], novoValor]
    elif opc == 3:
        id = inputInteligente("\n🆔 Digite o id para deletar: ", ret=int)
        despesasFixas.pop(idEtiqueta[id])

    print(imprimir()[1])

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

def resumoFeito(con, cursor, conf, usuario, dataLista, semCheck=False):
    """
    Verifica se o resumo mensal foi feito
    semCheck=False: Se a função vai fazer os 'checks' do intervalo de dias e se o resumo mensal foi feito
    """
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
        try: cursor.execute(connsql.criarTabela(dataLista[1], dataLista[2], res=True)) #TODO: consertar essa merda, nao ta criando a tabela
        except ProgrammingError: pass

        subtotais = connsql.executar(cursor, f"SELECT SUBTOTAL FROM {TAB}")

        for subtotal in subtotais:
            saidas += subtotal[0]
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
            entradas = inputInteligente("💵 Quanto você ganhou esse mês? R$", ret=float)
        
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
            total: float = entradas - saidas #calcula o total com base nas entradas e saídas

            cursor.execute(f"INSERT INTO {TAB}R VALUES ({entradas}, {saidas}, {total})")
            connsql.mostrarTabela(cursor, "*", f"{TAB}R", ordenar=False)
            con.commit()
    
            return True #retorna True porque o resumo foi concluído e feito
        else: return False #se o usuário não quiser

    return True #retorna True se não era dia de fazer o resumo ou semCheck era True e o usuário não quis


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
        usuario = inputInteligente("🧑 Login: ", ret=str, strVazia=False).capitalize()

    if usuario in conf['usuarios']:
        connsql.config['database'] = usuario #verifica se o usuário existe
        while True: #checa a senha
            if conf['senhaMestra']:
                _ = getpass("🔒️ Senha-Mestra: ")
                if _ == "": print(colored("Abortar missão!", "red")); sys.exit()
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
            opcoes(conf, usuario, con, cursor, *dataLista) #mandar o usuário pro menu de opções
            
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

def inicializar(usuario_arg="arg"):
    """
    Inicializa as configurações, usuário e verifica se é dia de RM
    """
    #carrega o arquivo de configuração na variável 'conf'
    with open("garracio.json", "r") as f: conf = j.load(f)
    usuario, con, cursor = login(conf, usuario=usuario_arg)
    
    verificarDespesasFixas(cursor, con, conf, usuario)

    conf[usuario]['config']['resumoMensalFeito'] = resumoFeito(con, cursor, conf, usuario, dataLista)
    if dia == "01" and conf[usuario]['config']['resumoMensalFeito']:
        conf[usuario]['config']['resumoMensalFeito'] = False

    with open("garracio.json", "w") as f: j.dump(conf, f, indent=4)

    return conf, usuario, con, cursor, *dataLista


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
            _ = inputInteligente(f"💳️ {i} R$", ret=float)
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

    colsStr = input("\nDigite as colunas " + colored("em ordem, separadas por '; '", "red") +
                     "\n(não é necessário incluir 'Dia', 'Etiqueta' e 'SUBTOTAL'): ")

    if colsStr == "":
        return conf

    colsUsuario: list = colsStr.split("; ")

    cols.extend(col.capitalize() for col in colsUsuario if col not in cols)
    
    for i in range(len(cols)): #deixar tudo com letra maiúscula
        cols[i] = cols[i].capitalize()
    cols.append("SUBTOTAL") #'SUBTOTAL' obrigatório

    conf[usuario]['colunas'] = cols


    with open("garracio.json", "w") as f: j.dump(conf, f, indent=4)
    return conf
 
def opcoes(conf: dict, usuario: str, con, cursor, dataLista):
    _ = inputInteligente(f"\n⚙️ Selecione uma configuração:\n\
                \n[1] 📆 Realizar o resumo mensal\
                \n[2] 💴 Configurar renda fixa\
                \n[3] 💳️ Configurar despesas fixas\
                \n[4] ⌛️ Configurar intervalo de dias para o resumo mensal\
                \n[5] 🧑 Mudar usuário\
                \n[6] 🔑 Alterar Senha-Mestra\
                \n[7] 📑 Configurar colunas para {usuario}\
                \n\n[9] ⬅️ Voltar\
                \n\n=>", ret=int, limpar=True)

    if _ == 1:
        if not (con or cursor): print(colored("🔄 Reinicie para acessar essa configuração!", "black", "on_green")); sys.exit()
        resumoFeito(con, cursor, conf, usuario, dataLista, semCheck=True)
    elif _ == 2:
        configurarRendaFixa(conf, usuario)
    elif _ == 3:
        configurarDespesasFixas(conf, usuario)
    elif _ == 4:
        configurarRMminmax(conf, usuario)
    elif _ == 5:
        return None, None, None, None, None, None, None, False, True # Último True para indicar que o usuário mudou
    elif _ == 6:
        configurarSenhaMestra(conf)
    elif _ == 7:
        with open("garracio.json", "r") as f: conf = j.load(f)
        configurarColunas(conf, usuario)
        connsql.reconstruirTabela(cursor, conf, usuario, mes, ano)
    elif _ == 9:
        os.system(CL)
        return conf, usuario, con, cursor, *dataLista, False, False

    return conf, usuario, con, cursor, *dataLista, False, False #Retorna os valores originais e False para indicar que a data não foi alterada


def main(conf, usuario, con, cursor, *dataLista, tipoExecucao=0, dataSimulada=False):
    """
    Função principal
    tipoExecucao:
        - Perguntar (0)
        - CLI (1)
        - Web (2)
    """
    global TAB
    
    connsql.sincronizar(cursor)


    if tipoExecucao == 0:
        tipoExecucao = inputInteligente(f"{usuario}, selecione a interface:\
                                \n[1] ⌨️Executar diretamente (pela linha de comando)\
                                \n[2] 🖥️Executar interface web (EXPERIMENTAL)\
                                \n\n=>", ret=int, limpar=True)
    
    if tipoExecucao == 1:
        TAB = f"{dataLista[1]}{dataLista[2]}"

        print(colored(f"\n👋 Olá {usuario}", "yellow") + ", bem vindo ao "+ colored("Garracio", "black", "on_green")+"!\n")

        print(colored(f"📅 Data atual: {d.strftime('%d/%m/%Y')}", "white", "on_black"), end='')

        print(
            colored(f"\n📅 Data simulada: {dataLista[0]} de {dataLista[1]}, {'20'+dataLista[2]}\n", "black", "on_blue"),
            end=''
        ) if dataSimulada else None

        opc = inputInteligente(
            "\n[@] ⚙️ Simular data" \
            "\n\nO que deseja fazer hoje❓️\n \
            \n[1] ➕ Adicionar gastos de hoje\
            \n[2] ➖ Remover os gastos de um dia\
            \n[3] ✏️ Alterar entrada\
            \n[4] 🔎 Consultar um dia\
            \n[5] 📊 Ver tabela do mês\
            \n[6] 🧾 Ver outra tabela\
            \n\n[0] ⚙️ Opções\
            \n[9] ⬅️ Sair\
            \n\n=>",
            ret=str, limpar=True, strVazia=False)

        print()

        #tenta criar a tabela do mês caso não exista
        try: cursor.execute(connsql.criarTabela(dataLista[1], dataLista[2], colunas=conf[usuario]['colunas']))
        except ProgrammingError: pass

        match(opc):
            case '@':  # Mudar data simulada
                print("Formato: dd/mm/aaaa")
                dataNovaLista = inputInteligente("📅 Data: ", ret=str, strVazia=False).split("/")
                dataNovaLista[1] = connsql.numeropraMes(int(dataNovaLista[1]))
                dataNovaLista[2] = dataNovaLista[2][2:4]
                os.system(CL)

                main(conf, usuario, con, cursor, *dataNovaLista, tipoExecucao=1, dataSimulada=True)

            case '1': # Adicionar gastos de hoje
                adicionarGastos(con, cursor, conf, dataLista[0], usuario)
                main(conf, usuario, con, cursor, *dataLista, tipoExecucao=1, dataSimulada=dataSimulada)

            case '2': # Remover gastos de um dia
                connsql.mostrarTabela(cursor, "*", TAB)
                idRemover = inputInteligente("\n✏️ Digite o ID da linha que você quer remover: ", ret=int)
                cursor.execute(f"DELETE FROM {TAB} WHERE ID={idRemover}")
                con.commit()
                main(conf, usuario, con, cursor, *dataLista, tipoExecucao=1, dataSimulada=dataSimulada)

            case '3': # Alterar um dia (por id)
                tabelasEnum = connsql.mostrarTabelas(cursor, enumerarId=True)
                id = inputInteligente("\n✏️ Digite o ID da tabela: ", ret=int)
                tabela = tabelasEnum[id]
                
                if not "R" in tabela:
                    connsql.mostrarTabela(cursor, "*", tabela)
                    idAlterar = inputInteligente("\n✏️ Digite o ID da entrada a alterar: ", ret=int)

                    alterarEntrada(con, cursor, tabela, id=idAlterar)

                else:
                    connsql.mostrarTabela(cursor, "*", tabela, ordenar=False)
                    colunaAlterar = inputInteligente("\n✏️ Digite o nome da coluna a alterar: ", ret=str, strVazia=False)

                    alterarEntrada(con, cursor, tabela, col=colunaAlterar)

                main(conf, usuario, con, cursor, *dataLista, tipoExecucao=1, dataSimulada=dataSimulada)

            case '4': # Consultar dia
                connsql.executareMostrar(cursor, f"SELECT Dia FROM {TAB} ORDER BY Dia ASC")
                diaConsultar = inputInteligente("\n📅 Qual dia você deseja ver? ", ret=int)
                connsql.executareMostrar(cursor, f"SELECT * FROM {TAB} WHERE Dia={diaConsultar} ORDER BY Dia ASC")
                main(conf, usuario, con, cursor, *dataLista, tipoExecucao=1, dataSimulada=dataSimulada)

            case '5': # Ver mês
                connsql.mostrarTabela(cursor, "*", TAB)
                main(conf, usuario, con, cursor, *dataLista, tipoExecucao=1, dataSimulada=dataSimulada)

            case '6': # Ver outra tabela
                tabelasEnum = connsql.mostrarTabelas(cursor, enumerarId=True)
                id = inputInteligente("✏️ Digite o ID da tabela: ", ret=int)
                tabela = tabelasEnum[id]

                if not "R" in tabela: connsql.mostrarTabela(cursor, "*", tabela)
                else: connsql.mostrarTabela(cursor, "*", tabela, ordenar=False)
                main(conf, usuario, con, cursor, *dataLista, tipoExecucao=1, dataSimulada=dataSimulada)

            case '9': # Sair
                print(f"\n👋 Tchau, {usuario}.\n"+colored("Não se esqueça de mim!!", "black", "on_red"))
                sys.exit()
            case '0': # Opções
                os.system(CL)
                conf, usuario, con, cursor, *dataLista, dataAlterada, usuarioMudou = opcoes(conf, usuario, con, cursor, dataLista)
                if dataAlterada or usuarioMudou:
                    if usuarioMudou:
                        conf, usuario, con, cursor, *dataLista = inicializar(usuario_arg="arg")
                    os.system(CL)
                    main(conf, usuario, con, cursor, *dataLista, tipoExecucao=1)
                main(conf, usuario, con, cursor, *dataLista, tipoExecucao=1)

    elif tipoExecucao == 2:
            backend.iniciar(host=connsql.config['host'], usuario=usuario)


if __name__ == "__main__":
    # Inicialização inicial para obter todos os dados
    if any(arg in sys.argv for arg in ["--help", "-h", "help", "?"]): #mensagem de ajuda 
        print(sys.argv)
        print("Uso: [ARGS] usuario\n\nARGS:\
        \n\t-cli: Executar interface em linha de comando \
        \n\n\t-web: Executar interface na web (EXPERIMENTAL!) \
        \n\nusuario: Nome do usuário para login\n")
        sys.exit() 

    # Determina o usuário a partir dos argumentos ou usa a inicialização padrão
    if sys.argv[-1] not in connsql.EXCECOES:
        conf, usuario, con, cursor, *dataLista = inicializar(usuario_arg=sys.argv[-1].capitalize())
    else:
        conf, usuario, con, cursor, *dataLista = inicializar()

    # Passa as variáveis para a função main
    if "-web" in sys.argv:
        main(conf, usuario, con, cursor, *dataLista, tipoExecucao=2)
    elif "-cli" in sys.argv:
        main(conf, usuario, con, cursor, *dataLista, tipoExecucao=1)
    else:
        main(conf, usuario, con, cursor, *dataLista)
