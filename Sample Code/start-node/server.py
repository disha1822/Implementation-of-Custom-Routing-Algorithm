import socket
import threading
import tqdm
import os
import sys
import time
node = "10.128.0.9"
port = 4444

SEPARATOR = "<<SEPARATOR>>"
BUFFER_SIZE = 4096 # send 4096 bytes each time step

# the name of file we want to send
if(len(sys.argv) < 2):
    print("Resource not specified...")
    exit()
else:
    filename = sys.argv[1]
# get the file size
filesize = os.path.getsize(filename)

def forward():
    for dest in sortedIpList:
        forward_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            print(f"[+] Connecting to {dest}:{port} ...")
            forward_conn.connect((dest, port))
            print("[+] Connected.")
            # send the filename and filesize
            forward_conn.send(f"{filename}{SEPARATOR}{filesize}{SEPARATOR}".encode())
            # start sending the file
            progress = tqdm.tqdm(range(filesize), f"Sending {filename}", unit="B", unit_scale=True, unit_divisor=1024)
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
            print(f"{dest} already received message...")
            continue
        finally:
            forward_conn.close()
        time.sleep(5)
ipPercCentralityMap = {"10.128.0.2":0.2,"10.128.0.3":0.2 ,"10.128.0.4":0 ,"10.128.0.5":0.366667,"10.128.0.6":0,"10.128.0.7":0,"10.128.0.8":0.633333}
sortedIpList = list(dict(sorted(ipPercCentralityMap.items(), key=lambda item: item[1],reverse=True)).keys())

forward()
