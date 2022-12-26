import threading
import socket
import json

from sqlhelpers import *

hostname = socket.gethostname()
host = socket.gethostbyname(hostname)
port = 5555

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server.bind((host, port))

server.listen()

clients = []


def broadcast(message):
    for client in clients:
        client.send(message)


def handle(client):
    while True:
        try:
            msg = message = client.recv(1024)
            msg = str(msg.decode("utf-8"))
            msg = msg.replace("\'", "\"")

            rs = json.loads(msg)
            print(rs)

            if rs["type"] == "transaction":
                send_money2(rs["sender"], rs["recipient"], rs["amount"])
            elif rs["type"] == "register":
                insert_user(rs["name"], rs["email"], rs["username"], rs["password"])

            broadcast(message)

        except:
            print("Error while Handling")


def recieve():
    while True:
        client, address = server.accept()
        print(f"Connected with {str(address)}")

        clients.append(client)

        # client.send('Connected to the Server!'.encode('utf-8'))

        thread = threading.Thread(target=handle, args=(client,))
        thread.start()


# Calling the main method
print(f'Node is Listening on {host}, port: {port}....')
recieve()
