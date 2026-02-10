
#!/bin/bash
set -e

# 1. Clonar a branch main do repositório em /opt/
cd /opt/
git clone -b main https://github.com/carlos-cabgj/cloudunderroof.git cloudunderroof

# 2. Criar venv no projeto
cd /opt/cloudunderroof
python3 -m venv venv

# 3. Ativar venv
source venv/bin/activate

# 4. Instalar pacotes do requirements.txt
pip install --upgrade pip
pip install -r /opt/cloudunderroof/infra/requirements.txt


#!/bin/bash
set -e

# Atualizar pacotes
sudo apt update

# Instalar PostgreSQL 15
sudo apt install -y postgresql-15

# Garantir que o serviço esteja rodando
sudo systemctl enable postgresql
sudo systemctl start postgresql

# Criar usuário e banco de dados
sudo -u postgres psql <<EOF
-- Criar usuário com senha
CREATE USER cloudUser WITH PASSWORD 'passToChange';

-- Criar banco de dados associado ao usuário
CREATE DATABASE cloudDB OWNER cloudUser;

-- Garantir privilégios
GRANT ALL PRIVILEGES ON DATABASE cloudDB TO cloudUser;
EOF

echo "PostgreSQL 15 instalado, usuário 'cloudUser' criado e banco 'cloudDB' configurado com sucesso!"

sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
 -keyout /etc/apache2/ssl/cloudunderroof.key \
 -out /etc/apache2/ssl/cloudunderroof.crt \
 -subj "/C=BR/ST=State/L=City/O=CloudUnderRoof/CN=192.168.0.42"

#!/bin/bash
set -e

# Caminho base do projeto
APP_DIR="/opt/cloudunderroof/app"

# Arquivo de origem e destino
SOURCE_FILE="$APP_DIR/.env_template"
DEST_FILE="$APP_DIR/.env"

# Copiar o arquivo
cp "$SOURCE_FILE" "$DEST_FILE"

echo "Arquivo .env criado a partir de .env_template em $APP_DIR"


# 5. Substituir termos no arquivo de configuração do Apache
sed -i 's#/tcc-engs/app/#/opt/cloudunderroof#g' /opt/cloudunderroof/infra/config_apache.txt

# 6. Copiar arquivo para sites-available do Apache
sudo cp /opt/cloudunderroof/infra/config_apache.txt /etc/apache2/sites-available/cloudunderroof.conf

# 7. Habilitar o site no Apache
sudo a2ensite cloudunderroof.conf

# 8. Reiniciar o Apache
sudo systemctl restart apache2

echo "Deploy concluído com sucesso!"
