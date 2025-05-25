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
## dia = randint(1,28)
## dia = 3
mes = connsql.numeropraMes(int(d.strftime("%m")))
## mes = "Trezembro"
ano = d.strftime("%Y")[2:4]
## ano = "99"

TAB = f"{mes}{ano}"

COLUNAS_PADRAO = ["Etiqueta", "Educação", "Saúde", "Lazer", "Outros"]

def adicionarGastos(con, cursor, conf):
    """
    Adicionar os gastos do dia simulado
    """
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

    min, max = input("\n⚙️ Digite o intervalo de tempo em dias para fazer o resumo mensal.\
                        \nFormato: min-max (incluindo os dois): ").split("-")
    
    conf[usuario]['config']['rmMinMax'] = [int(min), int(max)]

    with open("garracio.json", "w") as f: j.dump(conf, f, indent=4)

def resumoFeito(con, cursor, conf, usuario, semCheck=False):
    """
    Verifica se o resumo mensal foi feito
    """

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
        else: return False
    return True


def login(conf: dict, usuario="arg"):
    """
    Lógica de login e criação de usuários para o Garracio
    """

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
                if _ == " ": print(colored("Abortar‼️", "red")); exit()
                if hashlib.sha256(_.encode()).hexdigest() == conf['senhaMestra']:
                    print("🔓️ Login realizado!\n\n")
                    break
                else:
                    print("❌ Senha incorreta.")
                    continue
            else: configurarSenhaMestra(conf)

    else: #criar usuário
        _ = input("🤔 Usuário não encontrado!\nDeseja criá-lo (s/n)? ")

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

            os.system(CL)
            print("🔄 Reinicie o programa para aplicar as alterações!")
            sys.exit()
        elif _.lower() == 'n':
            print(colored("Abortar missão!", "red"))
            sys.exit()

    con, cursor = connsql.conectar()

    return usuario, con, cursor

def inicializar(usuario="arg"):
    """
    Inicializa as configurações, usuário e verifica se é dia de RM
    """
    #carrega o arquivo de configuração na variável 'conf'
    with open("garracio.json", "r") as f: conf = j.load(f)
    usuario, con, cursor = login(conf, usuario=usuario)
    conf[usuario]['config']['resumoMensalFeito'] = resumoFeito(con, cursor, conf, usuario)
    if dia == 1: conf[usuario]['config']['resumoMensalFeito'] = False
    with open("garracio.json", "w") as f: j.dump(conf, f, indent=4)

    return conf, usuario, con, cursor

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
    print(colored("Colunas atuais: ", "black", "on_white"), colsAtuaisPT)

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
 

def main(tipoExecucao=0):
    """
    Função principal
    """
    global dia, mes, ano, usuario, con, cursor, conf

    connsql.sincronizar(cursor)

    if tipoExecucao == 0:
        tipoExecucao = int(input(f"{usuario}, selecione a interface:\
                                \n1-⌨️Executar diretamente (pela linha de comando)\
                                \n2-🖥️Executar interface web (EXPERIMENTAL)\
                                \n\n=>"))
    
    if tipoExecucao == 1:
        print(colored(f"📅 Data atual: {datetime.now().strftime('%d/%m/%Y')}", "white", "on_black"))
        print(colored(f"📅 Data simulada: {dia} de {mes}, {'20'+ano}\n", "black", "on_blue"))
        opc = int(input(colored(f"👋 Olá {usuario}", "yellow")+", bem vindo ao "+colored("Garracio", "black", "on_green")+"!\n\nO que deseja fazer hoje❓️\
                    \n1-➕ Adicionar gastos de hoje\
                    \n2-➖ Remover os gastos de um dia\
                    \n3-🔎 Consultar um dia\
                    \n4-📊 Ver tabela do mês\
                    \n5-🧾 Ver outra tabela\
                    \n\n0-⚙️ Opções\
                    \n9-⬅️ Sair\
                    \n\n=>"))

        try: cursor.execute(connsql.criarTabela(mes, ano, colunas=conf[usuario]['colunas']))
        except ProgrammingError: pass

        match(opc):
            case 1: # Adicionar gastos de hoje
                adicionarGastos(con, cursor, conf)
            case 2: # Remover gastos de um dia
                connsql.mostrarTabela(cursor, "*", TAB)
                id = input("✏️ Digite o ID da linha que você quer remover: ")
                cursor.execute(f"DELETE FROM {TAB} WHERE ID={id}")
                con.commit()
            case 3: # Consultar dia
                d = int(input("📅 Qual dia você deseja ver? "))
                connsql.executareMostrar(cursor, f"SELECT * FROM {TAB} WHERE Dia={d} ORDER BY Dia ASC")
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
                os.system(CL)
                _ = int(input(f"⚙️ Selecione uma configuração:\n\
                            \n1-📅 Alterar data\
                            \n2-📆 Realizar o resumo mensal\
                            \n3-⌛️ Configurar intervalo de dias para o resumo mensal\
                            \n4-🧑 Mudar usuário\
                            \n5-🔑 Alterar Senha-Mestra\
                            \n6-📑 Configurar colunas para {usuario}\
                            \n\n=>"))
                if _ == 1:
                    dia = input("📅 Dia: ")
                    mes = connsql.numeropraMes(int(input("📅 Mês: ")))
                    ano = input("📅 Ano: ")[2:4]
                    main(tipoExecucao=1)
                elif _ == 2:
                    resumoFeito(con, cursor, conf, usuario, semCheck=True)
                elif _ == 3:
                    configurarRMminmax(conf, usuario)
                elif _ == 4:
                    with open("garracio.json", "r") as f: conf = j.load(f)
                    os.system(CL)
                    usuario, con, cursor = login(conf)
                    main(tipoExecucao=1)
                elif _ == 5:
                    configurarSenhaMestra(conf)
                elif _ == 6:
                    with open("garracio.json", "r") as f: conf = j.load(f)
                    configurarColunas(conf, usuario)
                    connsql.reconstruirTabela(cursor, conf, usuario, mes, ano)
                    
    elif tipoExecucao == 2:
        backend.iniciar(host="brasa.onthewifi.com", usuario=usuario)


if __name__ == "__main__":
    if any(arg in sys.argv for arg in ["--help", "-h", "help", "?"]): #mensagem de ajuda 
        print(sys.argv)
        print("Uso: [ARGS] usuario\n\nARGS:\
        \n\t-cli: Executar interface em linha de comando \
        \n\n\t-web: Executar interface na web (EXPERIMENTAL!) \
        \n\nusuario: Nome do usuário (inicial maiúscula) para login\n")
        sys.exit() 

    conf, usuario, con, cursor = inicializar(usuario=sys.argv[-1]) if sys.argv[-1] not in connsql.EXCECOES else inicializar()
    if "-web" in sys.argv:
        main(tipoExecucao=2)
    elif "-cli" in sys.argv:
        main(tipoExecucao=1)
    else:
        main()
