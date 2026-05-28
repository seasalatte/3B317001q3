@echo off
curl -iss http://127.0.0.1/api/tasks
timeout /t 2 > nul

curl -iss http://127.0.0.1/api/tasks/1
timeout /t 2 > nul

curl -iss -X POST http://127.0.0.1/api/tasks -H "Content-Type: application/json" -d "{\"title\":\"準備考試\",\"description\":\"複習 Flask API\"}"
timeout /t 2 > nul

curl -iss -X PUT http://127.0.0.1/api/tasks/3 -H "Content-Type: application/json" -d "{\"title\":\"準備考試 - 更新\",\"description\":\"加強練習\",\"done\":1}"
timeout /t 2 > nul

curl -iss -X DELETE http://127.0.0.1/api/tasks/3
timeout /t 2 > nul

curl -iss http://127.0.0.1/api/tasks/3
pause