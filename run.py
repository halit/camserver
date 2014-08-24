from flask import Flask, render_template
from gevent.pywsgi import WSGIServer
from geventwebsocket.handler import WebSocketHandler
from time import sleep
from cStringIO import StringIO

import SimpleCV as scv
cam = scv.Camera(0)

app = Flask(__name__, template_folder='./')
app.debug = True
host, port = 'localhost', 5000

@app.route('/')
def index():
    return render_template('index.html', host=host, port=port)


def wsgi_app(environ, start_response):
    path = environ["PATH_INFO"]
    if path == "/":
        return app(environ, start_response)
    elif path == "/websocket":
        handle_websocket(environ["wsgi.websocket"])
    else:
        return app(environ, start_response)


def handle_websocket(ws):
    while True:
        fp = StringIO()
        image = cam.getImage().flipHorizontal().getPIL()
        image.save(fp, 'JPEG')
        ws.send(fp.getvalue().encode("base64"))
        sleep(0.1)

if __name__ == '__main__':
    http_server = WSGIServer((host, port), wsgi_app, handler_class=WebSocketHandler)
    print('Server started at %s:%s' % (host, port))
    http_server.serve_forever()