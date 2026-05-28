import os
import sqlite3
from datetime import datetime
from flask import Flask, jsonify, request

app = Flask(__name__)
app.json.ensure_ascii = False

DB_FILE = "tasks.db"
LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "error.log")

def get_db_connection():
    """Establishes a connection to the SQLite database with row factory enabled."""
    conn = sqlite3.connect(DB_FILE)
    # Allows fetching query results by column names
    conn.row_factory = sqlite3.Row
    return conn

def write_error_log(message):
    """Safely handles directory creation and appends timestamped logs."""
    try:
        if not os.path.exists(LOG_DIR):
            os.makedirs(LOG_DIR)

        timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"{timestamp} {message}\n")
    except PermissionError:
        # Catch PermissionError quietly to avoid crashing the whole API server
        pass
# 1. GET /api/tasks - Retrieve all tasks
@app.route("/api/tasks", methods=["GET"])
def get_all_tasks():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tasks")
        rows = cursor.fetchall()
        conn.close()
        # Convert sqlite3.Row objects into dictionaries
        tasks_list = []
        for row in rows:
            tasks_list.append({
                "id": row["id"],
                "title": row["title"],
                "description": row["description"],
                "done": row["done"],
                "created_at": row["created_at"]
            })

        return jsonify({
            "message": "成功取得任務列表",
            "data": tasks_list
        }), 200

    except Exception as e:
        write_error_log(f"Database error in GET /api/tasks: {str(e)}")
        return jsonify({"error": "Internal Server Error", "message": "伺服器處理失敗，請稍後再試"}), 500
# 2. GET /api/tasks/<int:task_id> - Retrieve a single task by ID
@app.route("/api/tasks/<int:task_id>", methods=["GET"])
def get_task(task_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
        row = cursor.fetchone()
        conn.close()

        if row is None:
            return jsonify({"error": "Not Found", "message": f"找不到 ID 為 {task_id} 的任務"}), 404

        task_data = {
            "id": row["id"],
            "title": row["title"],
            "description": row["description"],
            "done": row["done"],
            "created_at": row["created_at"]
        }
        return jsonify(task_data), 200

    except Exception as e:
        write_error_log(f"Database error in GET /api/tasks/{task_id}: {str(e)}")
        return jsonify({"error": "Internal Server Error", "message": "伺服器處理失敗，請稍後再試"}), 500
# 3. POST /api/tasks - Create a new task
@app.route("/api/tasks", methods=["POST"])
def create_task():
    try:
        # Extract payload safely
        data = request.get_json(silent=True)

        # Validate incoming JSON format and required field
        if data is None or "title" not in data or not data["title"].strip():
            return jsonify({
                "error": "Bad Request",
                "message": "請求內容必須是合法 JSON，且 title 為必填欄位"
            }), 400

        title = data["title"]
        description = data.get("description", "")
        done = data.get("done", 0)

        conn = get_db_connection()
        cursor = conn.cursor()
        # Parameterized query placement (?) to stop SQL injection
        cursor.execute(
            "INSERT INTO tasks (title, description, done) VALUES (?, ?, ?)",
            (title, description, done)
        )
        conn.commit()
        new_id = cursor.lastrowid
        # Fetch the newly created task to return back full details
        cursor.execute("SELECT * FROM tasks WHERE id = ?", (new_id,))
        row = cursor.fetchone()
        conn.close()

        task_data = {
            "id": row["id"],
            "title": row["title"],
            "description": row["description"],
            "done": row["done"],
            "created_at": row["created_at"]
        }

        return jsonify({
            "message": "任務建立成功",
            "data": task_data
        }), 201

    except Exception as e:
        write_error_log(f"Database error in POST /api/tasks: {str(e)}")
        return jsonify({"error": "Internal Server Error", "message": "伺服器處理失敗，請稍後再試"}), 500
# 4. PUT /api/tasks/<int:task_id> - Full update of a task
@app.route("/api/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    try:
        data = request.get_json(silent=True)

        if data is None or "title" not in data or not data["title"].strip():
            return jsonify({"error": "Bad Request", "message": "資料驗證失敗，title 為必填欄位"}), 400

        conn = get_db_connection()
        cursor = conn.cursor()
        # Check if resource exists
        cursor.execute("SELECT id FROM tasks WHERE id = ?", (task_id,))
        if cursor.fetchone() is None:
            conn.close()
            return jsonify({"error": "Not Found", "message": f"找不到 ID 為 {task_id} 的任務"}), 404

        title = data["title"]
        description = data.get("description", "")
        done = data.get("done", 0)
        # Full substitution update syntax
        cursor.execute(
            "UPDATE tasks SET title = ?, description = ?, done = ? WHERE id = ?",
            (title, description, done, task_id)
        )
        conn.commit()
        # Fetch updated record
        cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
        row = cursor.fetchone()
        conn.close()

        updated_data = {
            "id": row["id"],
            "title": row["title"],
            "description": row["description"],
            "done": row["done"],
            "created_at": row["created_at"]
        }
        return jsonify(updated_data), 200

    except Exception as e:
        write_error_log(f"Database error in PUT /api/tasks/{task_id}: {str(e)}")
        return jsonify({"error": "Internal Server Error", "message": "伺服器處理失敗，請稍後再試"}), 500
# 5. DELETE /api/tasks/<int:task_id> - Remove a task
@app.route("/api/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        # Check if resource exists
        cursor.execute("SELECT id FROM tasks WHERE id = ?", (task_id,))
        if cursor.fetchone() is None:
            conn.close()
            return jsonify({"error": "Not Found", "message": f"找不到 ID 為 {task_id} 的任務"}), 404

        cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        conn.commit()
        conn.close()

        return jsonify({
            "message": f"ID 為 {task_id} 的任務已刪除"
        }), 200

    except Exception as e:
        write_error_log(f"Database error in DELETE /api/tasks/{task_id}: {str(e)}")
        return jsonify({"error": "Internal Server Error", "message": "伺服器處理失敗，請稍後再試"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)