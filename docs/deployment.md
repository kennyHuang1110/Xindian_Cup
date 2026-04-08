# Deployment Draft

## Target

Deploy `xindian-cup` to a Google Cloud Compute Engine VM with:

- Ubuntu LTS
- Python 3.12
- PostgreSQL
- Nginx reverse proxy
- `systemd` for service management
- Let's Encrypt for HTTPS

## Suggested VM bootstrap

```bash
sudo apt update
sudo apt install -y python3.12 python3.12-venv python3-pip postgresql postgresql-contrib nginx certbot python3-certbot-nginx
sudo mkdir -p /opt/xindian-cup
sudo chown $USER:$USER /opt/xindian-cup
```

## App setup

```bash
cd /opt/xindian-cup
git clone <your-repo-url> current
python3.12 -m venv /opt/xindian-cup/venv
source /opt/xindian-cup/venv/bin/activate
pip install --upgrade pip
pip install -r current/requirements.txt
cp current/.env.example /opt/xindian-cup/shared/.env
```

Edit `/opt/xindian-cup/shared/.env` and set real values for database, LINE, SMTP, and app secrets.

## Database setup

```bash
sudo -u postgres psql
CREATE DATABASE xindian_cup;
CREATE USER xindian_cup WITH ENCRYPTED PASSWORD 'change-me';
GRANT ALL PRIVILEGES ON DATABASE xindian_cup TO xindian_cup;
\q
```

Then initialize tables:

```bash
cd /opt/xindian-cup/current
source /opt/xindian-cup/venv/bin/activate
alembic upgrade head
```

## systemd

```bash
sudo cp infra/systemd/xindian-cup.service /etc/systemd/system/xindian-cup.service
sudo systemctl daemon-reload
sudo systemctl enable --now xindian-cup
sudo systemctl status xindian-cup
```

## Nginx + HTTPS

```bash
sudo cp infra/nginx/xindian-cup.conf.example /etc/nginx/sites-available/xindian-cup.conf
sudo ln -s /etc/nginx/sites-available/xindian-cup.conf /etc/nginx/sites-enabled/xindian-cup.conf
sudo nginx -t
sudo systemctl reload nginx
sudo certbot --nginx -d example.com -d www.example.com
```

## Next steps

- Add Alembic migrations.
- Replace MVP session/query handling with real auth middleware.
- Implement SMTP delivery and LINE webhook verification.
- Add admin auth and captain login/session guards.
