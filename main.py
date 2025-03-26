import os
import connsql, backend
from mysql.connector import ProgrammingError
from random import randint
from datetime import datetime
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

COLUNAS_PADRAO = ["Etiqueta", "Educação", "Saúde", "Lazer", "Outros gastos"]

def resumoFeito(con, cursor, semCheck=False):
    """
    Verifica se o resumo mensal foi feito
    """
    if semCheck or ((int(dia) >= 28 and int(dia) <= 31) and not conf['resumoMensalFeito']):
        opc = input("Deseja resumir seu mês? (s/n) ")
        if opc.lower() == 's':
            print("Inicializando resumo do mês...")
            entra = float(input("Quanto você ganhou esse mês? R$"))
            cursor.execute(connsql.criarTabela(mes, ano, res=True))
            _ = connsql.executar(cursor, f"SELECT SUBTOTAL FROM {TAB}")
            sai = 0 
            for i in _: #so Deus sabe o que esse for faz!
                for j in i:
                    sai += j
            total = entra - sai #calcula o total com base nas entradas e saídas

            cursor.execute(f"INSERT INTO {TAB}R VALUES ({entra}, {sai}, {total})")
            connsql.mostrarTabela(cursor, "*", f"{TAB}R")
            con.commit()
    
            with open("garracio.ini", "w") as f: f.write(str(conf))
        else: return False
    return True


def login(conf):
    """
    Lógica de login e criação de usuários para o Garracio
    """

    os.system(CL)
    
    print(f"Usuários disponíveis: {conf['databases']}")
    usuario = input("Usuário: ").capitalize()

    if usuario in conf['databases']: connsql.config['database'] = usuario #verifica se o usuário existe
    else: #criar usuário
        _ = input("Usuário não encontrado!\nDeseja criá-lo (s/n)? ")

        if _.lower() == 's':
            conf['databases'].append(usuario)
            with open('garracio.ini', 'w') as f: f.write(str(conf)) #registra o usuário no arquivo ini

            #cria o banco de dados do usuário
            connsql.config['database'] = usuario
            con, cursor = connsql.conectar()
            cursor.execute(f"CREATE DATABASE {usuario}")

            configurarColunas(conf, usuario)

            os.system(CL)
            print("Reinicie o programa para aplicar as alterações!")
            quit()
        elif _.lower() == 'n':
            print("Abortar missão!")
            quit()

    con, cursor = connsql.conectar()

    return usuario, con, cursor

def inicializar():
    #carrega o arquivo de configuração na variável 'conf'
    with open("garracio.ini", "r") as f: conf = eval(f.readline())
    usuario, con, cursor = login(conf)
    conf['resumoMensalFeito'] = resumoFeito(con, cursor)
    if dia == 1: conf['resumoMensalFeito'] = False
    with open("garracio.ini", "w") as f: f.write(str(conf))

    return conf, usuario, con, cursor

def receberColunas(cols=COLUNAS_PADRAO):
    """
    Pega as saídas do usuário com base nas colunas configuradas
    """
    valores = []
    
    for i in cols:
        _ = input(f"{i} R$")
        valores.append(_)
    return valores
 
def configurarColunas(conf, usuario):
    """
    Configura as colunas para um usuário específico
    """
    cols = ["Dia", "Etiqueta"]

    cols_str = input("Digite as colunas em ordem, separadas por '; ': ")

    cols_usuario = cols_str.split("; ")

    cols.extend(col for col in cols_usuario if col not in cols)
    
    for i in range(len(cols)): #deixar tudo com letra maiúscula
        cols[i] = cols[i].capitalize()
    cols.append("SUBTOTAL") #'SUBTOTAL' obrigatório

    conf[f'cols_{usuario}'] = cols

    print(conf[f'cols_{usuario}'])

    with open("garracio.ini", "w") as f: f.write(str(conf))
    return conf
 

