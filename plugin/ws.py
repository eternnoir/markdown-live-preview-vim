# coding: utf-8
# modified from: http://0x14.iteye.com/blog/1396511
import base64
import hashlib
import json
import struct


# shake hands after connection
def handshake(conn):
    headers = {}
    shake = conn.recv(1024)

    if not len(shake):
        return False

    header, data = shake.split('\r\n\r\n', 1)
    for line in header.split("\r\n")[1:]:
        key, value = line.split(": ", 1)
        headers[key] = value

    if "Sec-WebSocket-Key" not in headers:
        print("this socket is not websocket,close")
        conn.close()
        return False

    key = base64.b64encode(hashlib.sha1(
        headers["Sec-WebSocket-Key"] +
        '258EAFA5-E914-47DA-95CA-C5AB0DC85B11').digest())
    host = headers["Host"]

    response = "HTTP/1.1 101 Switching Protocols\r\n"\
               "Upgrade:websocket\r\n"\
               "Connection: Upgrade\r\n"\
               "Sec-WebSocket-Accept:" + key + "\r\n"\
               "WebSocket-Location: ws://" + host + "/WebManagerSocket\r\n"\
               "WebSocket-Protocol:WebManagerSocket\r\n\r\n"

    conn.send(response)
    return True


def RecvData(num, conn):
    try:
        recv_data = conn.recv(num)
        if not len(recv_data):
            return False
    except:
        return False
    else:
        length = ord(recv_data[1]) & 127
        if length == 126:
            masks = recv_data[4:8]
            data = recv_data[8:]
        elif length == 127:
            masks = recv_data[10:14]
            data = recv_data[14:]
        else:
            masks = recv_data[2:6]
            data = recv_data[6:]

        raw_str = ""
        i = 0
        for d in data:
            raw_str += chr(ord(d) ^ ord(masks[i % 4]))
            i += 1

        return raw_str


def SendData(data, conn):
    try:
        if not isinstance(data, str):
            data = json.dumps(data)
    except:
        return False

    token = "\x81"
    length = len(data)
    if length < 126:
        token += struct.pack("B", length)
    elif length <= 0xFFFF:
        token += struct.pack("!BH", 126, length)
    else:
        token += struct.pack("!BQ", 127, length)
    data = '%s%s' % (token, data)

    conn.send(data)
    return True