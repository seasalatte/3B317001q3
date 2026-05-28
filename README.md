# 1142 Web 程式設計 --- 第3次小考
任務管理 RESTful API 實作

## 檔案結構與說明
* `app.py` : 主程式
* `tasks.db` : SQLite 資料庫
* `requirements.txt` : 執行本專案所需的 Python 套件紀錄(用 pip freeze 產生)
* `run.cmd` : 鍵啟動伺服器的快捷腳本
* `test.cmd` : 測試腳本

## 執行操作步驟

1. 開 cmd 切換到你想存放專案的資料夾目錄, 然後執行 git clone <br>
`git clone https://github.com/seasalatte/3B317001q3.git`
2. 切換進入該專案資料夾, 建立虛擬環境 <br>
`python -m venv env` <br>
`venv\Scripts\activate`
3. 安裝必要套件 <br>
(env) `pip install -r requirements.txt`
4. 啟動伺服器, 一定要在虛擬環境執行 <br>
(env) `run.cm`
5. 到瀏覽器, 輸入 http://127.0.0.1/api/tasks 或 http:// <<你的IP>> /api/tasks, 顯示如下: <br>
{ <br>
"data": [ <br>
{ <br>
"created_at": "2026-05-28 14:01:21", <br>
"description": "牛奶、麵包、雞蛋", <br>
"done": 0, <br>
"id": 1, <br>
"title": "買雜貨" <br>
}, <br>
{ <br>
"created_at": "2026-05-28 14:01:21", <br>
"description": "完成資訊小考", <br>
"done": 1, <br>
"id": 2, <br>
"title": "寫作業" <br>
} <br>
], <br>
"message": "成功取得任務列表" <br>
} <br>
6. Optional: 執行測試腳本 test.cmd <br>
(env) `test.cmd` <br>
**當 API 運行遇到任何錯誤（例如：使用者輸入不存在的網址、或是測試腳本請求不存在的任務 ID）時，系統會自動在後端生成 error.log 紀錄，並格式化輸出錯誤時間與原因，不需手動建立**
