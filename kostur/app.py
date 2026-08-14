import os
import psycopg2
import psycopg2.extras
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)


def get_connection():
    """
    Connect to a Databricks Lakebase (managed Postgres) instance.
    Set these as environment variables (locally in a .env, or as
    Databricks App resources/secrets when deployed):

      PGHOST     - Lakebase instance hostname
      PGPORT     - usually 5432
      PGDATABASE - database name
      PGUSER     - Databricks user / service principal
      PGPASSWORD - OAuth token or password, depending on auth method
      PGSSLMODE  - "require" (Lakebase requires SSL)
    """
    return psycopg2.connect(
        host=os.environ["PGHOST"],
        port=os.environ.get("PGPORT", "5432"),
        dbname=os.environ["PGDATABASE"],
        user=os.environ["PGUSER"],
        password=os.environ["PGPASSWORD"],
        sslmode=os.environ.get("PGSSLMODE", "require"),
    )


def init_db():
    """Create the todos table if it doesn't exist yet."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS todos (
                    id SERIAL PRIMARY KEY,
                    task TEXT NOT NULL,
                    is_done BOOLEAN NOT NULL DEFAULT FALSE,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
                );
                """
            )
        conn.commit()
    finally:
        conn.close()


@app.route("/")
def index():
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("SELECT * FROM todos ORDER BY is_done ASC, created_at DESC;")
            todos = cur.fetchall()
    finally:
        conn.close()
    return render_template("index.html", todos=todos)


@app.route("/add", methods=["POST"])
def add():
    task = request.form.get("task", "").strip()
    if task:
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("INSERT INTO todos (task) VALUES (%s);", (task,))
            conn.commit()
        finally:
            conn.close()
    return redirect(url_for("index"))


@app.route("/toggle/<int:todo_id>", methods=["POST"])
def toggle(todo_id):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE todos SET is_done = NOT is_done WHERE id = %s;", (todo_id,)
            )
        conn.commit()
    finally:
        conn.close()
    return redirect(url_for("index"))


@app.route("/delete/<int:todo_id>", methods=["POST"])
def delete(todo_id):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM todos WHERE id = %s;", (todo_id,))
        conn.commit()
    finally:
        conn.close()
    return redirect(url_for("index"))


if __name__ == "__main__":
    init_db()
    # Databricks Apps sets PORT for you; 8000 is a safe local default.
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)), debug=True)
