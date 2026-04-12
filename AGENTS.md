Project: Xindian_Cup

請將本專案視為「純靜態資訊網站」。

目前專案定位如下：

1. 專案用途
   - 提供新店盃活動資訊展示
   - 提供公告名單頁
   - 提供報名表下載
   - 提供賽程表與循環圖頁
   - 提供歷屆照片頁
   - 提供比賽章程頁

2. 重要原則
   - 這是靜態網站，只提供顯示功能
   - 不要再新增登入、隊長後台、管理者後台、資料庫編輯流程
   - 不要再設計 captain / admin / email verification / LINE gate 等動態功能
   - 所有資料都由我手動新增與修改
   - 網站只負責把資料顯示出來

3. 資料維護方式
   - 隊伍、隊員、賽程等內容：由我直接修改 `app/data/site_content.json`
   - 章程內容：由我直接修改根目錄 `章程.txt`
   - 報名表檔案：由我直接放在 `app/data/sign.xlsx`
   - 圖片素材：由我直接放在 `img/`

4. 開發方向
   - 以靜態頁面內容與視覺呈現為主
   - 可調整首頁文案、版面、導覽、章程樣式、賽程表呈現、公告名單呈現
   - 可新增純顯示頁面
   - 可新增靜態檔案下載入口
   - 可改善 Render Static Site 輸出流程

5. 不要做的事
   - 不要主動把專案改回動態 Web App
   - 不要主動加入登入驗證
   - 不要主動加入 API 寫入功能
   - 不要主動加入資料庫 CRUD
   - 不要主動加入使用者權限系統
   - 不要主動加入隊長自行編輯名單功能

6. 部署模式
   - 以 Render Static Site 為主
   - 使用 `python scripts/build_static.py` 產生 `dist/`
   - Render 設定：
     - Build Command: `python scripts/build_static.py`
     - Publish Directory: `dist`

7. 專案目標
   - 保持簡單
   - 保持可維護
   - 以靜態展示為核心
   - 所有更新都應優先配合「我手動維護資料，網站負責顯示」
