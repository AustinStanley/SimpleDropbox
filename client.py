import os
import sys
import socket
import threading
from Crypto.Cipher import AES
from Crypto import Random
from base64 import b64encode, b64decode

hosted_files = []
key = b'sixteen byte key' # hackers please ignore this line
ip = socket.gethostbyname(socket.gethostname()) # local IP
port = 5050 # arbitrary port 

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((ip, port))

def encrypt(data):
    iv = bytes(Random.new().read(AES.block_size))
    cipher = AES.new(key, AES.MODE_CFB, iv)
    return b64encode(iv + cipher.encrypt(data))

def decrypt(data):
    iv = b64decode(data)[:AES.block_size]
    cipher = AES.new(key, AES.MODE_CFB, iv)
    return cipher.decrypt(b64decode(data)[AES.block_size:])

def upload(fname):
    with open(fname, 'rb') as f:
        data = f.read()

    s.sendall(b'up')
    s.recv(1)
    s.sendall(encrypt(data))
    s.recv(1)
    s.sendall(fname.encode())
    s.recv(1)

def download(fname, path):
    s.sendall(b'dl')
    s.recv(1)
    s.sendall(fname.encode())
    s.recv(1)
    data = s.recv(1024 ** 2)

    with open('/'.join([path, fname]), 'wb') as f:
        f.write(decrypt(data))

def remove(fname):
    s.sendall(b'rm')
    s.recv(1)
    s.sendall(fname.encode())
    s.recv(1)

def input_loop():
    '''Called by input thread. 
    Listens for user input.
    '''

    while True:
        cmd = input('>>> ').lower().split()

        if cmd[0] == 'q':
            s.sendall(b'q')
            s.close()
            return

        elif cmd[0] == 'dl':
            download(cmd[1], cmd[2])

def update_loop():
    '''Continually checks the contents of the directory.
    If any new files are found, the are automatically uploaded to server.
    If any files are missing, they are removed from the server.
    '''

    while True:
        for root, dirs, files in os.walk('.'):
            for fname in files:
                if fname not in hosted_files:
                    upload(fname)
                    hosted_files.append(fname)

            for fname in hosted_files:
                if fname not in files:
                    remove(fname)
                    hosted_files.remove(fname)

            # Do not follow subdirectories
            if dirs:
                del dirs[:]


def main():
    '''Walk the directory for files already added,
    then start the input and update threads.
    Note: files added to the directory while this
    program is not running will be added to hosted_files,
    but won't actually be uploaded.
    Can be fixed using Pickle, but I don't feel like it.
    '''

    for root, dirs, files in os.walk('.'):
        for fname in files:
            hosted_files.append(fname)

        # subdirectories not allowed!
        if dirs:
            del dirs[:]

    input_thread = threading.Thread(target=input_loop)
    update_thread = threading.Thread(target=update_loop) 
    update_thread.daemon = True
    update_thread.start()
    input_thread.start()

if __name__ == '__main__':
    main()
