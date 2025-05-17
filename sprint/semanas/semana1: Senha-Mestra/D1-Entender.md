# 🗺️ Dia 1 – Entender

## 🎯 Objetivo
> Defina claramente o problema que você quer resolver.
- Faça uma história de usuário.

**Como um usuário,**
**quero definir uma senha-mestra para acessar o Garracio,**
**para que a minha segurança e privacidade não sejam comprometidas.**

## 📖 Contexto
> Qual o histórico, usuários e contexto do problema?

Enquanto eu estava programando, pensei que os dados dos usuários estavam vulneráveis sem uma senha.

## ⛳️ Objetivo de Longo Prazo
> Qual o objetivo de longo prazo?
- Fazer com que os usuários tenham mais segurança ao adicionar uma senha-mestra no arquivo `garracio.json`

## ❓️ Perguntas principais
- O que pode dar errado?
    - A escrita da senha no arquivo de configuração com um algoritmo de hash confiável
- Quais as incertezas?
    - A garantia de que a senha-mestra digitada pelo usuário seja a mesma que está no arquivo (garantir que não tenha erro de escrita)

## 📝 Notas e insights
Com tudo isso em mente, penso em criar uma nova seção no dicionário config talvez assim:
``` json
{
    ...
    "senhaMestra": %hashdasenha%,
    ...
}
```
