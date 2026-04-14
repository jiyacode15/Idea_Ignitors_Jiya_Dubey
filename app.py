from flask import Flask, request, render_template, redirect, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "secret123"

# ---------------- DB PATH ---------------- #

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database.db")

# ---------------- DB ---------------- #

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fullname TEXT,
        dob TEXT,
        age INTEGER,
        education TEXT,
        username TEXT UNIQUE,
        email TEXT,
        password TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS applications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        income REAL,
        loan REAL,
        age INTEGER,
        employment TEXT,
        credit_history INTEGER,
        status TEXT DEFAULT 'Pending'
    )
    """)

    conn.commit()
    conn.close()

init_db()

# ---------------- HOME ---------------- #

@app.route("/")
def home():
    return render_template("home.html")

# ---------------- LOGIN ---------------- #

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            session["user"] = username
            return redirect("/user-form")
        else:
            return render_template("login.html", error="Invalid credentials")

    return render_template("login.html")

# ---------------- SIGNUP ---------------- #

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        conn = get_db()
        cursor = conn.cursor()

        try:
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
        except:
            return render_template("signup.html", error="User already exists")

        conn.close()
        return redirect("/login")

    return render_template("signup.html")

# ---------------- USER FORM ---------------- #

@app.route("/user-form")
def user_form():
    if "user" not in session:
        return redirect("/login")
    return render_template("user_form.html")

# ---------------- SUBMIT FORM ---------------- #

@app.route("/submit-form", methods=["POST"])
def submit_form():
    if "user" not in session:
        return redirect("/login")

    income = request.form.get("income")
    loan = request.form.get("loan")

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO applications (username, income, loan, status) VALUES (?, ?, ?, 'Pending')",
        (session["user"], income, loan)
    )

    conn.commit()
    conn.close()

    return redirect("/dashboard")

# ---------------- DASHBOARD ---------------- #

@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/login")

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM applications WHERE username=?", (session["user"],))
    data = cursor.fetchall()
    conn.close()

    return render_template("dashboard.html", data=data)

# ---------------- ADMIN ---------------- #

@app.route("/admin", methods=["GET", "POST"])
def admin():
    if request.method == "POST":
        if request.form.get("username") == "admin" and request.form.get("password") == "admin123":
            session["admin"] = True
            return redirect("/admin-dashboard")
        else:
            return render_template("admin.html", error="Invalid credentials")

    return render_template("admin.html")

# ---------------- ADMIN DASHBOARD ---------------- #

@app.route("/admin-dashboard")
def admin_dashboard():
    if "admin" not in session:
        return redirect("/admin")

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM applications")
    data = cursor.fetchall()
    conn.close()

    return render_template("admin_dashboard.html", data=data)

# ---------------- VIEW APPLICATION ---------------- #

@app.route("/view/<int:id>")
def view_application(id):
    if "admin" not in session:
        return redirect("/admin")

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM applications WHERE id=?", (id,))
    data = cursor.fetchone()
    conn.close()

    return render_template("view_application.html", data=data)

# ---------------- LOGOUT ---------------- #

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/")

@app.route("/admin-logout")
def admin_logout():
    session.pop("admin", None)
    return redirect("/")

# ---------------- RUN ---------------- #

if __name__ == "__main__":
    app.run(debug=True)