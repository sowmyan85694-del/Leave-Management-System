import os
import sqlite3
from functools import wraps

from flask import (
    Flask, render_template, request,
    redirect, session, url_for
)

app = Flask(__name__)

# Application settings
app.secret_key = "employee-leave-portal-secret-key"

# Use one database file for employee and manager pages
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, "leaves.db")

# Manager login credentials
MANAGER_USERNAME = "Khushi"
MANAGER_PASSWORD = "Devru@123"


# Connect to the database
def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# Create the database table if it does not exist
def init_db():
    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS leaves (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            leave_type TEXT NOT NULL,
            from_date TEXT NOT NULL,
            to_date TEXT NOT NULL,
            reason TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Pending'
        )
    """)

    conn.commit()
    conn.close()


# Check manager login
def manager_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if not session.get("manager_logged_in"):
            return redirect(url_for("manager"))
        return view(*args, **kwargs)

    return wrapped_view


# Employee home page
@app.route("/")
def home():
    conn = get_db()
    leaves = conn.execute(
        "SELECT * FROM leaves ORDER BY id DESC"
    ).fetchall()
    conn.close()

    return render_template("index.html", leaves=leaves)


# Employee submits a leave application
@app.route("/apply", methods=["POST"])
def apply_leave():
    name = request.form.get("name", "").strip()
    leave_type = request.form.get("leave_type", "").strip()
    from_date = request.form.get("from_date", "").strip()
    to_date = request.form.get("to_date", "").strip()
    reason = request.form.get("reason", "").strip()

    if not all([name, leave_type, from_date, to_date, reason]):
        return "Please fill in all fields.", 400

    if to_date < from_date:
        return "To date cannot be earlier than from date.", 400

    conn = get_db()
    conn.execute("""
        INSERT INTO leaves
        (name, leave_type, from_date, to_date, reason, status)
        VALUES (?, ?, ?, ?, ?, 'Pending')
    """, (name, leave_type, from_date, to_date, reason))

    conn.commit()
    conn.close()

    return redirect(url_for("home"))


# Manager login and leave application list
@app.route("/manager", methods=["GET", "POST"])
def manager():
    error = ""

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if (
            username == MANAGER_USERNAME
            and password == MANAGER_PASSWORD
        ):
            session["manager_logged_in"] = True
            return redirect(url_for("manager"))

        error = "Incorrect manager username or password."

    if session.get("manager_logged_in"):
        conn = get_db()
        leaves = conn.execute(
            "SELECT * FROM leaves ORDER BY id DESC"
        ).fetchall()
        conn.close()

        print("Leave applications found:", len(leaves))

        return render_template(
            "manager.html",
            logged_in=True,
            leaves=leaves,
            error=""
        )

    return render_template(
        "manager.html",
        logged_in=False,
        leaves=[],
        error=error
    )


# Manager approves or rejects an application
@app.route("/manager/update", methods=["POST"])
@manager_required
def update_leave():
    leave_id = request.form.get("leave_id", type=int)
    new_status = request.form.get("status", "")

    if leave_id is None or new_status not in ["Approved", "Rejected"]:
        return "Invalid leave application or status.", 400

    conn = get_db()

    result = conn.execute("""
        UPDATE leaves
        SET status = ?
        WHERE id = ?
    """, (new_status, leave_id))

    conn.commit()
    updated = result.rowcount
    conn.close()

    if updated == 0:
        return "Leave application not found.", 404

    return redirect(url_for("manager"))


# Manager logout
@app.route("/logout")
def logout():
    session.pop("manager_logged_in", None)
    return redirect(url_for("manager"))


# Start the application
if __name__ == "__main__":
    init_db()
    app.run(debug=True)
