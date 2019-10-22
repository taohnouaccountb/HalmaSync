""" Script for TCP chat server - relays messages to all clients """

from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread

clients = {}
addresses = {}

HOST = "0.0.0.0"
PORT = 2333
BUFSIZ = 1000000
ADDR = (HOST, PORT)
SOCK = socket(AF_INET, SOCK_STREAM)
SOCK.bind(ADDR)


def accept_incoming_connections():
    """Sets up handling for incoming clients."""
    while True:
        client, client_address = SOCK.accept()
        print("%s:%s has connected." % client_address)
        client.send("Greetings from the ChatRoom! ".encode("utf8"))
        client.send("Now type your name and press enter!".encode("utf8"))
        addresses[client] = client_address
        Thread(target=handle_client, args=(client, client_address)).start()


def handle_client(conn, addr):  # Takes client socket as argument.
    """Handles a single client connection."""
    name = conn.recv(BUFSIZ).decode("utf8")

    msg = "%s from [%s] has joined the chat!" % (
        name, "{}:{}".format(addr[0], addr[1]))
    broadcast(bytes(msg, "utf8"))
    clients[conn] = name
    try:
        while True:
            msg = conn.recv(BUFSIZ)
            if msg != bytes("#quit", "utf8"):
                broadcast(msg, name + ": ")
            else:
                conn.send(bytes("#quit", "utf8"))
                conn.close()
                del clients[conn]
                print("[Leaving]"+str(name))
                broadcast(bytes("%s has left the chat." % name, "utf8"))
                break
    except:
        print(str(addr) + " disconnected with exception")
        conn.close()


def broadcast(msg, prefix=""):  # prefix is for name identification.
    """Broadcasts a message to all the clients."""
    for sock in clients:
        print("[Broadcast]" + str(prefix) + str(msg))
        sock.send(bytes(prefix, "utf8") + msg)


if __name__ == "__main__":
    SOCK.listen(100)  # Listens for 5 connections at max.
    print("Chat Server has Started !!")
    print("Waiting for connections...")
    ACCEPT_THREAD = Thread(target=accept_incoming_connections)
    ACCEPT_THREAD.start()  # Starts the infinite loop.
    ACCEPT_THREAD.join()
    SOCK.close()
