# Xindian_Cup

`Xindian_Cup` 是一個以 FastAPI + Jinja2 建立的靜態賽事資訊網站，提供：

- LINE gate 入口
- 公告名單頁
- 比賽循環圖與賽程表頁
- 歷屆照片頁
- 比賽章程頁

目前這個版本不再讓隊長直接在網站上維護資料，而是由主辦自行整理後，直接修改站內靜態資料檔。

## 目前網站模式

- 只有通過 LINE 登入入口的人可以查看網站內容
- 隊伍名稱、隊長、隊員名單由主辦手動更新
- 公告名單、賽程表、章程與歷屆照片都以靜態頁呈現
- 適合部署在 GCP VM 上，由 Nginx 反向代理 FastAPI

## 主要頁面

- `/line/login`：LINE gate 入口
- `/`：首頁
- `/public/teams`：公告名單
- `/schedule`：比賽循環圖與賽程表
- `/history/photos`：歷屆照片
- `/charter`：比賽章程
- `/health`：健康檢查

## 靜態資料位置

網站主要內容由這份檔案控制：

- [app/data/site_content.json](/c:/Users/user/Desktop/Xindian_Cup/app/data/site_content.json)

你可以在這裡修改：

- 首頁主標與說明
- 隊伍名稱
- 隊長姓名
- 隊員名單
- 是否為校友
- 分組循環資訊
- 賽程表

比賽章程則來自：

- [章程.txt](/c:/Users/user/Desktop/Xindian_Cup/章程.txt)

## LINE gate 設定

`.env` / `.env.example` 目前支援：

```env
LINE_LOGIN_ALLOWED_IDS=
```

說明：

- 若留空，測試環境中任何非空白 `line_user_id` 都可以登入
- 若填入多個值，用逗號分隔
- 只有名單內的 `line_user_id` 可以進站

例如：

```env
LINE_LOGIN_ALLOWED_IDS=U123456789,U987654321
```

## 本機啟動

```bash
python -m venv .venv
source .venv/bin/activate  # Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env     # Windows PowerShell: Copy-Item .env.example .env
uvicorn app.main:app --reload
```

開啟：

- `http://127.0.0.1:8000/line/login`
- `http://127.0.0.1:8000/`
- `http://127.0.0.1:8000/public/teams`
- `http://127.0.0.1:8000/schedule`
- `http://127.0.0.1:8000/history/photos`
- `http://127.0.0.1:8000/charter`
- `http://127.0.0.1:8000/docs`

## 測試

```bash
pytest tests
```

目前測試涵蓋：

- `/health`
- 未登入時會被導到 `/line/login`
- LINE gate 登入 / 登出
- 公告名單頁
- 賽程表頁
- 歷屆照片頁
- 章程頁
- 靜態 API 回傳內容

## 專案結構

```text
app/
  api/
  core/
  data/
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

## API 路由

- `GET /health`
- `GET /api/public/teams`
- `GET /api/public/teams/detail`
- `POST /api/auth/line-entry`

## 部署

部署草稿請看：

- [docs/deployment.md](/c:/Users/user/Desktop/Xindian_Cup/docs/deployment.md)

範本檔：

- [infra/nginx/xindian-cup.conf.example](/c:/Users/user/Desktop/Xindian_Cup/infra/nginx/xindian-cup.conf.example)
- [infra/systemd/xindian-cup.service](/c:/Users/user/Desktop/Xindian_Cup/infra/systemd/xindian-cup.service)

## 後續可再接

- 正式 LINE Login / LIFF
- 更完整的 allowlist / 權限控管
- 後台資料編輯介面
- 賽程匯入與更動紀錄
