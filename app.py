from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html', **locals())

@app.route('/repurpose')
def repurpose():
    return render_template('repurpose.html', **locals())

@app.route('/sell')
def sell():
    return render_template('sell.html', **locals())


if __name__ == '__main__':
    app.run(debug=True)