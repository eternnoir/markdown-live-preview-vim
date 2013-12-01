import socket
import threading
import os
import sys
from bottle import *
from markdown import markdown
from ws import *
from PyQt4.QtGui import QApplication, QDialog, QMainWindow
from PyQt4.QtCore import pyqtSignature, QUrl
from mainwindow import  *



markdown_options = ['extra', 'codehilite']
client = None
workPath = ''
defaultHtml = '/template/default.html'


def startServer():
    global client
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("localhost", 5566))
    sock.listen(1)
    while True:
        conn, addr = sock.accept()
        if handshake(conn):
            client = conn


@route('/<path:path>')
def server_static(path):
    return static_file(path, root='.')

@post('/')
def convert():
    html = markdown(request.forms['md'].decode('utf-8'), markdown_options)
    if client:
        SendData(html, client)
    return 'OK'

def gogogo():
    t = threading.Thread(target=startServer)
    t.daemon = True
    t.start()
    run(host='localhost', port=9999)

def setScript(htmlPath,scriptPath):
    script = open(scriptPath).read()
    htmld = open(htmlPath).read()
    html = htmld.replace('{{script}}',script)
    f = open(workPath+'/tmp.html','w+')
    f.write(html)
    f.close()


if __name__ == '__main__':
    t = threading.Thread(target=gogogo)
    t.daemon = True
    workPath = sys.argv[1]
    t.start()
    setScript(workPath+defaultHtml,workPath+'/script')
    a = QApplication(sys.argv)
    window = QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(window)
    ui.webView.load(QUrl(workPath+'/tmp.html'))
    window.show()
    sys.exit(a.exec_())