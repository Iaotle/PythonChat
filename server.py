# Python program to implement server side of chat room. 
import socket
import sys
from thread import *

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

server.bind(('localhost', 5378))

server.listen(65)

iplist = []
userlist = []


def clientthread(conn, addr):
    # Login:
    if len(iplist) > 64:
        conn.send("BUSY\n")
        remove(conn)
    message = conn.recv(2048)
    if message.startswith("HELLO-FROM"):
        username = message.lstrip("HELLO-FROM ").rstrip("\n")
        if "\n" in username or " " in username:
            conn.send("BAD-RQST-BODY\n")
        elif username not in userlist:
            userlist.append(username)
            conn.send("HELLO " + username + "\n")
        else:
            conn.send("IN-USE\n")
            remove(conn)
    else:
        conn.send("BAD-RQST-HDR\n")
        remove(conn)

    print(username + " connected.")

    # Parse:
    while True:
        try:
            message = conn.recv(4096)
            if message:
                for x in range(0, message.count("\n")):
                    index = message.find("\n")
                    while index == -1:
                        message += conn.recv(4096)
                        index = message.find("\n")
                    sys.stdout.write(username + ": " + message[:index + 1])
                    if message.startswith("SEND"):
                        send = message[:index + 1].lstrip("SEND ").split(" ", 1)
                        if send[0] in userlist:
                            userindex = userlist.index(send[0])
                            if "\n" in send[1][:-1]:
                                conn.send("BAD-RQST-BODY\n")
                            else:
                                send = "DELIVERY " + username + " " + send[1] + "\n"
                                conn.send("SEND-OK\n")
                                # send = "DELIVERY iaotle testmessage"
                                iplist[userindex].send(send)
                                # iplist[userindex].send(" done\nSEND-OK\nDELIVERY iaotle testmessage\n")
                                message = message[index + 1:]
                        else:
                            conn.send("UNKNOWN\n")
                    elif message.startswith("WHO"):
                        conn.send("WHO-OK " + ", ".join(userlist) + "\n")
                        message = message[index + 1:]
                    else:
                        conn.send("BAD-RQST-HDR\n")
                        message = message[index + 1:]

            else:
                index = iplist.index(conn)
                print(userlist.pop(index) + " disconnected.")
                remove(conn)
        except:
            continue


def remove(connection):
    if connection in iplist:
        iplist.remove(connection)


while True:
    conn, addr = server.accept()
    iplist.append(conn)
    start_new_thread(clientthread, (conn, addr))

conn.close()
server.close()
