import socket
import threading
import constant as const
import time
import heapq as hq
from Packet import Packet

def handle_client(conn, addr):
    start = time.time()
    connected = True
    thread_count = 0
    response_packets = []
    hq.heapify(response_packets)

    print(f"[NEW CONNECTION] {addr} connected")
    while connected:
        try:
            msg = conn.recv(const.MAX_BUUFER_SIZE).decode(const.FORMAT)
            if msg:
                print(f"{addr}: received message")
                msg_components = msg.split('\r\n')
                main_message = msg_components[0].split()  # first line of the packet
                # if it is a non-persistent connection prepare packet, send it and break
                if main_message[-1][-1] == '0':
                    prepare_response_package(msg_components, response_packets, time.time(), 0)
                    conn.sendall(response_packets[0])
                    response_packets = []
                    hq.heapify(response_packets)
                    break
                print(f"{addr}: persistent connection")
                #if it's persistent and pipelined:
                #spawn thread and delegate preparing the response message to it
                spawned_thread=threading.Thread(target=prepare_response_package, args = (msg_components, response_packets, time.time(), 1))
                spawned_thread.start()
                spawned_thread.join()
                print(f"{addr}: a sub-thread has started")
                thread_count += 1
                print(f"for{addr} have {thread_count} sub-threads")
                #sending messages in order of the thread timestamp
                while response_packets:
                    print(f"{addr}: Sending packet")
                    response_packet = hq.heappop(response_packets)
                    conn.sendall(response_packet.msg)
                    thread_count -= 1
            else:
                #timeout
                if thread_count == 0 and time.time()-start > time_idle():
                    break
                else:
                    continue
        except:
            if thread_count == 0 and time.time() - start > time_idle():
                break
            else:
                continue
    print(f"[Connection closed] for connection {addr}")
    conn.close()


def prepare_response_package(msg_components, response_packets, timestamp, version):
    main_message = msg_components[0].split()  # first line of the packet

    #GET REQUEST
    if main_message[0] == 'GET':
        # check if file is available
        try:
            # if file is available open and read its data
            file = open(main_message[1][1:], "rb")
            data = file.read()
            file.close()
            # prepare the response packet along with the data read from the file
            data = data.decode(const.FORMAT)
            packet_string = main_message[-1] + " 200 OK\r\n\r\n" + data
            packet_bytes = packet_string.encode(const.FORMAT)
        except IOError:
            # if file is not found, send error response
            packet_string = main_message[-1] + " 404 Not Found\r\n\r\n"
            packet_bytes = packet_string.encode(const.FORMAT)

    #POST request
    elif main_message[0] == 'POST':
        data = msg_components[-1]
        uploaded_filename = main_message[1][1:]
        try:
            # if file is written successfully
            file = open(uploaded_filename, "wb")
            file.write(data.encode(const.FORMAT))
            file.close()
            # prepare the response packet along with the data read from the file
            packet_string = main_message[-1] + " 200 OK\r\n\r\n"
            packet_bytes = packet_string.encode(const.FORMAT)
        except IOError:
            # if file can not be written, send error response
            packet_string = main_message[-1] + " 404 Not Found\r\n\r\n"
            packet_bytes = packet_string.encode(const.FORMAT)

    #if http version 0, send bytes only
    if version == 0:
        hq.heappush(response_packets,packet_bytes)
    #if http version 1, send bytes and timestamp in a packet and add it to the heap
    else:
        packet= Packet(packet_bytes, timestamp)
        hq.heappush(response_packets, packet)
    return


# simple heuristic to determine the idle time available for a presistent connection
def time_idle():
        return max((30-threading.active_count())/2, 3)


def start():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.bind(const.SERVER_ADDR)
        server.listen()
        print(f"[SERVER IS LISTENING] on {const.SERVER_IP}")
        while True:
            # when request is received store the addr and port of that request and create object for that connection
            conn, addr = server.accept()
            thread = threading.Thread(
                target=handle_client, args=(conn, addr))
            thread.start()
            print(f"[ACTIVE CONNECTIONS] {threading.active_count()-1}")

if __name__ == '__main__':
    start()
