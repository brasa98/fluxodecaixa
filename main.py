from prettytable import PrettyTable
import connsql, backend
import os, hashlib, json as j, sys
from mysql.connector import ProgrammingError
from datetime import datetime
from getpass4 import getpass
from termcolor import colored

# Verifica o SO e define o comando de limpar a tela
if os.name == 'nt': CL = "cls"
else: CL = "clear"

d = datetime.now()
dia = d.strftime("%d")
mes = connsql.numeropraMes(int(d.strftime("%m")))
ano = d.strftime("%Y")[2:4]

COLUNAS_PADRAO = ["Etiqueta", "Educação", "Saúde", "Lazer", "Outros"]

def adicionarGastos(con, cursor, conf, usuario, dia, mes, ano): # Adicionado dia, mes, ano
    """
    Adicionar os gastos do dia simulado
    """
    TAB = f"{mes}{ano}" # Definido localmente
    colunasStr = ""

    colunasValores = receberColunas(cols=conf[usuario]['colunas']) #pega os VALUES
    colunasValores[0] = f"'{colunasValores[0]}'" # só coloca o '' na etiqueta pra não dar erro
    subtotal = sum(colunasValores[1:]) #remove a coluna 'Etiqueta'

    colunasValores = ", ".join(list(map(str, colunasValores))) #transforma tudo em string

    colunasStr = ", ".join(conf[usuario]['colunas']) #pega o nome das colunas pra colocar no INTO

    query = f"INSERT INTO {TAB} ({colunasStr}) VALUES ({dia}, {colunasValores}, {subtotal})"

    cursor.execute(query)
    connsql.mostrarTabela(cursor, "*", TAB)
    con.commit()

def configurarSenhaMestra(conf: dict):
    """
    Configurar a senha-mestra global a ser utilizada
    """
    senhaMestra = getpass("Qual será a nova senha mestra? ").encode()
    with open('garracio.json', 'w') as f:
        conf['senhaMestra'] = hashlib.sha256(senhaMestra).hexdigest()
        j.dump(conf, f, indent=4)

def configurarRMminmax(conf, usuario):
    """
    Configura intervalo de dias (mínimo e máximo) para fazer o resumo mensal
    """

    minDia, maxDia = input("\n⚙️ Digite o intervalo de tempo em dias para fazer o resumo mensal.\
                        \nFormato: min-max (incluindo os dois): ").split("-")
    
    conf[usuario]['config']['rmMinMax'] = [int(minDia), int(maxDia)]

    with open("garracio.json", "w") as f: j.dump(conf, f, indent=4)

def resumoFeito(con, cursor, conf, usuario, dia, mes, ano, semCheck=False): # Adicionado dia, mes, ano
    """
    Verifica se o resumo mensal foi feito
    """
    TAB = f"{mes}{ano}" # Definido localmente

    if semCheck or (( int(dia) >=conf[usuario]['config']['rmMinMax'][0] and #verifica o intervalo de dias por usuário
                      int(dia) <= conf[usuario]['config']['rmMinMax'][1] )
                      and not conf[usuario]['config']['resumoMensalFeito']):
        
        opc = input("\n📝 Deseja resumir seu mês? (s/n) ")
        if opc.lower() == 's':
            entra = float(input("💵 Quanto você ganhou esse mês? R$"))
            
            try: cursor.execute(connsql.criarTabela(mes, ano, res=True))
            except ProgrammingError: pass

            _ = connsql.executar(cursor, f"SELECT SUBTOTAL FROM {TAB}")
            sai = 0
            for i in _: #só Deus sabe o que esse for faz!
                for k in i:
                    sai += k
            total = entra - sai #calcula o total com base nas entradas e saídas

            cursor.execute(f"INSERT INTO {TAB}R VALUES ({entra}, {sai}, {total})")
            connsql.mostrarTabela(cursor, "*", f"{TAB}R", ordenar=False)
            con.commit()
    
            with open("garracio.json", "w") as f: j.dump(conf, f, indent=4)
            return True # Retorna True se o resumo foi feito
        else: return False
    return True # Retorna True se não era dia de fazer o resumo ou semCheck era True e o usuário não quis


def login(conf: dict, usuario="arg"):
    """
    Lógica de login e criação de usuários para o Garracio
    usuario="arg": Se for "arg", perguntar o usuário, se não, apenas pedir a senha
    """
    global dia

    os.system(CL)
    
    if usuario == "arg":
        usuarios = ", ".join(conf['usuarios']) if conf['usuarios'] != [] else colored("Não há usuários cadastrados!", "white", "on_red")
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
                    ]
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
            opcoes(conf, usuario, con, cursor, dia, mes, ano)
            
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
    

    # Atualiza o estado do resumo mensal
    conf[usuario]['config']['resumoMensalFeito'] = resumoFeito(con, cursor, conf, usuario, dia, mes, ano)
    if dia == "01": # Use string para comparar com strftime
        conf[usuario]['config']['resumoMensalFeito'] = False
    with open("garracio.json", "w") as f: j.dump(conf, f, indent=4)

    return conf, usuario, con, cursor, dia, mes, ano # Retorna todos os valores


def receberColunas(cols=COLUNAS_PADRAO):
    """
    Pega as saídas do usuário com base nas colunas configuradas
    """
    valores = []
    
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

    colsPadrao = ["Dia"] + COLUNAS_PADRAO + ["SUBTOTAL"]
    colsPadraoPT = PrettyTable() # o PT é PrettyTable tá pelo amor de Deus
    colsPadraoPT.field_names = colsPadrao

    colsAtuaisPT = PrettyTable()
    colsAtuaisPT.field_names = conf[usuario]['colunas']

    print(colored("\nColunas padrão: \n", "white", "on_grey"), colsPadraoPT)
    print(colored("Colunas atuais: \n", "black", "on_white"), colsAtuaisPT)

    cols_str = input("\nDigite as colunas " + colored("em ordem, separadas por '; '", "red") +
                     "\n(não é necessário incluir 'Dia', 'Etiqueta' e 'SUBTOTAL'): ")

    cols_usuario = cols_str.split("; ")

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
                \n3-⌛️ Configurar intervalo de dias para o resumo mensal\
                \n4-🧑 Mudar usuário\
                \n5-🔑 Alterar Senha-Mestra\
                \n6-📑 Configurar colunas para {usuario}\
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
        configurarRMminmax(conf, usuario)
    elif _ == 4:
        return None, None, None, None, None, None, None, False, True # Último True para indicar que o usuário mudou
    elif _ == 5:
        configurarSenhaMestra(conf)
    elif _ == 6:
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
                adicionarGastos(con, cursor, conf, usuario, dia, mes, ano)
            case 2: # Remover gastos de um dia
                connsql.mostrarTabela(cursor, "*", TAB)
                id_remover = input("✏️ Digite o ID da linha que você quer remover: ")
                cursor.execute(f"DELETE FROM {TAB} WHERE ID={id_remover}")
                con.commit()
            case 3: # Consultar dia
                d_consultar = int(input("📅 Qual dia você deseja ver? "))
                connsql.executareMostrar(cursor, f"SELECT * FROM {TAB} WHERE Dia={d_consultar} ORDER BY Dia ASC")
            case 4: # Ver mês
                connsql.mostrarTabela(cursor, "*", TAB)
            case 5: # Ver outra tabela
                connsql.mostrarTabelas(cursor)
                t = input("✏️ Digite o nome da tabela: ")
                connsql.mostrarTabela(cursor, "*", t)
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
            backend.iniciar(host="brasa.onthewifi.com", usuario=usuario)


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
