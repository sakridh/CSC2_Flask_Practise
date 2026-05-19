import json

from flask import Flask, render_template, request, redirect, url_for, session, flash 

app = Flask(__name__)
app.secret_key = 'your secret key'


@app.route('/')
def index():
    return render_template('index.html')
 
@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/checkout')
def checkout():
    return render_template('invoice.html')

@app.route('/orders')
def order_history():
    return render_template('order_history.html')

if __name__ == '__main__': 
    app.run(debug=True)