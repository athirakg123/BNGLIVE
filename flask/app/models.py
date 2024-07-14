from flask import Flask
from flask_mysqldb import MySQL

app = Flask(__name__)
app.config.from_object('config.Config')

mysql = MySQL(app)

def get_user_by_username(username):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM users WHERE username = %s", [username])
    user = cur.fetchone()
    cur.close()
    return user

def get_user_by_email(email):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM users WHERE email = %s", [email])
    user = cur.fetchone()
    cur.close()
    return user

def add_user(username, email, password):
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)", (username, email, password))
    mysql.connection.commit()
    cur.close()
