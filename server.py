from socket import socket, SOL_SOCKET, SO_REUSEADDR

from multiprocessing import Process
from select import select
from time import sleep


def createContext(ip, port):
    sock = socket()
    sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    sock.bind((ip, port))
    sock.listen(0)
    return sock


def cltSession(cltSock, address):
    packet = ''.join([i for i in svrResponse(cltSock)])
    req =  parseRequest(packet,cltSock)
    resp = svrMng(req)
    cltSock.close()


def createCltSock(sock):
    while True:
        cltSock, address = sock.accept()
        cltSock.setblocking(False)
        cltSession(cltSock, address)


def parseRequest(request,cltSock):
    req = {}
    req['cltSock'] = cltSock
    req['totalReq'] = request
    ipAndPort = request.split('Host: ')[1].split('\r\n')[0]
    if ':' in ipAndPort :
        ip, port = ipAndPort.split(':')
        req['ip'] = ip
        req['port'] = int(port)
    else :
        req['ip'] = ipAndPort
        req['port'] = 80
    if 'Connection: keep-alive' in req['totalReq']:
        req['totalReq'] = req['totalReq'].replace('Connection: keep-alive', 'Connection: Close')
    if 'Connection: Keep-Alive' in req['totalReq']:
        req['totalReq'] = req['totalReq'].replace('Connection: Keep-Alive', 'Connection: Close')
    return req


def svrMng(dic):
    svrSock = socket()
    svrSock.connect((dic['ip'], dic['port']))
    svrSock.setblocking(False)
    dispoSock(svrSock,False)
    svrSock.send(dic['totalReq'])
    response = ''
    for data in svrResponse(svrSock) :
       response += data
       dispoSock(dic['cltSock'],False)
       dic['cltSock'].send(data)
    return response
    # header, corps  = reponse.split('\n\r\n\r')



def svrResponse(sock, timeout=5):
    over = False
    ct = 0
    dispoSock(sock)
    bufferSize = 536
    while not over:
        print bufferSize
        if ct == timeout:
            over = True
        try:
            response = sock.recv(bufferSize)
            if response == '':
                sleep(0.1)
                ct += 1
        except Exception:
            bufferSize = bufferSize/2
            sleep(0.1)
            ct += 1
        else :
            ct = 0
            if len(response) == bufferSize:
                bufferSize = bufferSize*4
            yield response



def dispoSock(sock, lecture=True):
    over = False
    while not over :
        if lecture:
            r, w, e = select((sock, ), (), (), 0)
            if r and r[0] == sock :
                over = True
        else :
            r, w, e = select((), (sock, ), (), 0)
            if w and w[0] == sock:
                over = True


def mainServer():
    processList = []
    sock = createContext('0.0.0.0', 8080)
    for i in range(4):
        p = Process(target=createCltSock, args=(sock, ))
        p.daemon = True
        p.start()
        processList.append(p)
    try:
        for proc in processList:
            proc.join()
    except KeyboardInterrupt:
        sock.close()
        exit(0)


if __name__ == '__main__':
    mainServer()