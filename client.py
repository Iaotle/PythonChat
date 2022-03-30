import select
import socket
import sys
import threading


server_address = ('localhost', 5378)  # for local server
# Log in:
while True:
    # Create a TCP/IP socket
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Bind the socket to the port
    print("Connecting to %s on port %s" % server_address)
    server.connect(server_address)
    sys.stdout.write("Enter your username: ")
    username = sys.stdin.readline()
    if username.startswith("!quit") or username.startswith("!exit"):
        server.close()
        exit(0)
    server.send(bytes("HELLO-FROM " + username))
    loginStatus = server.recv(4096)
    if loginStatus == "HELLO " + username:
        break
    print("Error: " + loginStatus)
print("Login successful! Type !who for a list of users, !quit or !exit to exit, and @user message to send a message!")
# Parse:
while True:
    read_sockets, write_socket, error_socket = select.select([sys.stdin, server], [], [])

    for socks in read_sockets:
        if socks == server:
            message = socks.recv(4096)
	    for x in range (0, message.count("\n")):
		    index = message.find("\n")
		    while index == -1:
			message += socks.recv(4096)
			index = message.find("\n")
		    if message.startswith("DELIVERY"):
			send = message[9:index+1].split(" ", 1)
			message = message[index+1:]
			response = send[0] + ": " + send[1]
			sys.stdout.write(response)
		    elif message.startswith("SEND-OK"):
		        response = "Message sent.\n"
			message = message[index+1:]
			sys.stdout.write(response)
		    elif message.startswith("WHO-OK"):
		        response = "Active users:" + message[:index+1].lstrip("WHO-OK")
			message = message[index+1:]
			sys.stdout.write(response)
		    elif message.startswith("B") or message.startswith("U"):
		        response = "Error: " + message
			message = message[index+1:]
			sys.stdout.write(response)
		    else:
		        response = message
			message = message[index+1:]
			sys.stdout.write(response)
        else:
            message = sys.stdin.readline()

            if message.startswith("@"):
                request = bytes("SEND " + message.lstrip("@"))
		# request = bytes("SEND iaotle batched\nWHO\nSEND iaotle message\n")
            elif message.startswith("!who"):
                request = bytes("WHO\n")
            elif message.startswith("!quit") or message.startswith("!exit"):
                server.close()
                exit(0)
            else:
                request = message
            server.send(request)
            sys.stdout.flush()
