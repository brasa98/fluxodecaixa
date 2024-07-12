# Fluxo de Caixa

### Código funcional, simples e sem nenhum erro.

Template de tabela: CREATE TABLE MesANO (ID INT AUTO_INCREMENT PRIMARY KEY, Dia INT, Educacao FLOAT, Saude FLOAT, Lazer FLOAT, Outros FLOAT, SUBTOTAL FLOAT NOT NULL DEFAULT 0);

# REGISTRO:
    -Adicionar detecção de data. FEITO (v1.5)
    -Adicionar uma tabela para cada mês. FEITO (v1)
    -Automaticamente criar tabelas do mês caso não existam FEITO (v1.7)
    -Adicionar uma tabela para o ano inteiro mostrando o resumo dos meses anteriores. FEITO (v1.7)
	-Quanto ganhou (fim de mês). EXP (v1.7)
		> Tabela separada, NOME=MesAnoR
		> Colunas: Entradas/Saídas/TOTAL	
	-Adicionado um arquivo de configuração (fdc.ini) TR
		> Principalmente para saber se já foi revisado o mês
	-Criar uma DB por ano? talvez...não
	
	--|ID; DIA; *GASTOS FIXOS*; SUBTOTAL| (mensal) OK
		> Gastos fixos: "Educação Saúde Lazer e Outros"
	
	-Adicionado o gerenciamento de usuários WIP (v2.0)
		> Usuários localizados no fdc.ini
