# Garracio: **Ga**stos **racio**nais e controlados

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
- **git** (_apenas para instalação pelo [código fonte](#instalacao-source)_)
- **Python** versão 3.11+
- **MySQL** versão 8.2+
    - **OBS: Usar _docker_ é opcional**
- **Sistema Operacional**
    - Linux (_recomendado_)
    - Windows 10+ (_experimental_)

### Versões finais
<a id="instalacao-releases"></a>
- Instale o arquivo *.zip* da versão e plataforma desejada na seção [releases](https://github.com/olucasfracaro/Garracio/releases)
    - Alternativamente, instale a [versão mais recente](https://github.com/olucasfracaro/Garracio/releases/latest)
- Extraia-o usando um software de sua preferência
- Execute o programa

### Instalar pelo código-fonte
<a id="instalacao-source"><a>
> **OBS: Apenas para usuários experientes!**  
> Usando o código experimental.
- Clone o repositório
    - `git clone https://github.com/olucasfracaro/Garracio`
        - **Dica:** Use `-b <nome-da-versao>` antes do _url_ para clonar uma versão específica
- Entre no diretório
    - `cd Garracio/`
- Execute o arquivo de instalação
    - **Linux**: `./setup.sh`
    - **Windows**: `setup.bat` ou `.\setup.ps1`
- Execute o programa
    - `python main.py`

# Histórico de Atualizações:
<a id="historico"></a>

## v2.7
- Alterações mínimas na interface de linha de comando
- Reformulações em menu, revisões de código
- Adicionada a opção de alterar um dia, caso contenha valores errôneos, por exemplo.

## v2.5.x
- Melhorias na UI e UX (_User Interface, User Experience_) - Emojis e cores no terminal, argumentos CLI, variáveis de ambiente
- Separação das configurações por usuário
- Personalização das colunas das tabelas
- Menus reformulados
- Adicionada a senha-mestra: maior segurança para entrar no Garracio
- Configuração do intervalo de dias para fazer o resumo mensal
- Reescritas funções do `connsql.py` para usar `from_db_cursor()`
- Criado `setup.bat` e `setup.ps1` para maior compatibilidade com Windows
- À prova de idiotas: verificações de tipo nas entradas do usuário

## v2.5
- Adicionar login com senha por usuário na linha de comando

## v2.x
- Gerenciamento de usuários
- Ordenar gastos por dia
- Separação das configurações por usuário
- Configuração do intervalo de dias para fazer o resumo mensal

## v1.7
- Automaticamente criar tabelas do mês caso não existam
- Adicionar uma tabela para o ano inteiro mostrando o resumo dos meses anteriores (resumo mensal)
- Quanto ganhou (fim de mês)

## v1.5
- Adicionar detecção de data

## v1.x
- Adicionar uma tabela para cada mês
- Adicionada coluna string para identificar cada gasto
- Adicionado um arquivo de configuração (garracio.json)
- DB por usuário

---
