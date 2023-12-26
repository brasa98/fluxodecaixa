import mysql.connector as mysqlc
from prettytable import PrettyTable as pt

# Configuração da conexão
config = {
    'user': 'positivo',
    'password': '76190403',
    'host': '192.168.15.32',
    'database': 'FDC',
    'raise_on_warnings': True,
}

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

def showTable(cursor):
    results = cursor.fetchall()

    table = pt()
    table.field_names = [i[0] for i in cursor.description]

    for row in results:
        table.add_row(row)

    print(table)
    return table

def exec_show(cursor, query: str):
    cursor.execute(query)
    results = cursor.fetchall()

    _ = pt()
    _.field_names = [i[0] for i in cursor.description]
    for row in results:
        _.add_row(row)
    print(_)


if __name__ == "__main__":
    connection, cursor = connect(**config)
    if 'connection' in locals() and connection.is_connected():
        cursor.close()
        connection.close()
        print("Conexão fechada")

