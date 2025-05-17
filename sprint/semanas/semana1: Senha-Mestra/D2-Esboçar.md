# 📝 Dia 2 – Esboçar

## 💭 Inspiração
> Soluções existentes ou ideias similares?

Não tive nenhuma inspiração para as ideias, apenas ideias lógicas.

## 📄 Rascunhos / Ideias
- 💡 Ideia 1:
    - Definir senha-mestra com SHA256 e guardar no `garracio.json`.
- 💡 Ideia 2:
    - Definir uma senha por usuário e colocar na config[usuario] usando SHA256.
- 💡 Ideia 3:
    - Definir como a mesma senha do usuário do banco de dados.

## 🎖️ Solução preferida
> Descreva a ideia mais promissora.

Acho que a melhor ideia com certeza seria a **Nº1**, porque foi a primeira que tive em mente e é a mais segura e prática que as outras.  

### ❓️ Por quê
- **Eu poderia colocar uma senha por usuário? (Nº2)** Sim, mas achei redundante, já que o Garracio foi feito para ser usado em, por exemplo, uma família.  
- E por último, a ideia Nº3, porque tornar as duas senhas iguais indicaria uma vulnerabilidade no banco de dados, que é o objetivo contrário dessa semana 1 (aumentar a segurança)
