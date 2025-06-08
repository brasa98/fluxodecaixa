# Script GarracioDB para PowerShell

# --- Entrada de Dados ---
Write-Host "" # Newline
$BD = Read-Host -Prompt "✏️ Digite o nome do banco de dados"
$USER = Read-Host -Prompt "✏️ Digite o nome do usuário"

Write-Host "" # Newline
$HOST = Read-Host -Prompt "🔗 Digite o host"

# Oculta a entrada da senha usando -AsSecureString
# IMPORTANTE: A entrada será completamente oculta (não mostrará asteriscos ou caracteres).
# As senhas são armazenadas como objetos SecureString para maior segurança.
$PASSWORD_SECURE = Read-Host -Prompt "🔒 Digite a senha do usuário" -AsSecureString
Write-Host "" # Newline

$ROOT_PASSWORD_SECURE = Read-Host -Prompt "🔒 Digite a senha root" -AsSecureString
Write-Host "" # Newline

# --- Geração do arquivo .env ---
Write-Host "Gerando arquivo .env..."

# Para usar as senhas com o Docker, que espera texto plano, precisamos convertê-las
# AVISO DE SEGURANÇA: Esta conversão expõe a senha em texto plano na memória por um curto período.
# Use com cautela e apenas quando necessário para ferramentas externas que não aceitam SecureString.
$PLAIN_PASSWORD = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto([System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($PASSWORD_SECURE))
$PLAIN_ROOT_PASSWORD = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto([System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($ROOT_PASSWORD_SECURE))

# O conteúdo do arquivo .env
$envContent = @"
USER=$USER
PASSWORD=$($PLAIN_PASSWORD)
HOST=$HOST
"@

# Salva o conteúdo no arquivo .env
$envContent | Set-Content -Path ".env" -Encoding UTF8

Write-Host "Arquivo .env gerado."

# --- Iniciar o container Docker ---
Write-Host "Iniciando container Docker 'GarracioDB'..."

try {
    docker run -d --name GarracioDB `
      -e MYSQL_DATABASE="$BD" `
      -e MYSQL_USER="$USER" `
      -e MYSQL_PASSWORD="$PLAIN_PASSWORD" `
      -e MYSQL_ROOT_PASSWORD="$PLAIN_ROOT_PASSWORD" `
      -p 3306:3306 `
      -v my-db:/var/lib/mysql `
      --restart always `
      mysql:8.2

    # Verifica o último código de saída do Docker. No PowerShell, isso é $LASTEXITCODE.
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Erro ao iniciar o container Docker. Verifique se o Docker está em execução e se não há containers com o nome GarracioDB."
        exit $LASTEXITCODE
    }
}
catch {
    Write-Error "Ocorreu um erro ao tentar executar o comando docker run: $($_.Exception.Message)"
    exit 1
}


Write-Host "Esperando 5 segundos para o banco de dados inicializar..."
Start-Sleep -Seconds 5

# --- Executar o comando GRANT no Docker ---
# Definindo a query usando um 'here-string' para facilitar a leitura de múltiplas linhas
$query = @"
GRANT SELECT, INSERT, CREATE, DELETE, DROP, SHOW DATABASES, UPDATE ON *.* TO '$USER'@'${HOST}';
"@

Write-Host "Executando comando GRANT no container Docker..."
try {
    docker exec -it GarracioDB mysql -uroot -p"$($PLAIN_ROOT_PASSWORD)" -e "$query"

    if ($LASTEXITCODE -ne 0) {
        Write-Error "Erro ao executar o comando GRANT. Verifique a senha root e as permissões."
        exit $LASTEXITCODE
    }
}
catch {
    Write-Error "Ocorreu um erro ao tentar executar o comando docker exec: $($_.Exception.Message)"
    exit 1
}

# --- Criar arquivo garracio.json ---
Write-Host "Criando garracio.json..."
'{"senhaMestra": "", "usuarios": []}' | Set-Content -Path "garracio.json" -Encoding UTF8

# --- Instalar dependências Python ---
Write-Host "Instalando dependências Python (requirements.txt)..."
# Garante que pip esteja no PATH e seja executável
try {
    pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Erro ao instalar dependências Python. Verifique se o pip está instalado e acessível."
        exit $LASTEXITCODE
    }
}
catch {
    Write-Error "Ocorreu um erro ao tentar executar o comando pip: $($_.Exception.Message)"
    exit 1
}

Write-Host "" # Newline
Write-Host "Script finalizado!"

# Limpa as senhas em texto plano da memória (tentativa, não garante 100%)
$PLAIN_PASSWORD = $null
$PLAIN_ROOT_PASSWORD = $null
[System.GC]::Collect()

