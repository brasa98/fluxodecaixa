import mysql.connector as mysqlc
from prettytable import PrettyTable as pt

MESES = ["Janeiro", "Fevereiro", "Marco", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]

config = {
    'user': 'FDC',
    'password': 'caixadefluxo',
    'host': '192.168.15.32',
    'database': 'Roseli',
    'raise_on_warnings': True,
}

def make_table(mes, ano, res=False):
    """
    Cria uma tabela com base no mês e ano.
    res=False: Indica se a tabela será de resumo ou não
    """
    if res: return f"CREATE TABLE {mes}{ano}R (Entradas FLOAT NOT NULL DEFAULT 0, Saidas FLOAT NOT NULL DEFAULT 0, TOTAL FLOAT NOT NULL DEFAULT 0)"
    else: return f"CREATE TABLE {mes}{ano} (ID INT AUTO_INCREMENT PRIMARY KEY, Dia INT, Educacao FLOAT, Saude FLOAT, Lazer FLOAT, Outros FLOAT, SUBTOTAL FLOAT NOT NULL DEFAULT 0)"

def show_tables(cursor):
    """
    Mostra as tabelas disponíveis para visualização
    """
    tbs = pt(["Tabelas"])
    cursor.execute("SHOW TABLES")

    for table_name in cursor:
        tbs.add_row(table_name)

    print(tbs)

def connect():
    """
    Realiza a conexão ao MySQL com base no dicionário de configuração 'config'
    """
    try:
        connection = mysqlc.connect(**config)
        if connection.is_connected(): 
            print(f"Conectado ao MySQL (host:{config['host']})")
            cursor = connection.cursor()
            
    except mysqlc.Error as err:
        try:
            # Testa o outro host caso tenha dado errado
            config['host'] = "192.168.0.109"
            connection = mysqlc.connect(**config)
            if connection.is_connected():
                print(f"Conectado ao MySQL (host:{config['host']})")
                cursor = connection.cursor()
        except mysqlc.Error as err:
            print(f"Erro: {err}")
            return err
    
    return connection, cursor

def show_table(cursor, vals, table):
    """
    Mostra os valores escolhidos de uma tabela.
    """
    if vals != "*": cursor.execute(f"SELECT ({vals}) FROM {table}")
    else: cursor.execute(f"SELECT {vals} FROM {table}")

    results = cursor.fetchall()    
    _ = pt()
    _.field_names = [i[0] for i in cursor.description]
    for row in results:
        _.add_row(row)
    print(_)

def exec(cursor, query: str):
    """
    Executa uma query MySQL
    """
    cursor.execute(query)
    results = cursor.fetchall()
    return results

def exec_show(cursor, query: str) -> None:
    """
    Executa uma query MySQL e exibe os resultados obtidos
    """
    cursor.execute(query)
    results = cursor.fetchall()

    _ = pt()
    _.field_names = [i[0] for i in cursor.description]
    for row in results:
        _.add_row(row)
    print(_)

def sync(cursor):
    """
    Sincroniza as databases do MySQL para o fdc.ini
    """
    dbs = []
    with open("fdc.ini", "r") as f: fdc_conf = eval(f.readline())

    dbb = exec(cursor, 'SHOW DATABASES')
    for _ in range(4): dbb.pop(-1) # Remove da lista as DB's que são do sistema

    for tupl in dbb:
        for db in tupl:
            dbs.append(db)

    fdc_conf['databases'] = dbs

    with open("fdc.ini", "w") as f: f.write(str(fdc_conf))

def ntomonth(m: int):
    """
    Converte o número do mês para o nome do mês em si
    """
    for i in range(1,13):
        if m == i:
            return MESES[i-1]

if __name__ == "__main__":
    connection, cursor = connect(**config)
    if 'connection' in locals() and connection.is_connected():
        cursor.close()
        connection.close()
        print("Conexão fechada")

