# 🤔 Dia 3 – Decidir

## 💭 Ideias comparadas
- 💡 Ideia A
    - Definir senha mestra com SHA256 e guardar no `garracio.json`
- 💡 Ideia B
    - Definir como a mesma senha do banco de dados.

## 🎖️ Solução escolhida
> Detalhe a solução final.

Como dito no Dia 2 (Esboçar), escolhi a ideia A, já que a ideia B indica vulnerabilidade no sistema e banco de dados.

## ➡️ Fluxo simplificado
> Passos ou fluxograma básico da ideia.
1. Solicitar a senha ao executar o programa/via menu de opções
2. Ao obter a senha, imediatamente usar o SHA256 e armazená-la no `garracio.json`
3. Após isso, cada vez que o Garracio for executado, pedir nome do usuário e a senha-mestra
4. Comparar se o hash da entrada do usuário corresponde ao hash da senha-mestra
5. Se esqueceu a senha, contatar o administrador (eu)

**FUTURAMENTE ADICIONAR RECUPERAÇÃO DE SENHA!**
