import connsql
from datetime import datetime

d = datetime.now()
#data = d.strftime("%d/%m/%Y")

def main():
    print(f"Data: {d.strftime('%d/%m/%Y')}")
    dia = d.strftime("%d")
    mes = d.strftime("%m")
    mes = connsql.ntomonth(int(mes))

    ano = d.strftime("%Y")
    ano = int(ano[2:4])

    educa = float(input("Educação R$"))
    saude = float(input("Saude R$"))
    lazer = float(input("Lazer R$"))
    outros = float(input("Outros gastos R$"))

    total = educa + saude + lazer + outros

    con, cursor = connsql.connect()
    cursor.execute(f"INSERT INTO {mes}{ano} (Dia, Educacao, Saude, Lazer, Outros, TOTAL) VALUES ({dia}, {educa}, {saude}, {lazer}, {outros}, {total})")

    connsql.exec_show(cursor, f"SELECT * FROM {mes}{ano}")
    con.commit()

if __name__ == "__main__": main()

