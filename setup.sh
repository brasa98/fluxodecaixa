#!/bin/bash

read -p "Digite o nome do banco de dados: " db_name
read -p "Digite o nome do usuário: " user_name
read -s -p "Digite a senha do usuário: " user_password
echo
read -s -p "Digite a senha root: " root_password
echo

sudo docker run -d --name fluxo_de_caixa \
  -e MYSQL_DATABASE="$db_name" \
  -e MYSQL_USER="$user_name" \
  -e MYSQL_PASSWORD="$user_password" \
  -e MYSQL_ROOT_PASSWORD="$root_password" \
  -p 3306:3306 \
  -v my-db:/var/lib/mysql \
  --restart always \
  mysql:8.2

echo "Esperando 5 segundos..."
sleep 5

query="GRANT SELECT, INSERT, CREATE, DELETE, DROP, SHOW DATABASES, UPDATE ON *.* TO '$user_name'@'localhost';"

sudo docker exec -it fluxo_de_caixa mysql -uroot -p"$root_password" -e "$query"
