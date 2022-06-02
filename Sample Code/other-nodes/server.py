from datetime import datetime
import socket
import threading, queue
import tqdm
import os
node = "10.128.0.2" # ip address of the particular node
port = 4444

# receive 4096 bytes each time
BUFFER_SIZE = 4096
SEPARATOR = "<<SEPARATOR>>"

# Adjacent nodes to this node
destinations = ["10.128.0.5","10.128.0.8"]  # destination ip addresses of the particular node
q = queue.Queue()
recovered = True
def accept():
    accept_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # bind the socket to our local address
    accept_conn.bind((node, port))
    # enabling our server to accept connections
    # 5 here is the number of unaccepted connections that
    # the system will allow before refusing new connections
    accept_conn.listen(5)
    print(f"[*] Listening as {node}:{port}")
    global recovered
    while recovered:
        # accept connection if there is any
        conn, addr = accept_conn.accept()
        print(f"[+] {addr} is connected.")
        # receive the file infos
        # receive using client socket, not server socket
        received = conn.recv(BUFFER_SIZE).decode()
        filename, filesize, message = received.split(SEPARATOR)
        # remove absolute path if there is
        filename = os.path.basename(filename)
        # convert to integer
        filesize = int(filesize)
        # start receiving the file from the socket
        # and writing to the file stream
        progress = tqdm.tqdm(range(filesize), f"Receiving {filename}", unit="B", unit_scale=True, unit_divisor$
        with open(filename, "wb") as f:
            if(message != ""):
                f.write(message.encode())
            while True:
                # read 1024 bytes from the socket (receive)
                bytes_read = conn.recv(BUFFER_SIZE)
                if not bytes_read:
                    # nothing is received
                    # file transmitting is done
                    break
                # write to the file the bytes we just received
                f.write(bytes_read)
                # update the progress bar
                progress.update(len(bytes_read))
        print(f"[+] Message received at [{datetime.utcnow()}]")
        for dest in destinations:
            q.put((conn, addr, filename, filesize, dest))
        recovered = False
        conn.close()
    accept_conn.close()
def forward():
    global recovered
    print("Forward connections listening...")
    while True:
        if q.empty()==True and recovered==False:
            break
        curr = q.get()
        forward_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            print(f"Forwarding to {curr[4]}:{port}")
            forward_conn.connect((curr[4], port))
            # send the filename and filesize
            filename = curr[2]
            filesize = curr[3]
            forward_conn.send(f"{filename}{SEPARATOR}{filesize}{SEPARATOR}".encode())
            # start sending the file
            progress = tqdm.tqdm(range(filesize), f"Sending {filename}", unit="B", unit_scale=True, unit_divis$
            with open(filename, "rb") as f:
                while True:
                    # read the bytes from the file
                    bytes_read = f.read(BUFFER_SIZE)
                    if not bytes_read:
                        # file transmitting is done
                        break
                    # we use sendall to assure transimission in
                    # busy networks
                    forward_conn.sendall(bytes_read)
                    # update the progress bar
                    progress.update(len(bytes_read))
        except:
            print(f"{curr[4]} already received message")
            continue
        finally:
            forward_conn.close()
if __name__ == "__main__":
    t1 = threading.Thread(target=accept)
    t2 = threading.Thread(target=forward)
    t1.start()
    t2.start()
    t1.join()
    t2.join()
