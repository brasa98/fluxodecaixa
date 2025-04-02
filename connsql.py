import connsql, backend
import os, json as j
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

COLUNAS_PADRAO = ["Etiqueta", "Educação", "Saúde", "Lazer", "Outros"]

def configurarRMminmax(conf, usuario):
    """
    Configura intervalo de dias (mínimo e máximo) para fazer o resumo mensal
    """

    min, max = input("\nDigite o intervalo de tempo em dias para fazer o resumo mensal.\
                        \nFormato: min-max (incluindo os dois): ").split("-")
    
    conf[usuario]['config']['rmMinMax'] = [int(min), int(max)]

    with open("garracio.json", "w") as f: j.dump(conf, f, indent=4)

def resumoFeito(con, cursor, conf, usuario, semCheck=False):
    """
    Verifica se o resumo mensal foi feito
    """

    if semCheck or (( int(dia) >=conf[usuario]['config']['rmMinMax'][0] and 
                      int(dia) <= conf[usuario]['config']['rmMinMax'][1] )
                      and not conf[usuario]['config']['resumoMensalFeito']):
        
        opc = input("Deseja resumir seu mês? (s/n) ")
        if opc.lower() == 's':
            entra = float(input("Quanto você ganhou esse mês? R$"))
            cursor.execute(connsql.criarTabela(mes, ano, res=True))
            _ = connsql.executar(cursor, f"SELECT SUBTOTAL FROM {TAB}")
            sai = 0 
            for i in _: #só Deus sabe o que esse for faz!
                for j in i:
                    sai += j
            total = entra - sai #calcula o total com base nas entradas e saídas

            cursor.execute(f"INSERT INTO {TAB}R VALUES ({entra}, {sai}, {total})")
            connsql.mostrarTabela(cursor, "*", f"{TAB}R")
            con.commit()
    
            with open("garracio.json", "w") as f: j.dump(conf, f, indent=4)
        else: return False
    return True


def login(conf):
    """
    Lógica de login e criação de usuários para o Garracio
    """

    os.system(CL)
    
    print(f"Usuários disponíveis: {", ".join(conf['databases'])}")
    usuario = input("Login: ").capitalize()

    if usuario in conf['databases']: connsql.config['database'] = usuario #verifica se o usuário existe
    else: #criar usuário
        _ = input("Usuário não encontrado!\nDeseja criá-lo (s/n)? ")

        if _.lower() == 's':
            conf['databases'].append(usuario)
            conf[usuario]['config']['rmMinMax'] = [28, 31]
            with open('garracio.json', 'w') as f: j.dump(conf, f, indent=4) #registra o usuário no arquivo json

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
    with open("garracio.json", "r") as f: conf = j.load(f)
    usuario, con, cursor = login(conf)
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
            _ = input(f"Etiqueta: ")
            valores.append(_)
        elif i not in ["Dia", "SUBTOTAL"]:
            _ = float(input(f"{i} R$"))
            valores.append(_)
    return valores

def configurarColunas(conf, usuario):
    """
    Configura as colunas para um usuário específico
    """
    cols = ["Dia", "Etiqueta"]

    print("\nColunas padrão: ", ["Dia"] + COLUNAS_PADRAO + ["SUBTOTAL"])
    print("Colunas atuais: ", conf[usuario]['colunas'])

    cols_str = input("\nDigite as colunas em ordem, separadas por '; '\n(não é necessário incluir 'Dia', 'Etiqueta' e 'SUBTOTAL'): ")

    cols_usuario = cols_str.split("; ")

    cols.extend(col for col in cols_usuario if col not in cols)
    
    for i in range(len(cols)): #deixar tudo com letra maiúscula
        cols[i] = cols[i].capitalize()
    cols.append("SUBTOTAL") #'SUBTOTAL' obrigatório

    conf[usuario]['colunas'] = cols


    with open("garracio.json", "w") as f: j.dump(conf, f, indent=4)
    return conf
 

def main(pular_execucao=False):
    """
    Função principal
    """
    global dia, mes, ano, usuario, con, cursor, conf
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

        try: cursor.execute(connsql.criarTabela(mes, ano, colunas=conf[usuario]['colunas']))
        except ProgrammingError: pass

        match(_):
            case 1: # Adicionar gastos de hoje
                colunas_str = ""

                colunas_valores = receberColunas(cols=conf[usuario]['colunas']) #pega os VALUES
                colunas_valores[0] = f"'{colunas_valores[0]}'" # só coloca o '' na etiqueta pra não dar erro
                subtotal = sum(colunas_valores[1:]) #remove a coluna 'Etiqueta'

                colunas_valores = ", ".join(list(map(str, colunas_valores))) #transforma tudo em string

                colunas_str = ", ".join(conf[usuario]['colunas']) #pega o nome das colunas pra colocar no INTO

                query = f"INSERT INTO {TAB} ({colunas_str}) VALUES ({dia}, {colunas_valores}, {subtotal})"

                cursor.execute(query)
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
                            \n3-Configurar intervalo de dias para o resumo mensal\
                            \n4-Mudar usuário\
                            \n5-Configurar colunas para {usuario}\
                            \n\n=>"))
                if _ == 1:
                    dia = input("Dia: ")
                    mes = connsql.numeropraMes(int(input("Mês: ")))
                    ano = input("Ano: ")[2:4]
                    main(pular_execucao=True)
                elif _ == 2:
                    resumoFeito(semCheck=True)
                elif _ == 3:
                    configurarRMminmax(conf, usuario)
                elif _ == 4:
                    with open("garracio.json", "r") as f: conf = j.load(f)
                    os.system(CL)
                    usuario, con, cursor = login(conf)
                    main(pular_execucao=True)
                elif _ == 5:
                    with open("garracio.json", "r") as f: conf = j.load(f)
                    configurarColunas(conf, usuario)
                    connsql.reconstruirTabela(cursor, conf, usuario, mes, ano)
                    
    elif tipo_execucao == 2:
        backend.iniciar(host="brasa.onthewifi.com", usuario=usuario)


if __name__ == "__main__":
    conf, usuario, con, cursor = inicializar()
    main()

