#!/usr/bin/env python
#-*- coding: utf-8 -*-
import os
from flask import Flask
from flask import request
from flask import render_template
from flask import abort, redirect, url_for

led_status = "off"

app = Flask(__name__)

#button show
@app.route('/')
def index():
    return render_template('button.html')

@app.route('/ledon', methods=['GET', 'POST'])
def ledon():
    global led_status
    if request.method == 'POST':
        led_status = request.form['on']
        return redirect(url_for('index'))
    elif request.method == 'GET':
        return led_status
    else:
        return redirect(url_for('index'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run()
    
