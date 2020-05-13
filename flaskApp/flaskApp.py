from flask import Flask
import socket

app = Flask(__name__)

@app.route('/')
def hello():
    return ("<html><head> <title>CC Project Phase-2</title> <style>body {text-align: center;}</style></head><body>"
        "<b>Roll No = </b>i18-1421 <br /> <br /> " + 
        "<b>Name = </b> Hamza Mustafa Alvi <br /> <br />" +
        "<b>Hostname = </b>" + socket.gethostname() +
        "</body></html>"
        )

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
