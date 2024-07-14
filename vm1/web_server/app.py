# Store this code in 'app.py' file
from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import hashlib


app = Flask(__name__)


app.secret_key = "your secret key"


app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "username"
app.config["MYSQL_PASSWORD"] = "password"
app.config["MYSQL_DB"] = "profileApp"


mysql = MySQL(app)


@app.route("/")
@app.route("/login", methods=["GET", "POST"])
def login():
    msg = ""
    if (
        request.method == "POST"
        and "username" in request.form
        and "password" in request.form
    ):
        username = request.form["username"]

        input_str = request.form["password"]
        hash_object = hashlib.sha256(input_str.encode())
        password_hash = hash_object.hexdigest()

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(
            "SELECT * FROM accounts WHERE username = %s \
			AND password = %s",
            (
                username,
                password_hash,
            ),
        )
        account = cursor.fetchone()
        if account:
            session["loggedin"] = True
            session["id"] = account["id"]
            session["username"] = account["username"]
            msg = "Logged in successfully !"
            return render_template("index.html", msg=msg)
        else:
            cursor.execute("SELECT * FROM accounts WHERE username = %s", (username,))
            account = cursor.fetchone()
            if not account:
                msg = "Incorrect username!"
            else:
                msg = "Incorrect password!"
    return render_template("login.html", msg=msg)


@app.route("/logout")
def logout():

    session.pop("loggedin", None)
    session.pop("id", None)
    session.pop("username", None)
    return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register():
    msg = ""
    if (
        request.method == "POST"
        and "username" in request.form
        and "password" in request.form
        and "email" in request.form
        and "address" in request.form
        and "city" in request.form
        and "country" in request.form
        and "postalcode" in request.form
        and "organization" in request.form
    ):
        username = request.form["username"]

        input_str = request.form["password"]
        hash_object = hashlib.sha256(input_str.encode())
        password_hash = hash_object.hexdigest()

        email = request.form["email"]
        organization = request.form["organization"]
        address = request.form["address"]
        city = request.form["city"]
        state = request.form["state"]
        country = request.form["country"]
        postalcode = request.form["postalcode"]

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM accounts WHERE username = %s", (username,))
        account = cursor.fetchone()

        if account:
            msg = "Account already exists !"

        elif not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            msg = "Invalid email address !"

        elif not re.match(r"[A-Za-z0-9]+", username):
            msg = "name must contain only characters and numbers !"

        else:
            cursor.execute(
                "INSERT INTO accounts VALUES \
			(NULL, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                (
                    username,
                    password_hash,
                    email,
                    organization,
                    address,
                    city,
                    state,
                    country,
                    postalcode,
                ),
            )
            mysql.connection.commit()
            msg = "You have successfully registered !"
            return render_template("login.html", msg=msg)
    elif request.method == "POST":
        msg = "Please fill out the form !"
    return render_template("register.html", msg=msg)


@app.route("/index")
def index():
    if "loggedin" in session:
        return render_template("index.html")
    return redirect(url_for("login"))


@app.route("/display")
def display():
    if "loggedin" in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM accounts WHERE id = %s", (session["id"],))
        account = cursor.fetchone()
        return render_template("display.html", account=account)
    return redirect(url_for("login"))


@app.route("/update", methods=["GET", "POST"])
def update():
    msg = ""
    if "loggedin" in session:
        if (
            request.method == "POST"
            and "username" in request.form
            and "password" in request.form
            and "email" in request.form
            and "address" in request.form
            and "city" in request.form
            and "country" in request.form
            and "postalcode" in request.form
            and "organization" in request.form
        ):
            username = request.form["username"]
            
            input_str = request.form["password"]
            hash_object = hashlib.sha256(input_str.encode())
            password_hash = hash_object.hexdigest()
            
            email = request.form["email"]
            organization = request.form["organization"]
            address = request.form["address"]
            city = request.form["city"]
            state = request.form["state"]
            country = request.form["country"]
            postalcode = request.form["postalcode"]
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            
            account = None
            if session['username'] != username:
                cursor.execute("SELECT * FROM accounts WHERE username = %s", (username,))
                account = cursor.fetchone()
                
            if account:
                msg = "username already exists !"
            elif not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                msg = "Invalid email address !"
            elif not re.match(r"[A-Za-z0-9]+", username):
                msg = "name must contain only characters and numbers !"
            else:
                cursor.execute(
                    "UPDATE accounts SET username =%s,\
				password =%s, email =%s, organization =%s, \
				address =%s, city =%s, state =%s, \
				country =%s, postalcode =%s WHERE id =%s",
                    (
                        username,
                        password_hash,
                        email,
                        organization,
                        address,
                        city,
                        state,
                        country,
                        postalcode,
                        (session["id"],),
                    ),
                )
                session['username'] = username
                mysql.connection.commit()
                msg = "You have successfully updated !"
        elif request.method == "POST":
            msg = "Please fill out the form !"
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM accounts WHERE id = %s", (session["id"],))
        account = cursor.fetchone()
        return render_template("update.html", msg=msg, account=account)
    return redirect(url_for("login"))


@app.route("/home")
def home():
    if "loggedin" in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT username, email FROM accounts")
        accounts = cursor.fetchall()
        return render_template("home.html", accounts=accounts)
    return redirect(url_for("login"))


@app.route("/delete_account")
def delete_account():
    if "loggedin" in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("delete from accounts where id = %s", (session["id"],))
        mysql.connection.commit()
        msg = "account was successfully deleted."
    return render_template("login.html", msg=msg)


if __name__ == "__main__":
    app.run(host="localhost", port=int("5000"),debug=True)
