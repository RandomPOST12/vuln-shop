from flask import Flask,render_template,request,session,redirect,jsonify
from flask_sqlalchemy import SQLAlchemy
import sqlite3
import string
import os
import random

app  = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)
app.secret_key = 'secret_password'

# pa$$w0rd#$^#$
# Code Written By Sankalpa Acharya

class User(db.Model):
    id  = db.Column(db.Integer,primary_key=True);
    username = db.Column(db.String(100),nullable=False);
    password = db.Column(db.String(100),unique=True);
    role = db.Column(db.String(50));
    balance = db.Column(db.Integer);
    claim = db.Column(db.Boolean)

    def __init__(self,username,password,role):
        self.username = username
        self.password = password
        self.role = role
        self.balance = 450
        self.claim = False

    def check_password(self,password):
        return password==self.password



# connect = sqlite3.connect('users.db')
# with app.app_context():
#     db.create_all()

@app.route('/',methods=['GET','POST'])
def home():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session['username'] = user.username
            return redirect('/shop')
        else:
            return render_template('login.html',error_msg = 'Invalid Username or Password')
    return render_template('login.html')


@app.route('/create')
def create():
    return 'create'


@app.route('/dashboard')
def admin_panel():
    if 'username' in session:
        user = User.query.filter_by(username=session['username']).first()
        if user is None:
            return '<h1>You are not logged in :(</h1>'
        if user and user.role == 'admin':
            return render_template('dashboard.html')
    else:
        return '<h1>You are not logged in :(</h1>'

    return '<h1>Only admin can view this page, can you bypass it ?</h1>'


@app.route('/coupon', methods=['POST'])
def apply_coupon():
    if request.method == 'POST':
        if 'username' in session:
            user = User.query.filter_by(username=session['username']).first()
            if user:
                coupon_code = request.form['couponCode']
                if coupon_code=='X7pK9':
                    if user.claim:
                        return jsonify({'status':'ok','msg':'Coupon is already claimed'})
                    else:
                        user.balance+=100
                        user.claim = True
                        db.session.commit()
                        return jsonify({'status':'ok','msg':'🎉Coupon claimed, Refresh Page to Update Balance'})
                else:
                    return jsonify({'error':'Invalid Coupon'})
    return jsonify({'error':'Some error has occured'})


@app.route('/shop')
def shop():
    if 'username' in session:
        user = User.query.filter_by(username=session['username']).first()
        if user:
            if user.username=='dummyuser' or user.username=='admin':
                return redirect('/logout')
            return render_template('shop.html',balance=user.balance,username=user.username)
    return redirect('/')


@app.route('/checkout',methods=['POST'])
def checkout():
    if request.method == 'POST':
            if 'username' in session:
                user = User.query.filter_by(username=session['username']).first()
                if user:
                    data = request.get_json()
                    productId = data.get('productId')
                    if productId!=1:
                        return jsonify({'error':'Invalid Product ID'});
                    total = data.get('total')
                    user = User.query.filter_by(username=session['username']).first()
                    if total<550:
                        return jsonify({'error':'You are tampering with prices; there are no items in the store priced lower than Rs 550'});
                    if user.balance>=total:
                        return jsonify({'success':'congrats, your item is shipped for devlivery,flag{2e6cc8e163f713ec41cc39d5a867fab5}'});
                    else:
                        return jsonify({'error':'Insufficient Balance'});


@app.route('/admin',methods=['GET','POST'])
def admin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = sqlite3.connect('/home/webtest3434/mysite/users.db')
        cursor = conn.cursor()
        sql_query = f"SELECT * FROM users where username='{username}' AND password='{password}'"
        try:
            cursor.execute(sql_query)
            result = cursor.fetchone()
            print(result)
            if result is None:
                return render_template('admin.html',query=sql_query,error_msg='Invalid Username or Password')
            if result is not None:
                if result[1]=='admin':
                    session['username']='admin'
                    return redirect('/dashboard')
                else:
                    session['username']='dummyuser'
                    return redirect('/dashboard')
            return render_template('admin.html',query=sql_query)
        except Exception as e:
            return render_template('admin.html',error_msg=e,query=sql_query)
    return render_template('admin.html')


@app.route('/logout')
def logout():
    session.pop('username',None)
    return redirect('/')


if __name__ == '__main__':
    app.run(debug=True)