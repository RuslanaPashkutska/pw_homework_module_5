import socket



def main():
    server = socket.gethostname()
    port = 5001

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    while True:
        message = input(">>> ")
        if message.lower() in ["exit", "quit"]:
            break
        sock.sendto(message.encode(), (server, port))
        data, _ = sock.recvfrom(4096)
        print("Server:", data.decode())

    sock.close()

if __name__ == "__main__":
    main()
