import connsql, os
from random import randint
from datetime import datetime

d = datetime.now()

con, cursor = connsql.connect()
dia = d.strftime("%d")
# dia = randint(1,28)
# dia = 28
mes = connsql.ntomonth(int(d.strftime("%m")))
# mes = "Trezembro"
ano = int(d.strftime("%Y")[2:4])
# ano = "99"

TAB = f"{mes}{ano}"

def rmFeito():
    if (int(dia) >= 28 and int(dia) <= 31) and not conf['resumo_mensal_feito']:
        _ = input("Deseja resumir seu mês? <s; n> ")
        if _.lower() == 's':
            print("Inicializando resumo do mês...")
            entra = float(input("Quanto você ganhou esse mês? R$"))
            cursor.execute(connsql.make_table(mes, ano, res=True))
            _ = connsql.exec(cursor, f"SELECT SUBTOTAL FROM {TAB}")
            sai = 0
            for i in _:
                for j in i:
                    sai += j
            total = entra - sai

            cursor.execute(f"INSERT INTO {TAB}R VALUES ({entra}, {sai}, {total})")
            connsql.show_table(cursor, "*", f"{TAB}R")
            con.commit()
    
            with open("fdc.ini", "w") as f: f.write(str(conf))
    return True

def saidas():
    e = float(input("Educação R$"))
    s = float(input("Saude R$"))
    l = float(input("Lazer R$"))
    o = float(input("Outros gastos R$"))
    return e, s, l, o
 
with open("fdc.ini", "r") as f: conf = eval(f.readline())

conf['resumo_mensal_feito'] = rmFeito()
if dia == 1: conf['resumo_mensal_feito'] = False
with open("fdc.ini", "w") as f: f.write(str(conf))

def main():
    os.system("clear")
    print(f"Data: {datetime.now().strftime('%d/%m/%Y')}\n")
    _ = int(input("Olá Roseli, sou seu Fluxo de Caixa!\n\nO que deseja fazer hoje?\
    \n1-Adicionar gastos de hoje\
    \n2-Remover os gastos de um dia\
    \n3-Consultar um dia\
    \n4-Ver tabela do mês\
    \n5-Ver outra tabela\n=>"))
    match(_):
        case 1: #Adicionar gastos de hoje
            educa, saude, lazer, outros = saidas()
            subtotal = educa + saude + lazer + outros 
            try:
                cursor.execute(f"INSERT INTO {TAB} (Dia, Educacao, Saude, Lazer, Outros, SUBTOTAL) VALUES ({dia}, {educa}, {saude}, {lazer}, {outros}, {subtotal})")
            except:
                cursor.execute(connsql.make_table(mes, ano))
                cursor.execute(f"INSERT INTO {TAB} (Dia, Educacao, Saude, Lazer, Outros, SUBTOTAL) VALUES ({dia}, {educa}, {saude}, {lazer}, {outros}, {subtotal})")
            finally:
                connsql.show_table(cursor, "*", TAB)
                con.commit()
        case 2: #Remover gastos de um dia
            connsql.show_table(cursor, "*", TAB)
            id = input("Digite o ID da linha que você quer remover: ")
            cursor.execute(f"DELETE FROM {TAB} WHERE ID={id}")
            con.commit()
        case 3: #Consultar dia
            d = int(input("Qual dia você deseja ver? "))
            connsql.exec_show(cursor, f"SELECT * FROM {TAB} WHERE Dia={d}")
        case 4: #Ver mês
            connsql.show_table(cursor, "*", TAB)
        case 5: #Ver outra tabela
            connsql.show_tables(cursor)
            t = input("Digite o nome da tabela: ")
            connsql.show_table(cursor, "*", t)

if __name__ == "__main__": main()

