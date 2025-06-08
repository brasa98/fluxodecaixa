@echo off
setlocal

rem --- Entrada de Dados ---
echo.
echo ✏️ Digite o nome do banco de dados:
set /p "BD="

echo ✏️ Digite o nome do usuário:
set /p "USER="

rem --- Usando VBScript para entrada oculta (senhas) ou para prompt customizado (host) ---

rem Cria um VBScript temporário para obter o host
echo WScript.StdOut.Write(InputBox("🔗 Digite o host:", "Entrada de Dados", "localhost")) > "%TEMP%\getInputHost.vbs"
for /f "usebackq delims=" %%i in (`cscript //nologo "%TEMP%\getInputHost.vbs"`) do set "HOST=%%i"
del "%TEMP%\getInputHost.vbs"

echo.

rem Cria um VBScript temporário para obter a senha do usuário (entrada oculta)
rem O último '1' no InputBox é para ocultar a entrada.
echo WScript.StdOut.Write(InputBox("🔒 Digite a senha do usuário:", "Entrada de Senha", "", 0, 0, 1)) > "%TEMP%\getHiddenInput.vbs"
for /f "usebackq delims=" %%i in (`cscript //nologo "%TEMP%\getHiddenInput.vbs"`) do set "PASSWORD=%%i"
del "%TEMP%\getHiddenInput.vbs"

echo.

rem Reusa o VBScript temporário para obter a senha root (entrada oculta)
echo WScript.StdOut.Write(InputBox("🔒 Digite a senha root:", "Entrada de Senha", "", 0, 0, 1)) > "%TEMP%\getHiddenInput.vbs"
for /f "usebackq delims=" %%i in (`cscript //nologo "%TEMP%\getHiddenInput.vbs"`) do set "ROOT_PASSWORD=%%i"
del "%TEMP%\getHiddenInput.vbs"

echo.

rem --- Geração do arquivo .env ---
rem Note: No CMD, o echo adiciona uma nova linha automaticamente, então concatenamos as strings.
(
  echo USER=%USER%
  echo PASSWORD=%PASSWORD%
  echo HOST=%HOST%
) > .env

echo Arquivo .env gerado.

rem --- Iniciar o container Docker ---
rem 'sudo' é removido, pois não é um comando do Windows.
echo Iniciando container Docker 'GarracioDB'...
docker run -d --name GarracioDB ^
  -e MYSQL_DATABASE="%BD%" ^
  -e MYSQL_USER="%USER%" ^
  -e MYSQL_PASSWORD="%PASSWORD%" ^
  -e MYSQL_ROOT_PASSWORD="%ROOT_PASSWORD%" ^
  -p 3306:3306 ^
  -v my-db:/var/lib/mysql ^
  --restart always ^
  mysql:8.2

if %ERRORLEVEL% NEQ 0 (
  echo Erro ao iniciar o container Docker. Verifique se o Docker está em execução e se não há containers com o nome GarracioDB.
  pause
  exit /b %ERRORLEVEL%
)

echo "Esperando 5 segundos para o banco de dados inicializar..."
timeout /t 5 /nobreak > nul

rem --- Executar o comando GRANT no Docker ---
set "QUERY=GRANT SELECT, INSERT, CREATE, DELETE, DROP, SHOW DATABASES, UPDATE ON *.* TO '%USER%'@'%HOST%';"

echo Executando comando GRANT no container Docker...
docker exec -it GarracioDB mysql -uroot -p"%ROOT_PASSWORD%" -e "%QUERY%"

if %ERRORLEVEL% NEQ 0 (
  echo Erro ao executar o comando GRANT. Verifique a senha root e as permissões.
  pause
  exit /b %ERRORLEVEL%
)

rem --- Criar arquivo garracio.json ---
echo Criando garracio.json...
echo {"senhaMestra": "", "usuarios": []} > garracio.json

rem --- Instalar dependências Python ---
echo Instalando dependências Python (requirements.txt)...
pip install -r requirements.txt

echo.
echo Script finalizado!
pause

