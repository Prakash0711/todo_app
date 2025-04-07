from flask import Flask, render_template, request, redirect
import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)


def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
    )


@app.route("/test-db")
def test_db():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT DATABASE();")
        db_name = cursor.fetchone()[0]
        conn.close()
        return f"Connected to database: {db_name}"
    except Exception as e:
        return f"Database connection failed: {e}"


@app.route("/")
def index():
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM tasks")
    tasks = cursor.fetchall()
    db.close()
    return render_template("index.html", tasks=tasks)


@app.route("/add", methods=["POST"])
def add():
    content = request.form["content"]
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("INSERT INTO tasks (content) VALUES (%s)", (content,))
    db.commit()
    db.close()
    return redirect("/")


@app.route("/update", methods=["POST"])
def update():
    completed_ids = request.form.getlist(
        "completed"
    )  # https://stackoverflow.com/questions/44600601/get-a-list-of-values-from-checkboxes-using-flask-through-python
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("UPDATE tasks SET completed = FALSE")  # Reset all
    if completed_ids:
        placeholders = ",".join(["%s"] * len(completed_ids))
        query = f"UPDATE tasks SET completed = TRUE WHERE id IN ({placeholders})"
        cursor.execute(query, tuple(completed_ids))
    db.commit()
    db.close()
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)