def main(pular_execucao=False):
    """
    Função principal
    """
    global dia, mes, ano, usuario, con, cursor
    tipo_execucao = 1

    connsql.sincronizar(cursor)

    if not pular_execucao:
        tipo_execucao = int(input(f"{usuario}, selecione uma opção:\
                                \n1-Executar diretamente (pela linha de comando)\
                                \n2-Executar interface web (EXPERIMENTAL)\
                                \n\n=>"))
    
    if tipo_execucao == 1:
        print(f"Data atual: {datetime.now().strftime('%d/%m/%Y')}")
        print(f"Data simulada: {dia} de {mes}, {'20'+ano}\n")
        _ = int(input(f"Olá {usuario}, bem vindo ao Garracio!\n\nO que deseja fazer hoje?\
                    \n1-Adicionar gastos de hoje\
                    \n2-Remover os gastos de um dia\
                    \n3-Consultar um dia\
                    \n4-Ver tabela do mês\
                    \n5-Ver outra tabela\
                    \n\n0-Opções\
                    \n9-Sair\
                    \n\n=>"))

        try: cursor.execute(connsql.criarTabela(mes, ano))
        except ProgrammingError: pass

        match(_):
            case 1: # Adicionar gastos de hoje
                colunas_str = ""

                with open("garracio.ini", "r") as f: conf = eval(f.readline())

                colunas = receberColunas(cols=conf[f'cols_{usuario}']) #pegar as colunas 
                subtotal = sum(colunas[1:]) #remove a coluna 

                for col in colunas:
                    colunas_str += f"{col}, "
                colunas_str.rstrip(", ")

                # TODO: Adicionar a coluna "Etiqueta" em todas as queries
                cursor.execute(f"INSERT INTO {TAB}\
                                (Dia, {colunas_str}, SUBTOTAL)\
                                VALUES ({dia}, {colunas_str}, {subtotal})")
                connsql.mostrarTabela(cursor, "*", TAB)
                con.commit()
            case 2: # Remover gastos de um dia
                connsql.mostrarTabela(cursor, "*", TAB)
                id = input("Digite o ID da linha que você quer remover: ")
                cursor.execute(f"DELETE FROM {TAB} WHERE ID={id}")
                con.commit()
            case 3: # Consultar dia
                d = int(input("Qual dia você deseja ver? "))
                connsql.executareMostrar(cursor, f"SELECT * FROM {TAB} WHERE Dia={d} ORDER BY Dia ASC")
            case 4: # Ver mês
                connsql.mostrarTabela(cursor, "*", TAB)
            case 5: # Ver outra tabela
                connsql.mostrarTabelas(cursor)
                t = input("Digite o nome da tabela: ")
                connsql.mostrarTabela(cursor, "*", t)
            case 9: # Sair
                print(f"Tchau, {usuario}.\nNão se esqueça de mim!!")
                quit()
            case 0: # Opções
                os.system(CL)
                _ = int(input(f"Selecione uma abaixo:\
                            \n1-Alterar data\
                            \n2-Realizar o resumo mensal\
                            \n3-Mudar usuário\
                            \n4-Configurar colunas para {usuario}\
                            \n\n=>"))
                if _ == 1:
                    dia = input("Dia: ")
                    mes = connsql.numeropraMes(int(input("Mês: ")))
                    ano = input("Ano: ")[2:4]
                    main(pular_execucao=True)
                elif _ == 2:
                    resumoFeito(semCheck=True)
                elif _ == 3:
                    with open("garracio.ini", "r") as f: conf = eval(f.readline())
                    os.system(CL)
                    usuario, con, cursor = login(conf)
                    main(pular_execucao=True)
                elif _ == 4:
                    with open("garracio.ini", "r") as f: conf = eval(f.readline())
                    configurarColunas(conf, usuario)
                    
    elif tipo_execucao == 2:
        backend.iniciar(host="brasa.onthewifi.com", usuario=usuario)


if __name__ == "__main__":
    conf, usuario, con, cursor = inicializar()
    main()

