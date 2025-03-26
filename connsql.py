import mysql.connector as mysqlc
from prettytable import PrettyTable as pt

MESES = ["Janeiro", "Fevereiro", "Marco", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]

config = {
    'user': 'Garracio',
    'password': 'garracio',
    'host': '192.168.15.32',
    'database': 'Roseli',
    'raise_on_warnings': True,
}

def criarTabela(mes, ano, res=False): #TODO: Corrigir as linhas 19 e 20 de acordo com a linha 90 do README.md
    """
    Cria uma tabela com base no mês e ano.
    res=False: Indica se a tabela será de resumo ou não
    """
    if res: return f"CREATE TABLE {mes}{ano}R (Entradas FLOAT NOT NULL DEFAULT 0, Saidas FLOAT NOT NULL DEFAULT 0, TOTAL FLOAT NOT NULL DEFAULT 0)"
    else: return f"CREATE TABLE {mes}{ano} (ID INT AUTO_INCREMENT PRIMARY KEY, Dia INT, Educacao FLOAT, Saude FLOAT, Lazer FLOAT, Outros FLOAT, SUBTOTAL FLOAT NOT NULL DEFAULT 0)"


def conectar():
    """
    Realiza a conexão ao MySQL com base no dicionário de configuração 'config'
    """
    try:
        conexao = mysqlc.connect(**config)
        if conexao.is_connected(): 
            print(f"Conectado ao MySQL (host:{config['host']})\n\n")
            cursor = conexao.cursor()
            
    except mysqlc.Error as err:
        try:
            # Testa o outro host caso tenha dado errado
            config['host'] = "192.168.0.109"
            conexao = mysqlc.connect(**config)
            if conexao.is_connected():
                print(f"Conectado ao MySQL (host:{config['host']})\n\n")
                cursor = conexao.cursor()
        except mysqlc.Error as err:
            print(f"Erro: {err}")
            return err
    
    return conexao, cursor

def mostrarTabela(cursor, vals, table):
    """
    Mostra os valores escolhidos de uma tabela.
    """
    if vals != "*": cursor.execute(f"SELECT ({vals}) FROM {table} ORDER BY Dia ASC")
    else: cursor.execute(f"SELECT {vals} FROM {table} ORDER BY Dia ASC")

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
    Executa uma query MySQL e exibe os resultados obtidos
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
    Sincroniza as databases do MySQL para o garracio.ini
    """
    dbs = []
    with open("garracio.ini", "r") as f: conf = eval(f.readline())

    dbb = executar(cursor, 'SHOW DATABASES')
    for _ in range(4): dbb.pop(-1) # Remove da lista as DB's que são do sistema

    for tupl in dbb:
        for db in tupl:
            if db != "AMPS": dbs.append(db) # Remove a DB do AMPS-Mais

    conf['databases'] = dbs

    with open("garracio.ini", "w") as f: f.write(str(conf))

def numeropraMes(mes: int):
    """
    Converte o número do mês para o nome do mês em si
    """
    for i in range(1,13):
        if mes == i:
            return MESES[i-1]
