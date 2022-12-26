#!/usr/bin/python
# -*- coding: utf-8 -*-

# import flask dependencies for web GUI
from flask import Flask, render_template, flash, redirect, url_for, session, request, logging
from passlib.hash import sha256_crypt
from flask_mysqldb import MySQL
from functools import wraps

# import other functions and classes
from sqlhelpers import *
from forms import *

# other dependencies
import time
import socket
import threading
import json
import os

# initialize the app
app = Flask(__name__)

# configure mysql
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Hwangzh@1234'
app.config['MYSQL_DB'] = 'crypto'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

# initialize mysql
mysql = MySQL(app)


# wrap to define if the user is currently logged in from session
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash("Unauthorized, please login.", "danger")
            return redirect(url_for('login'))

    return wrap


# log in the user by updating session
def log_in_user(username):
    users = Table("users", "name", "email", "username", "password")
    user = users.getone("username", username)

    session['logged_in'] = True
    session['username'] = username
    session['name'] = user.get('name')
    session['email'] = user.get('email')


# Registration page
@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    users = Table("users", "name", "email", "username", "password")

    # if form is submitted
    if request.method == 'POST' and form.validate():

        username = form.username.data
        email = form.email.data
        name = form.name.data

        # make sure user does not already exist
        if isnewuser(username):
            # add the user to mysql and log them in
            password = sha256_crypt.encrypt(form.password.data)

            data = {
                "type": "register",
                "username": f"{username}",
                "password": f"{password}",
                "email": f"{email}",
                "name": f"{name}"
            }
            write_thread = threading.Thread(target=write, args=(str(data),))
            write_thread.start()

            # users.insert(name, email, username, password)
            log_in_user(username)
            return redirect(url_for('dashboard'))
        else:
            flash('User already exists', 'danger')
            return redirect(url_for('register'))

    return render_template('register.html', form=form)


# Login page
@app.route("/login", methods=['GET', 'POST'])
def login():
    # if form is submitted
    if request.method == 'POST':
        # collect form data
        username = request.form['username']
        candidate = request.form['password']

        # access users table to get the user's actual password
        users = Table("users", "name", "email", "username", "password")
        user = users.getone("username", username)
        accPass = user.get('password')

        # if the password cannot be found, the user does not exist
        if accPass is None:
            flash("Username is not found", 'danger')
            return redirect(url_for('login'))
        else:
            # verify that the password entered matches the actual password
            if sha256_crypt.verify(candidate, accPass):
                # log in the user and redirect to Dashboard page
                log_in_user(username)
                flash('You are now logged in.', 'success')
                return redirect(url_for('dashboard'))
            else:
                # if the passwords do not match
                flash("Invalid password", 'danger')
                return redirect(url_for('login'))

    return render_template('login.html')


# Transaction page
@app.route("/transaction", methods=['GET', 'POST'])
@is_logged_in
def transaction():
    form = SendMoneyForm(request.form)
    balance = get_balance(session.get('username'))

    # if form is submitted
    if request.method == 'POST':
        try:
            # attempt to execute the transaction
            sender = session.get('username')
            recipient = form.username.data
            amount = form.amount.data

            # send_money(sender, recipient, amount)
            data = {
                "type": "transaction",
                "sender": f"{sender}",
                "recipient": f"{recipient}",
                "amount": f"{amount}"
            }
            write_thread = threading.Thread(target=write, args=(str(data),))
            write_thread.start()
            flash("Money Sent!", "success")
        except Exception as e:
            flash(str(e), 'danger')

        return redirect(url_for('transaction'))

    return render_template('transaction.html', balance=balance, form=form, page='transaction')


# Buy page
@app.route("/buy", methods=['GET', 'POST'])
@is_logged_in
def buy():
    form = BuyForm(request.form)
    balance = get_balance(session.get('username'))

    if request.method == 'POST':
        # attempt to buy amount
        try:
            # send_money("BANK", session.get('username'), form.amount.data)

            data = {
                "type": "transaction",
                "sender": "BANK",
                "recipient": f"{session.get('username')}",
                "amount": f"{form.amount.data}"
            }
            write_thread = threading.Thread(target=write, args=(str(data),))
            write_thread.start()

            flash("Purchase Successful!", "success")
        except Exception as e:
            flash(str(e), 'danger')

        return redirect(url_for('dashboard'))

    return render_template('buy.html', balance=balance, form=form, page='buy')


# logout the user. Ends current session
@app.route("/logout")
@is_logged_in
def logout():
    session.clear()
    flash("Logout success", "success")
    return redirect(url_for('login'))


# Dashboard page
@app.route("/dashboard")
@is_logged_in
def dashboard():
    balance = get_balance(session.get('username'))
    blockchain = get_blockchain().chain
    ct = time.strftime("%I:%M %p")
    return render_template('dashboard.html', balance=balance, session=session, ct=ct, blockchain=blockchain,
                           page='dashboard')


# Index page
@app.route("/")
@app.route("/index")
def index():
    return render_template('index.html')


stop_thread = False


def recieve():
    while True:
        global stop_thread
        if stop_thread:
            break
        try:
            message = client.recv(1024).decode('utf-8')
            # msg = message
            # msg = msg.replace("\'", "\"")
            #
            # rs = json.loads(msg)
            # print(rs)
            print(message)
        except:
            print('Error Occured while Connecting')
            client.close()
            break


def write(message):
    try:
        client.send(message.encode('utf-8'))
    except:
        print('Error Occured while Sending')


# Run app
if __name__ == '__main__':
    ip = "192.168.1.102"
    port = 5555
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((ip, port))

    recieve_thread = threading.Thread(target=recieve)
    recieve_thread.start()

    app.secret_key = 'secret123'
    app.run(debug=True)
