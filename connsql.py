import mysql.connector as mysqlc
from prettytable import PrettyTable as pt, from_db_cursor
import json as j, sys
from dotenv import dotenv_values
from termcolor import colored

ENV = dotenv_values(".env")

MESES = ["Janeiro", "Fevereiro", "Marco", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
COLUNAS_PADRAO = ["Etiqueta", "Educação", "Saúde", "Lazer", "Outros"]
EXCECOES = ("mysql", "sys", "information_schema", "performance_schema", "virobase", "AMPS", "ADM", "python", "main.py", "garracio", "-cli", "-web", "--help", "-h", "help", "?")

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
    sys.exit()

def criarTabela(mes, ano, colunas=COLUNAS_PADRAO, res=False) -> str:
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
                                            {', '.join(col + ' FLOAT' for col in colunas_cp)}, \
                                            SUBTOTAL FLOAT NOT NULL DEFAULT 0)"
        
def reconstruirTabela(cursor, conf: dict, usuario: str, mes, ano):
    """
    Recria a tabela com as colunas novas
    """
    tabela = f"{mes}{ano}"
    mostrarTabela(cursor, "*", tabela)
    _ = input( colored("\nSalve os dados dessa tabela!", "white", "on_red") +
                "\n\n🔄 Excluir tabela e reconstruir com as colunas novas?? \
                \nOBS: É recomendado fazer isso no dia 1 do mês‼️\n\n(s/n) => ")
    if _.lower() == 's':
        executar(cursor, f"DROP TABLE {tabela}")
        executar(cursor, criarTabela(mes, ano, conf[usuario]['colunas']))
        print(f"✅ Tabela '{tabela}' recriada com sucesso!")
    else:
        conf[usuario]['colunas'] = COLUNAS_PADRAO
        with open("garracio.json", "w") as f: j.dump(conf, f, indent=4)
        print("❌ Atualização de colunas cancelada!")
        print(colored("Abortar missão!", "red"))

def conectar():
    """
    Realiza a conexão ao MySQL com base no dicionário de configuração 'config'
    """
    try:
        conexao = mysqlc.connect(**config)
        if conexao.is_connected(): 
            print(f"🔗 Conectado ao MySQL (host:{config['host']})\n\n")
            cursor = conexao.cursor()
            
    except mysqlc.Error as err:
        try:
            config['host'] = "localhost"
            conexao = mysqlc.connect(**config)
            if conexao.is_connected():
                print(f"🔗 Conectado ao MySQL (host:{config['host']})\n\n")
                cursor = conexao.cursor()

        except mysqlc.Error as err:
            """print(f"Erro: {err}")"""
            return err
    
    return conexao, cursor

from prettytable import PrettyTable as pt
from termcolor import colored

def mostrarTabela(cursor, vals, tabela, ordenar=True):
    from prettytable import PrettyTable as pt
    from termcolor import colored

    if ordenar:
        query = f"SELECT {vals} FROM {tabela} ORDER BY Dia ASC"
    else:
        query = f"SELECT {vals} FROM {tabela}"
    cursor.execute(query)

    resultados = cursor.fetchall()
    campos = [desc[0] for desc in cursor.description]

    tabelaPretty = pt()
    tabelaPretty.field_names = campos

    for linha in resultados:
        linhaColorida = list(linha)
        if "R" in tabela:
            for i, campo in enumerate(campos):
                if campo == "Entradas":
                    linhaColorida[i] = colored(str(linha[i]), "green")
                elif campo == "Saidas":
                    linhaColorida[i] = colored(str(linha[i]), "red")
                elif campo == "TOTAL":
                    linhaColorida[i] = colored(str(linha[i]), "blue")
        tabelaPretty.add_row(linhaColorida)

    # Gera string da tabela
    tabelaStr = tabelaPretty.get_string()

    # Substitui nomes das colunas por versões coloridas
    if "R" in tabela:
        tabelaStr = tabelaStr.replace("Entradas", colored("Entradas", "black", "on_green"))
        tabelaStr = tabelaStr.replace("Saidas", colored("Saidas", "black", "on_red"))
        tabelaStr = tabelaStr.replace("TOTAL", colored("TOTAL", "black", "on_blue"))

    print(tabelaStr)
    

def mostrarTabelas(cursor, enumerarId=False):
    """
    Mostra as tabelas disponíveis para visualização
    """
    cursor.execute("SHOW TABLES")
    _ = []

    if enumerarId:
        tbs = pt(["id", "Tabelas"])
        for nomeTabela in cursor.fetchall(): _.append(nomeTabela[0])

        #adiciona um índice pra cada tabela
        tabelasEnum = {i: tabela for i, tabela in enumerate(_, start=1)}
        tbs.add_rows(tuple(tabelasEnum.items()))
        print(tbs)
        return tabelasEnum
        
    else:
        tbs = pt(["Tabelas"])

        for nomeTabela in cursor:
            print(nomeTabela)
            tbs.add_row(nomeTabela)

        print(tbs)
        return {}

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

    for tupl in dbb:
        for db in tupl:
            if db not in EXCECOES: dbs.append(db) # Remove bancos de dados irrelevantes

    conf['usuarios'] = dbs

    with open("garracio.json", "w") as f: j.dump(conf, f, indent=4)

def numeropraMes(mes: int) -> str:
    """
    Converte o número do mês para o nome do mês em si
    """
    for i in range(1,13):
        if mes == i:
            return MESES[i-1]
    return ""

if __name__ == "__main__":
    config['database'] = "Teste"
    conexao, cursor = conectar()
    mostrarTabela(cursor, "*", "Maio25R", ordenar=False)
    mostrarTabelas(cursor, enumerarId=True)
