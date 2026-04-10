# Xindian_Cup

`Xindian_Cup` 是一個以 FastAPI + Jinja2 維護、可輸出成純靜態網站的賽事資訊平台。

目前網站不做登入，也不提供隊長或管理者線上編輯功能。隊伍、隊員、賽程等資料由主辦自行整理後，更新靜態資料檔再重新部署。

## 主要頁面

- `/`：首頁
- `/public/teams`：公告名單
- `/schedule`：比賽循環圖與賽程表
- `/history/photos`：歷屆照片
- `/charter`：比賽章程
- `/health`：健康檢查，FastAPI 模式使用

## 靜態資料位置

主要內容由這份檔案控制：

- [app/data/site_content.json](/c:/Users/user/Desktop/Xindian_Cup/app/data/site_content.json)

可在這裡修改：

- 首頁主標與說明
- 隊伍名稱
- 隊長姓名
- 隊員名單
- 是否為校友
- 分組循環資訊
- 賽程表

比賽章程來自：

- [章程.txt](/c:/Users/user/Desktop/Xindian_Cup/章程.txt)

## Render Static Site 部署

在 Render 建立 `Static Site`，設定：

```text
Build Command:
python scripts/build_static.py
```

```text
Publish Directory:
dist
```

建置後會輸出：

```text
dist/
  index.html
  public/teams/index.html
  schedule/index.html
  history/photos/index.html
  charter/index.html
  static/
  gallery/
```

## 本機產生靜態站

```bash
python scripts/build_static.py
```

產物會在：

```text
dist/
```

## FastAPI 本機預覽

如果仍想用 FastAPI 預覽：

```bash
python -m venv .venv
source .venv/bin/activate  # Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

開啟：

- `http://127.0.0.1:8000/`
- `http://127.0.0.1:8000/public/teams`
- `http://127.0.0.1:8000/schedule`
- `http://127.0.0.1:8000/history/photos`
- `http://127.0.0.1:8000/charter`

## 測試

```bash
pytest tests
```

目前測試涵蓋：

- `/health`
- 首頁
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
  services/
  static/
  templates/
  main.py
img/
scripts/
tests/
```
