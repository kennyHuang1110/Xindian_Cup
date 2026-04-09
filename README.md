# Xindian_Cup

`Xindian_Cup` 是一個以 FastAPI 為核心的排球賽事網站 MVP，提供公開公告名單、隊長驗證入口、隊員管理、歷屆照片與比賽章程頁面，目標部署環境為 Google Cloud Compute Engine VM。

## 目前已完成

- FastAPI + Jinja2 網站骨架
- `/health` 健康檢查
- 首頁、公告名單、歷屆照片、比賽章程頁
- SQLAlchemy models 與 Alembic 初始 migration
- 管理者建立隊伍 API
- LINE entry 取得隊長 session
- 隊長 Email 驗證流程
- 隊長管理頁新增隊員流程
- 黑名單與 admin token 基本保護
- Nginx / systemd / GCP VM 部署範本

## 目前主要流程

1. 管理者先建立隊伍與隊長資料
2. 隊長透過 `POST /api/auth/line-entry` 取得登入 session
3. 隊長進入 `/captain/manage`
4. 隊長完成 Email 驗證
5. 驗證完成後新增隊員
6. 公開頁 `/public/teams` 顯示已公告隊伍與成員

## 專案結構

```text
app/
  api/
  core/
  models/
  schemas/
  services/
  static/
  templates/
  main.py
docs/
infra/
  nginx/
  systemd/
migrations/
scripts/
tests/
img/
```

## 本機啟動

```bash
python -m venv .venv
source .venv/bin/activate  # Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env     # Windows PowerShell: Copy-Item .env.example .env
alembic upgrade head
uvicorn app.main:app --reload
```

開啟：

- `http://127.0.0.1:8000/`
- `http://127.0.0.1:8000/health`
- `http://127.0.0.1:8000/public/teams`
- `http://127.0.0.1:8000/history/photos`
- `http://127.0.0.1:8000/charter`
- `http://127.0.0.1:8000/docs`

## 測試

```bash
pytest tests
```

目前測試涵蓋：

- 健康檢查與首頁
- admin 建隊流程
- 公告名單頁
- LINE entry 驗證
- 隊長 web flow
- Email 驗證後新增隊員
- 隊長登出

## API 路由

- `GET /health`
- `GET /api/public/teams`
- `GET /api/public/teams/detail`
- `POST /api/auth/line-entry`
- `POST /api/captain/send-email-verification`
- `GET /api/captain/verify-email`
- `GET /api/captain/me`
- `GET /api/captain/members`
- `POST /api/captain/members`
- `POST /api/admin/teams`
- `PATCH /api/admin/teams/{id}`
- `POST /api/admin/blacklist`

## 頁面路由

- `/`
- `/public/teams`
- `/history/photos`
- `/charter`
- `/captain/manage`

## 部署

部署草稿請看：

- [docs/deployment.md](/c:/Users/user/Desktop/Xindian_Cup/docs/deployment.md)

範本檔：

- [infra/nginx/xindian-cup.conf.example](/c:/Users/user/Desktop/Xindian_Cup/infra/nginx/xindian-cup.conf.example)
- [infra/systemd/xindian-cup.service](/c:/Users/user/Desktop/Xindian_Cup/infra/systemd/xindian-cup.service)

## 接下來可再補

- 真正的 LINE Login / LIFF / webhook 驗證
- 真實 SMTP 寄信
- session 撤銷與逾期清理
- rate limit
- 更完整的 audit log 記錄
