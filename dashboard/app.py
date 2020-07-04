#!/usr/bin/env python3

import json

from flask import (
    Flask,
    redirect,
    render_template,
    request,
)


app = Flask(__name__)
datastore = '/usr/local/mehetweret/setpoints.json'

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/update', methods=['POST'])
def update():
    try:
        data = {
            'temperature': float(request.form['temperature']),
            'humidity': float(request.form['humidity']),
        }

        if data['temperature'] > 60:
            data['temperature'] = 60

        with open(datastore, 'w') as f:
            f.write(json.dumps(data))
    except Exception as e:
        return 'configuration update failed'
    return redirect('/')


@app.context_processor
def load_setpoints():
    data = None
    try:
        with open(datastore, 'r') as f:
            data = json.load(f)
    except:
        pass

    if not data:
        data = dict()
    if 'temperature' not in data:
        data['temperature'] = 52
    if 'humidity' not in data:
        data['humidity'] = 80

    return data


if __name__ == '__main__':
    app.run(debug=True)
