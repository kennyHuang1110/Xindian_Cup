Project: Xindian_Cup

請幫我建立一個可部署在 Google Cloud Compute Engine VM（IaaS）的 Python 專案骨架，使用 FastAPI + Jinja2 + PostgreSQL + Nginx + systemd + Let's Encrypt。

需求如下：
1. 專案名稱：
   - 顯示名稱：Xindian_Cup
   - repo / Linux 路徑名稱：xindian-cup

2. 目標功能：
   - LINE 作為主要通知入口
   - 網站提供公告名單頁
   - 隊長可登入後新增隊員
   - 隊員欄位：
     - 姓名（必填）
     - 電話（選填）
     - 是否為新店高中校友（必填，boolean）
   - 隊伍不能自行建立，必須由管理者先建立隊伍與隊長資料
   - 隊長新增名單前必須完成 email 驗證
   - 網站功能頁需檢查入口狀態，未通過驗證者不可使用
   - 站台要預留黑名單機制
   - 後續會部署在 GCP VM 上，Nginx 負責 reverse proxy、redirect、HTTPS

3. 請直接建立完整專案結構：
   - app/
     - main.py
     - api/
     - core/
     - models/
     - schemas/
     - services/
     - templates/
     - static/
   - migrations/
   - scripts/
   - tests/
   - infra/nginx/
   - infra/systemd/
   - docs/
   - requirements.txt
   - .env.example
   - .gitignore
   - README.md

4. 請先實作最小可運作版本：
   - FastAPI app 可啟動
   - /health API
   - 首頁 / 可顯示 Xindian_Cup Running
   - requirements.txt
   - .env.example
   - .gitignore
   - README.md
   - systemd service 範本
   - nginx conf 範本

5. 請規劃資料表與 model：
   - teams
   - members
   - email_verifications
   - sessions
   - blacklists
   - audit_logs

6. teams 欄位至少要有：
   - id
   - team_name
   - captain_name
   - captain_email
   - captain_phone
   - captain_line_user_id
   - status (pending / active / disabled)
   - created_at
   - updated_at

7. members 欄位至少要有：
   - id
   - team_id
   - name
   - phone
   - is_alumni
   - created_by
   - created_at

8. email_verifications 欄位至少要有：
   - id
   - team_id
   - email
   - token_hash
   - expires_at
   - used_at
   - created_at

9. sessions 欄位至少要有：
   - id
   - team_id
   - line_user_id
   - session_token_hash
   - expires_at
   - created_at

10. blacklists 欄位至少要有：
   - id
   - type
   - value
   - reason
   - is_active
   - created_at

11. audit_logs 欄位至少要有：
   - id
   - actor_type
   - actor_id
   - action
   - target_type
   - target_id
   - ip
   - user_agent
   - created_at

12. API 先規劃以下路由：
   - GET /health
   - GET /api/public/teams
   - POST /api/auth/line-entry
   - POST /api/captain/send-email-verification
   - GET /api/captain/verify-email
   - GET /api/captain/me
   - GET /api/captain/members
   - POST /api/captain/members
   - POST /api/admin/teams
   - PATCH /api/admin/teams/{id}
   - POST /api/admin/blacklist

13. 請幫我產出：
   - 初始專案骨架
   - SQLAlchemy model
   - Pydantic schema
   - API router 檔案
   - README
   - deployment 文件草稿
   - nginx 範本
   - systemd 範本

14. 程式風格要求：
   - 結構清楚
   - 每個模組有註解
   - 先以可維護性為主
   - 不要過度設計
   - 先完成 MVP
   - 所有敏感值放進 .env.example
   - Python 使用 FastAPI 慣例結構

15. 請先從「可直接執行的第一版骨架」開始產出，不要只給規劃，直接建立檔案內容。