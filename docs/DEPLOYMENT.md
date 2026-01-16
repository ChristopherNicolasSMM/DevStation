# Guia de Deploy - DevStation

## Deploy Local (Executável .exe)

### Pré-requisitos

- Python 3.11+
- PyInstaller instalado: `pip install PyInstaller`

### Gerar Executável

```bash
# Na raiz do projeto
python setup/build_exe.py
```

O executável será gerado em `dist/DevStation.exe`

### Executar

1. Copie o arquivo `DevStation.exe` para o local desejado
2. Crie um arquivo `.env` na mesma pasta (copie de `src/config.env.modelo`)
3. Execute `DevStation.exe`

## Deploy em VPS (Produção)

### Pré-requisitos

- Servidor Linux (Ubuntu/Debian recomendado)
- Python 3.11+
- PostgreSQL (ou SQLite para desenvolvimento)
- Nginx (opcional, para reverse proxy)
- Gunicorn

### Instalação

1. **Clonar/Copiar projeto para o servidor**

```bash
cd /opt
git clone <repo> devstation
cd devstation
```

2. **Criar ambiente virtual**

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3. **Configurar variáveis de ambiente**

```bash
cp src/config.env.modelo src/.env
nano src/.env
```

Configure:
- `FLASK_ENV=PRD`
- `DATABASE_URL` ou configurações do PostgreSQL
- `SECRET_KEY` (gere uma chave segura)

4. **Inicializar banco de dados**

```bash
cd src
python main.py
# Ou usando Flask CLI
flask init-admin
```

5. **Instalar Gunicorn**

```bash
pip install gunicorn
```

6. **Criar serviço systemd**

Crie `/etc/systemd/system/devstation.service`:

```ini
[Unit]
Description=DevStation Gunicorn daemon
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/opt/devstation/src
Environment="PATH=/opt/devstation/venv/bin"
ExecStart=/opt/devstation/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:5000 main:app

[Install]
WantedBy=multi-user.target
```

7. **Iniciar serviço**

```bash
sudo systemctl daemon-reload
sudo systemctl enable devstation
sudo systemctl start devstation
```

8. **Configurar Nginx (opcional)**

Crie `/etc/nginx/sites-available/devstation`:

```nginx
server {
    listen 80;
    server_name seu-dominio.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Ative o site:

```bash
sudo ln -s /etc/nginx/sites-available/devstation /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## Backup e Restauração

### Backup do Banco de Dados

**SQLite:**
```bash
cp src/instance/devstation.db backup_$(date +%Y%m%d).db
```

**PostgreSQL:**
```bash
pg_dump -U usuario -d devstation > backup_$(date +%Y%m%d).sql
```

### Restauração

**SQLite:**
```bash
cp backup_YYYYMMDD.db src/instance/devstation.db
```

**PostgreSQL:**
```bash
psql -U usuario -d devstation < backup_YYYYMMDD.sql
```

## Monitoramento

### Logs

Logs estão em `logs/` na raiz do projeto.

### Verificar Status

```bash
# Serviço systemd
sudo systemctl status devstation

# Logs
tail -f logs/devstation.log
```

## Atualização

1. Fazer backup do banco de dados
2. Parar serviço: `sudo systemctl stop devstation`
3. Atualizar código
4. Atualizar dependências: `pip install -r requirements.txt`
5. Reiniciar serviço: `sudo systemctl start devstation`
