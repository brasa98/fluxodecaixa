import mysql.connector as mysqlc
from prettytable import PrettyTable as pt
import json as j
from dotenv import dotenv_values
from termcolor import colored

ENV = dotenv_values(".env")

MESES = ["Janeiro", "Fevereiro", "Marco", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
COLUNAS_PADRAO = ["Etiqueta", "Educação", "Saúde", "Lazer", "Outros"]
EXCECOES = ("mysql", "sys", "information_schema", "performance_schema", "virobase", "AMPS", "ADM", "python", "main.py", "-cli", "-web")

try:
    config = {
        'user': ENV['USER'],
        'password': ENV['PASSWORD'],
        'host': ENV['HOST'],
        'database': 'ADM',
        'raise_on_warnings': True,
    }
except KeyError:
    print(colored("Você não definiu as variáveis de ambiente!\nInclua-as no '.env' ou execute o 'setup.sh'", "white", "on_red"))
    exit()

def criarTabela(mes, ano, colunas=COLUNAS_PADRAO, res=False):
    """
    Cria uma tabela com base no mês e ano.
    res=False: Indica se a tabela será de resumo ou não
    """

    colunas_cp = colunas.copy()

    if res:
        return f"CREATE TABLE {mes}{ano}R  (Entradas FLOAT NOT NULL DEFAULT 0, \
                                            Saidas FLOAT NOT NULL DEFAULT 0, \
                                            TOTAL FLOAT NOT NULL DEFAULT 0)"
    else:
        if colunas == COLUNAS_PADRAO:
            return f"CREATE TABLE {mes}{ano} (ID INT AUTO_INCREMENT PRIMARY KEY, \
                                            Dia INT, Etiqueta VARCHAR(30) NOT NULL, \
                                            Educacao FLOAT, Saude FLOAT, \
                                            Lazer FLOAT, Outros FLOAT, \
                                            SUBTOTAL FLOAT NOT NULL DEFAULT 0)"
        else: 
            colunas_cp.pop(0); colunas_cp.pop(0); colunas_cp.pop(-1) # remover 'Dia', 'Etiqueta' e 'SUBTOTAL'
            return f"CREATE TABLE {mes}{ano} (ID INT AUTO_INCREMENT PRIMARY KEY, \
                                            Dia INT, Etiqueta VARCHAR(30) NOT NULL, \
                                            {" FLOAT, ".join(colunas_cp) + " FLOAT, "} \
                                            SUBTOTAL FLOAT NOT NULL DEFAULT 0)"
        
def reconstruirTabela(cursor, conf, usuario, mes, ano):
    """
    Recria a tabela com as colunas novas
    """
    tabela = f"{mes}{ano}"
    mostrarTabela(cursor, "*", tabela)
    _ = input( colored("\nSalve os dados dessa tabela!", "white", "on_red") +
                "\n\n🔄 Excluir tabela e reconstruir com as colunas novas?? \
                \nOBS: É recomendado fazer isso no dia 1 do mês‼️\n\n(s/n) =>")
    if _.lower() == 's':
        executar(cursor, f"DROP TABLE {tabela}")
        executar(cursor, criarTabela(mes, ano, conf[usuario]['colunas']))
        print(f"✅ Tabela '{tabela}' recriada com sucesso!")
    else:
        conf[usuario]['colunas'] = COLUNAS_PADRAO
        with open("garracio.json", "w") as f: j.dump(conf, f, indent=4)
        print("❌ Atualização de colunas cancelada!\nAbortar missão!")

def conectar():
    """
    Realiza a conexão ao MySQL com base no dicionário de configuração 'config'
    """
    mysqlc.connect
    try:
        conexao = mysqlc.connect(**config)
        if conexao.is_connected(): 
            print(f"🔗 Conectado ao MySQL (host:{config['host']})\n\n")
            cursor = conexao.cursor()
            
    except mysqlc.Error as err:
        try:
            # Testa o outro host caso tenha dado errado
            config['host'] = "192.168.0.109"
            conexao = mysqlc.connect(**config)
            if conexao.is_connected():
                print(f"🔗 Conectado ao MySQL (host:{config['host']})\n\n")
                cursor = conexao.cursor()
        except mysqlc.Error as err:
            print(f"Erro: {err}")
            return err
    
    return conexao, cursor

def mostrarTabela(cursor, vals, table, ordenar=True):
    """
    Mostra os valores escolhidos de uma tabela.
    """
    if ordenar:
        if vals != "*": cursor.execute(f"SELECT ({vals}) FROM {table} ORDER BY Dia ASC") #se houver valores específicos pra procurar
        else: cursor.execute(f"SELECT {vals} FROM {table} ORDER BY Dia ASC") #se for '*' (todos)
    else:
        if vals != "*": cursor.execute(f"SELECT ({vals}) FROM {table}")
        else: cursor.execute(f"SELECT {vals} FROM {table}")

    resultados = cursor.fetchall()    
    _ = pt()
    _.field_names = [i[0] for i in cursor.description]
    for linha in resultados:
        _.add_row(linha)
    print(_)

def mostrarTabelas(cursor):
    """
    Mostra as tabelas disponíveis para visualização
    """
    tbs = pt(["Tabelas"])
    cursor.execute("SHOW TABLES")

    for nome_tabela in cursor:
        tbs.add_row(nome_tabela)

    print(tbs)

def executar(cursor, query: str):
    """
    Executa uma query MySQL
    """
 
    cursor.execute(query)
    resultados = cursor.fetchall()
    return resultados

def executareMostrar(cursor, query: str) -> None:
    """
    Executa uma query no MySQL e exibe os resultados obtidos
    """
    cursor.execute(query)
    resultados = cursor.fetchall()

    _ = pt()
    _.field_names = [i[0] for i in cursor.description]
    for linha in resultados:
        _.add_row(linha)
    print(_)

def sincronizar(cursor):
    """
    Sincroniza os bancos de dados do MySQL para o garracio.json
    """
    dbs = []
    with open("garracio.json", "r") as f: conf = j.load(f)

    dbb = executar(cursor, 'SHOW DATABASES')
    #for _ in range(4): dbb.pop(-1) # Remove da lista as DB's que são do sistema

    for tupl in dbb:
        for db in tupl:
            if db not in EXCECOES: dbs.append(db) # Remove bancos de dados irrelevantes

    conf['databases'] = dbs

    with open("garracio.json", "w") as f: j.dump(conf, f, indent=4)

def numeropraMes(mes: int):
    """
    Converte o número do mês para o nome do mês em si
    """
    for i in range(1,13):
        if mes == i:
            return MESES[i-1]
