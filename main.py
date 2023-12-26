import connsql
# from datetime import datetime

def main():
    dia = int(input("Dia: "))
    mes = input("Mês: ")
    ano = input("Ano: ")
    ano = int(ano[2:4])

    educa = float(input("Educação R$"))
    saude = float(input("Saude R$"))
    lazer = float(input("Lazer R$"))
    outros = float(input("Outros gastos R$"))

    total = educa + saude + lazer + outros

    con, cursor = connsql.connect()
    cursor.execute(f"INSERT INTO {mes}{ano} (Dia, Educacao, Saude, Lazer, Outros, TOTAL) VALUES ({dia}, {educa}, {saude}, {lazer}, {outros}, {total})")

    connsql.exec_show(cursor, f"SELECT * FROM {mes}{ano}")

if __name__ == "__main__": main()

