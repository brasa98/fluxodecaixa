# Garracio: Gastos racionais e controlados

## Sumário
- [Introdução](#introducao)
- [Instalação](#instalacao)
    - [Versões finais](#instalacao-releases)
    - [Usando o código-fonte](#instalacao-source)
- [Histórico de Atualizações](#historico)  

## Introdução
<a id="introducao"></a>
Esse projeto foi feito para destacar a importância de gerenciar seus gastos, com uma interface intuitiva e acesso remoto, priorizo a **facilidade e simplicidade**.

###### Feito por Lucas de Morais Fracaro (2023)

### Gerenciador de despesas com:
- Tabelas mensais
- Execução híbrida (linha de comando e web)
- Suporte para mais de um usuário
- Arquivo de configuração (garracio.json)
- Executável para configuração do banco de dados (*por enquanto, apenas com Linux*)

## Instalação
<a id=instalacao></a>
### Requisitos:
- **Python** versão 3.11+
- **MySQL** versão 8.2+
- **SO: *Linux***
    - Opcional, não foi testado em Windows.

### Versões finais
<a id="instalacao-releases"></a>
- Instale o arquivo *.zip* da versão desejada na seção [releases](https://github.com/olucasfracaro/Garracio/releases)
    - Alternativamente, instale a [versão mais recente](https://github.com/olucasfracaro/Garracio/releases/latest)
- Extraia-o usando um software de sua preferência
- Execute o programa

### Instalar pelo código-fonte
<a id="instalacao-source"><a>
> **OBS: Apenas para usuários experientes!**  
> Usando o código experimental.
- Clone o repositório
    - `git clone -b rolling https://github.com/olucasfracaro/Garracio`
- Entre no diretório
    - `cd Garracio/`
- Instale os requisitos do Python
    - `pip install -r requirements.txt`
- Execute o arquivo *setup.sh* (**APENAS PARA LINUX!**)
    - `./setup.sh`
- Execute o programa
    - `python main.py`

# Histórico de Atualizações:
<a id="historico"></a>

- [X] Adicionar detecção de data. (v1.5)

- [X] Adicionar uma tabela para cada mês. (v1)

- [X] Automaticamente criar tabelas do mês caso não existam. (v1.7)

- [X] Adicionar uma tabela para o ano inteiro mostrando o resumo dos meses anteriores. (v1.7)

- [X] Quanto ganhou (fim de mês). EXP (v1.7)
	> Tabela separada, NOME=MesAnoR  
	> Colunas: Entradas/Saídas/TOTAL

- [X] Adicionado um arquivo de configuração (garracio.json)
	> Principalmente para saber se já foi revisado o mês

- [X] Criar uma DB por ano?
	> talvez... não, melhor não.  
    > Decidido q a DB é por usuário

- [X] |ID; DIA; *GASTOS FIXOS*; SUBTOTAL| (mensal)
	> Gastos fixos: Educação Saúde Lazer e Outros  
    > OUUUU, com a nova atualização v2.5, colunas personalizadas!

- [X] Adicionado o gerenciamento de usuários. (v2.0)
	> Usuários localizados no garracio.json

- [X] Adicionar coluna string para identificar cada gasto. (v2.5)

- [X] Adicionar usuário padrão e menu de opções. (v2.5)
    > Desisti do negócio de usuário padrão. Mas o menu ta funcionando

- [X] Ordenar gastos por dia. (v2.1)

- [ ] Adicionar uma interface gráfica web. WIP ()
	> Usando HTML, CSS e Flask

- [X] Personalização das colunas das tabelas. (v2.5)

- [X] Configuração do intervalo de dias para fazer o resumo mensal.

- [X] Separação das configurações por usuário. (v2.5)
    > "Lucas": {"config": [], "colunas": []}

- [ ] Adicionar login com senha por usuário, tanto headless quanto na web. EXP (v2.5.1)
    > ~~Acho melhor usar a senha da database como senha única ao invés de uma por usuário~~
    > Adicionei uma senha-mestra global no `garracio.json`

- [X] Melhorias na UI e UX (_User Interface, User Experience_). EXP (v2.5.5)
    > Emojis e cores no terminal  
    > Junto com argumentos na CLI e varíaveis de ambiente '.env'

- [ ] Colorir Entradas de green e Saídas de red
    > Metade feito, falta algumas ainda

- [X] Salário (automaticamente adicionar no resumo mensal)
    > Adicionada a rendaFixa para realizar o resumo mensal automaticamente.  
    > O usuário tem a opção de definir uma renda fixa ou continuar no formato antigo

- [ ] Despesas fixas (pro resumo mensal)

- [ ] Mover o `garracio.json` para uma tabela no MySQL?
    > Ou deixá-lo mais _seguro/secreto_

- [ ] Reescrever funções do `connsql.py` para usar `from_db_cursor()`
