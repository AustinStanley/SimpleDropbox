import os
import sys
import socket

HOST = ''
PORT = 5050

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT)) 
s.listen(1)
conn, addr = s.accept()    

def save(data, fname):
    with open(fname, 'wb') as f:
        f.write(data)

def delete(fname):
    os.remove(fname)

def sendback(fname):
    with open(fname, 'rb') as f:
        conn.sendall(f.read())

def main():
    
    print('Connection from: ' + str(addr))

    while True:

        req = conn.recv(1024).decode()
        conn.sendall(b'1')

        if req == 'up':
            data = conn.recv(1024 ** 2)
            conn.sendall(b'1')
            fname = conn.recv(1024 ** 2).decode()
            save(data, fname)
            conn.sendall(b'1')

        elif req == 'dl':
            #import pdb; pdb.set_trace()
            fname = conn.recv(1024).decode()
            conn.sendall(b'1')
            sendback(fname)

        elif req == 'rm':
            delete(conn.recv(1024).decode())
            conn.sendall(b'1')

        elif req == 'q':
            break

    conn.close()
    s.close()

if __name__ == '__main__':
    main()
