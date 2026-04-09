# Deployment Draft

## 目標環境

將 `xindian-cup` 部署到 Google Cloud Compute Engine VM，使用：

- Ubuntu LTS
- Python 3
- PostgreSQL
- Nginx reverse proxy
- `systemd`
- Let's Encrypt

## 建議安裝套件

```bash
sudo apt update
sudo apt install -y git python3 python3-venv python3-pip postgresql postgresql-contrib nginx certbot python3-certbot-nginx
```

## 抓專案與建立虛擬環境

```bash
cd /opt
sudo git clone <your-repo-url> xindian-cup
sudo chown -R $USER:$USER /opt/xindian-cup
cd /opt/xindian-cup
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

## 設定環境變數

```bash
cp .env.example .env
```

至少確認：

- `DATABASE_URL`
- `APP_SECRET_KEY`
- `ADMIN_API_TOKEN`
- `APP_BASE_URL`
- `LINE_CHANNEL_ACCESS_TOKEN`
- `LINE_CHANNEL_SECRET`
- `SMTP_*`

## 建立資料庫

```bash
sudo -u postgres psql
```

```sql
CREATE USER xindian_cup WITH PASSWORD 'change-me';
CREATE DATABASE xindian_cup OWNER xindian_cup;
\q
```

## 執行 migration

```bash
cd /opt/xindian-cup
source .venv/bin/activate
alembic upgrade head
```

## 本機測試啟動

```bash
uvicorn app.main:app --host 127.0.0.1 --port 8000
curl http://127.0.0.1:8000/health
```

## systemd

```bash
sudo cp infra/systemd/xindian-cup.service /etc/systemd/system/xindian-cup.service
sudo systemctl daemon-reload
sudo systemctl enable xindian-cup
sudo systemctl start xindian-cup
sudo systemctl status xindian-cup
```

## Nginx

```bash
sudo cp infra/nginx/xindian-cup.conf.example /etc/nginx/sites-available/xindian-cup
sudo ln -sf /etc/nginx/sites-available/xindian-cup /etc/nginx/sites-enabled/xindian-cup
sudo nginx -t
sudo systemctl reload nginx
```

## HTTPS

```bash
sudo certbot --nginx -d your-domain.example
```

## 部署後驗證

```bash
curl http://127.0.0.1:8000/health
curl https://your-domain.example/health
```

## 目前部署版本注意事項

- LINE 入口仍是 MVP 驗證流程，尚未接正式 LINE Login
- Email 驗證在測試流程中會提供 preview link，正式環境應改為實際寄信
- Nginx 負責 HTTPS、redirect 與 reverse proxy
