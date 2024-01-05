import mysql.connector as mysqlc
from prettytable import PrettyTable as pt

MESES = ["Janeiro", "Fevereiro", "Marco", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]

config = {
    'user': 'FDC_Roseli',
    'password': 'Rosel1',
    'host': '192.168.15.32',
    'database': 'FDC',
    'raise_on_warnings': True,
}

def make_table(mes, ano, res=False):
    if res: return f"CREATE TABLE {mes}{ano}R (Entradas FLOAT NOT NULL DEFAULT 0, Saidas FLOAT NOT NULL DEFAULT 0, TOTAL FLOAT NOT NULL DEFAULT 0)"
    else: return f"CREATE TABLE {mes}{ano} (ID INT AUTO_INCREMENT PRIMARY KEY, Dia INT, Educacao FLOAT, Saude FLOAT, Lazer FLOAT, Outros FLOAT, SUBTOTAL FLOAT NOT NULL DEFAULT 0)"

def show_tables(cursor):
    tbs = pt(["Tabelas"])
    cursor.execute("SHOW TABLES")

    for table_name in cursor:
        tbs.add_row(table_name)

    print(tbs)

def connect():
    try:
        connection = mysqlc.connect(**config)
        if connection.is_connected(): 
            print("Conectado ao MySQL.")
            cursor = connection.cursor()
            
    except mysqlc.Error as err:
        print(f"Erro: {err}")
        return err
    
    return connection, cursor

def show_table(cursor, vals, table):
    if vals != "*": cursor.execute(f"SELECT ({vals}) FROM {table}")
    else: cursor.execute(f"SELECT {vals} FROM {table}")

    results = cursor.fetchall()    
    _ = pt()
    _.field_names = [i[0] for i in cursor.description]
    for row in results:
        _.add_row(row)
    print(_)

def exec(cursor, query: str):
    cursor.execute(query)
    results = cursor.fetchall()
    return results

def exec_show(cursor, query: str) -> None:
    cursor.execute(query)
    results = cursor.fetchall()

    _ = pt()
    _.field_names = [i[0] for i in cursor.description]
    for row in results:
        _.add_row(row)
    print(_)

def ntomonth(m: int):
    for i in range(1,13):
        if m == i:
            return MESES[i-1]

if __name__ == "__main__":
    connection, cursor = connect(**config)
    if 'connection' in locals() and connection.is_connected():
        cursor.close()
        connection.close()
        print("Conexão fechada")

