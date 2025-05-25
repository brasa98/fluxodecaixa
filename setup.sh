#!/bin/bash

read -p "✏️ Digite o nome do banco de dados: " BD
read -p "✏️ Digite o nome do usuário: " USER

read -s "🔗 Digite o host: " HOST
read -s -p "🔒️ Digite a senha do usuário: " PASSWORD
echo
read -s -p "🔒️ Digite a senha root: " ROOT_PASSWORD
echo

echo "USER=${USER}\nPASSWORD=${PASSWORD}\nHOST=${HOST}" >> .env

sudo docker run -d --name GarracioDB \
  -e MYSQL_DATABASE="$BD" \
  -e MYSQL_USER="$USER" \
  -e MYSQL_PASSWORD="$PASSWORD" \
  -e MYSQL_ROOT_PASSWORD="$ROOT_PASSWORD" \
  -p 3306:3306 \
  -v my-db:/var/lib/mysql \
  --restart always \
  mysql:8.2

echo "Esperando 5 segundos..."
sleep 5

query="GRANT SELECT, INSERT, CREATE, DELETE, DROP, SHOW DATABASES, UPDATE ON *.* TO '$USER'@'${HOST}';"

sudo docker exec -it GarracioDB mysql -uroot -p"$ROOT_PASSWORD" -e "$query"

echo '{"senhaMestra": "", "usuarios": []}' > garracio.json
