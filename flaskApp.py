from flask import Flask
import socket

app = Flask(__name__)

@app.route('/')
def hello():
    return "Hostname = " + socket.gethostname() + ",  Roll No = i18-1421"

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
