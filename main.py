import connsql, os
from mysql.connector import ProgrammingError
from random import randint
from datetime import datetime

# Verifica o SO, e define o comando de limpar a tela
if os.name == 'nt': CL = "cls"
else: CL = "clear"

d = datetime.now()
dia = d.strftime("%d")
## dia = randint(1,28)
## dia = 3
mes = connsql.ntomonth(int(d.strftime("%m")))
## mes = "Trezembro"
ano = int(d.strftime("%Y")[2:4])
## ano = "99"

TAB = f"{mes}{ano}"

def rmFeito(con, cursor):
    """
    Verifica se o resumo mensal foi feito
    """
    TAB = f"{mes}{dia}"
    if (int(dia) >= 28 and int(dia) <= 31) and not conf['resumo_mensal_feito']: # Verificação
        _ = input("Deseja resumir seu mês? <s; n> ")
        if _.lower() == 's':
            print("Inicializando resumo do mês...")
            entra = float(input("Quanto você ganhou esse mês? R$"))
            cursor.execute(connsql.make_table(mes, ano, res=True))
            _ = connsql.exec(cursor, f"SELECT SUBTOTAL FROM {TAB}")
            sai = 0 
            for i in _: # Só Deus sabe o que esse for faz!
                for j in i:
                    sai += j
            total = entra - sai # Calcula o total com base nas entradas e saídas

            cursor.execute(f"INSERT INTO {TAB}R VALUES ({entra}, {sai}, {total})")
            connsql.show_table(cursor, "*", f"{TAB}R")
            con.commit()
    
            with open("fdc.ini", "w") as f: f.write(str(conf))
    return True


def login():
    """
    Lógica de usuários para o Fluxo de Caixa
    """

    os.system(CL)
    
    if conf['default_db'] is not None:
        user = conf['default_db']
        print(user)
        connsql.config['database'] = user
        con, cursor = connsql.connect()
        return user, con, cursor
    
    print(f"Usuários disponíveis: {conf['databases']}")
    user = input("Usuário: ").capitalize()

    if user in conf['databases']: connsql.config['database'] = user # Verifica se o usuário existe
    else:
        _ = input("Usuário não encontrado!\nDeseja criá-lo (s/n)? ")

        if _.lower() == 's':
            conf['databases'].append(user)
            with open('fdc.ini', 'w') as f: f.write(str(conf)) # Registra o usuário no arquivo ini

            # Cria a database do usuário
            connsql.config['database'] = "Roseli"
            con, cursor = connsql.connect()
            cursor.execute(f"CREATE DATABASE {user}")

            os.system(CL)
            print("Reinicie o programa para aplicar as alterações!")
            quit()
        elif _.lower() == 'n':
            print("Abortar missão!")
            quit()

    con, cursor = connsql.connect()

    return user, con, cursor

# Carrega o arquivo de configuração na variável 'conf'
with open("fdc.ini", "r") as f: conf = eval(f.readline())
user, con, cursor = login()
conf['resumo_mensal_feito'] = rmFeito(con, cursor)
if dia == 1: conf['resumo_mensal_feito'] = False
with open("fdc.ini", "w") as f: f.write(str(conf))


def saidas():
    """
    Pega as saídas do usuário
    """
    e = float(input("Educação R$"))
    s = float(input("Saude R$"))
    l = float(input("Lazer R$"))
    o = float(input("Outros gastos R$"))
    return e, s, l, o
 

def main():
    """
    Função principal
    """
    global dia, mes, ano, user
    os.system(CL)

    connsql.sync(cursor)
    print(f"Data atual: {datetime.now().strftime('%d/%m/%Y')}")
    print(f"Data usada: {dia} de {mes}, {ano}\n")
    TAB = f"{mes}{ano}"
    _ = int(input(f"Olá {user}, sou seu Fluxo de Caixa!\n\nO que deseja fazer hoje?\
    \n1-Adicionar gastos de hoje\
    \n2-Remover os gastos de um dia\
    \n3-Consultar um dia\
    \n4-Ver tabela do mês\
    \n5-Ver outra tabela\
    \n\n0-Opções\
    \n\n=>"))

    try: cursor.execute(connsql.make_table(mes, ano))
    except ProgrammingError: pass

    match(_):
        case 1: # Adicionar gastos de hoje
            educa, saude, lazer, outros = saidas()
            subtotal = educa + saude + lazer + outros 
            try:
                cursor.execute(f"INSERT INTO {TAB} (Dia, Educacao, Saude, Lazer, Outros, SUBTOTAL) VALUES ({dia}, {educa}, {saude}, {lazer}, {outros}, {subtotal})")
            except ProgrammingError:
                cursor.execute(connsql.make_table(mes, ano))
                cursor.execute(f"INSERT INTO {TAB} (Dia, Educacao, Saude, Lazer, Outros, SUBTOTAL) VALUES ({dia}, {educa}, {saude}, {lazer}, {outros}, {subtotal})")
            finally:
                connsql.show_table(cursor, "*", TAB)
                con.commit()
        case 2: # Remover gastos de um dia
            connsql.show_table(cursor, "*", TAB)
            id = input("Digite o ID da linha que você quer remover: ")
            cursor.execute(f"DELETE FROM {TAB} WHERE ID={id}")
            con.commit()
        case 3: # Consultar dia
            d = int(input("Qual dia você deseja ver? "))
            connsql.exec_show(cursor, f"SELECT * FROM {TAB} WHERE Dia={d} ORDER BY Dia ASC")
        case 4: # Ver mês
            connsql.show_table(cursor, "*", TAB)
        case 5: # Ver outra tabela
            connsql.show_tables(cursor)
            t = input("Digite o nome da tabela: ")
            connsql.show_table(cursor, "*", t)
        case 0: # Opções
            os.system(CL)
            _ = int(input("Selecione uma abaixo:\n1-Alterar data\n2-Definir usuário padrão\n3-Mudar usuário\n\n=>"))
            if _ == 1:
                dia = input("Dia: ")
                mes = connsql.ntomonth(int(input("Mês: ")))
                ano = input("Ano: ")[2:4]
                main()
            elif _ == 2:
                with open("fdc.ini", "r") as f: conf = eval(f.readline())
                print(f"Usuários disponíveis: {conf['databases']}")
                user = input("Usuário padrão: ").capitalize()

                conf['default_db'] = user
                with open('fdc.ini', 'w') as f: f.write(str(conf))

if __name__ == "__main__": main()

