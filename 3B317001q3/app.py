import os
import sqlite3
from datetime import datetime
from flask import Flask, jsonify, request

app = Flask(__name__)
app.json.ensure_ascii = False
DB_FILE = "tasks.db"

# 執行 error automatically generated logs/error.log
def write_error_log(message):
    os.makedirs("logs", exist_ok=True)
    try:
        with open("logs/error.log", "a", encoding="utf-8") as f:
            timestamp = datetime.now().isoformat(' ', 'seconds')
            f.write(f"[{timestamp}] {message}\n")
    except PermissionError:
        pass

# connect 到 SQlite DB 
def get_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

# DB row 轉換成 dict，方便 jsonify 使用 
def task_to_dict(row):
    return {
        "id": row["id"],
        "title": row["title"],
        "description": row["description"],
        "done": row["done"],
        "created_at": row["created_at"],
    }

# GET /api/tasks
@app.route("/api/tasks", methods=["GET"])
def get_all_tasks():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tasks")
        rows = cursor.fetchall()
        conn.close()

        tasks_list = [task_to_dict(row) for row in rows]
        return jsonify({"message": "成功取得任務列表", "data": tasks_list}), 200

    except Exception as e:
        write_error_log(f"GET /api/tasks: {str(e)}")
        return jsonify({
            "error": "Internal Server Error",
            "message": "運算過程發生異常"
        }), 500

# GET /api/tasks/<task_id>
@app.route("/api/tasks/<int:task_id>", methods=["GET"])
def get_single_task(task_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
        row = cursor.fetchone()
        conn.close()

        if row is None:
            write_error_log(f"404 Not Found - 找不到 ID 為 {task_id} 的任務")
            return jsonify({
                "error": "Not Found",
                "message": f"找不到 ID 為 {task_id} 的任務"
            }), 404

        return jsonify({"message": "成功取得任務", "data": task_to_dict(row)}), 200

    except Exception as e:
        write_error_log(f"GET /api/tasks/{task_id}: {str(e)}")
        return jsonify({
            "error": "Internal Server Error",
            "message": "運算過程發生異常"
        }), 500

# POST /api/tasks
@app.route("/api/tasks", methods=["POST"])
def create_task():
    data = request.get_json(silent=True)
    if data is None or not str(data.get("title", "")).strip():
        write_error_log("400 Bad Request - 請求內容必須是合法 JSON，且 title 為必填欄位")
        return jsonify({
            "error": "Bad Request",
            "message": "請求內容必須是合法 JSON，且 title 為必填欄位"
        }), 400

    title = data["title"].strip()
    description = data.get("description", "")
    done = data.get("done", 0)

    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO tasks (title, description, done) VALUES (?, ?, ?)",
            (title, description, done),
        )
        conn.commit()
        cursor.execute("SELECT last_insert_rowid()")
        new_id = cursor.fetchone()[0]
        cursor.execute("SELECT * FROM tasks WHERE id = ?", (new_id,))
        row = cursor.fetchone()
        conn.close()

        return jsonify({"message": "任務建立成功", "data": task_to_dict(row)}), 201

    except Exception as e:
        write_error_log(f"POST /api/tasks: {str(e)}")
        return jsonify({
            "error": "Internal Server Error",
            "message": "運算過程發生異常"
        }), 500

# PUT /api/tasks/<task_id>
@app.route("/api/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    data = request.get_json(silent=True)
    if data is None or not str(data.get("title", "")).strip():
        write_error_log("400 Bad Request - 請求內容必須是合法 JSON，且 title 為必填欄位")
        return jsonify({
            "error": "Bad Request",
            "message": "請求內容必須是合法 JSON，且 title 為必填欄位"
        }), 400

    title = data["title"].strip()
    description = data.get("description", "")
    done = data.get("done", 0)

    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM tasks WHERE id = ?", (task_id,))
        if cursor.fetchone() is None:
            conn.close()
            write_error_log(f"404 Not Found - 找不到 ID 為 {task_id} 的任務")
            return jsonify({
                "error": "Not Found",
                "message": f"找不到 ID 為 {task_id} 的任務"
            }), 404

        cursor.execute(
            "UPDATE tasks SET title = ?, description = ?, done = ? WHERE id = ?",
            (title, description, done, task_id),
        )
        conn.commit()
        cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
        row = cursor.fetchone()
        conn.close()

        return jsonify({"message": "任務更新成功", "data": task_to_dict(row)}), 200

    except Exception as e:
        write_error_log(f"PUT /api/tasks/{task_id}: {str(e)}")
        return jsonify({
            "error": "Internal Server Error",
            "message": "運算過程發生異常"
        }), 500

# DELETE /api/tasks/<task_id>
@app.route("/api/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM tasks WHERE id = ?", (task_id,))
        if cursor.fetchone() is None:
            write_error_log(f"404 Not Found - 找不到 ID 為 {task_id} 的任務")
            conn.close()
            return jsonify({
                "error": "Not Found",
                "message": f"找不到 ID 為 {task_id} 的任務"
            }), 404

        cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        conn.commit()
        conn.close()

        return jsonify({"message": f"ID 為 {task_id} 的任務已刪除"}), 200

    except Exception as e:
        write_error_log(f"DELETE /api/tasks/{task_id}: {str(e)}")
        return jsonify({
            "error": "Internal Server Error",
            "message": "運算過程發生異常"
        }), 500

# error 400 處理
@app.errorhandler(400)
def bad_request(error):
    message = getattr(error, 'description', "請求格式錯誤")
    write_error_log(f"400 Bad Request - {message}")
    return jsonify({
        "error": "Bad Request",
        "message": message
    }), 400

# error 404 處理
@app.errorhandler(404)
def not_found(error):
    message = getattr(error, 'description', "請求的資源不存在")
    write_error_log(f"404 Not Found - {message}")
    return jsonify({
        "error": "Not Found",
        "message": message
    }), 404

# error 500 處理
@app.errorhandler(500)
def internal_server_error(error):
    write_error_log(f"500 Internal Server Error - {str(error)}")
    return jsonify({
        "error": "Internal Server Error",
        "message": "運算過程發生異常"
    }), 500