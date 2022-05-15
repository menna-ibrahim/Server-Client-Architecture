import socket
import constant as const
import sys

def read_input(filename):
    #reading commands from input.txt file which will have all client commands
    text_file = open(filename, "r")
    data = text_file.read()
    text_file.close()
    commands = data.split('\n')
    for command in commands:
        handle_command(command)

def handle_command(command):
    if command in cache_dict.keys():
        print("command found in cache")
        print(cache_dict[command])
    else:
        command_string = command
        command = command.split()
        #call the appropriate function according to the nature of the command
        if command[0] == "GET":
            print("GET REQUEST")
            send_get_request(command[1:], command_string)
        elif command[0] == "POST":
            print("POST REQUEST")
            send_post_request(command[1:], command_string)
        else:
            print("UNKNOWN COMMAND")

def send_get_request(command, command_string):
    #extracting all infromation needed from the command
    filename = command[0]
    hostname = command[1]
    if command[-1] == command[1]:
        port_number = 80 #default value
    else:
        port_number = int(command[-1])
    #preparing packet
    packet_string = "GET "+filename+" HTTP/1.1\r\nHost: "+hostname+":"+str(port_number)+"\r\n\r\n"
    packet_bytes = packet_string.encode(const.FORMAT)
    #setting up connection and sending packet
    data = send_packet(hostname, port_number, packet_bytes)
    #add response message to cache
    cache_dict[command_string] = data
    print(data)
    data = data.decode(const.FORMAT).split('\r\n')
    downloaded_filename = filename[1:]
    try:
        file = open(downloaded_filename, "wb")
        file.write(data[-1].encode(const.FORMAT))
        file.close()
    except IOError:
        print("Error occured while downloading the file")

def send_post_request(command, command_string):
    filename = command[0]
    hostname = command[1]
    if command[-1] == command[1]:
        port_number = 80  # default value
    else:
        port_number = int(command[-1])
    try:
        # if file is available open and read its data
        file = open(filename[1:], "r")
        data = file.read()
        file.close()
        uploaded_filename = filename[1:]
        # prepare the request packet along with the data read from the file
        packet_string = "POST \\" + uploaded_filename + " HTTP/1.1\r\nHost: "+hostname+":"+str(port_number)+"\r\n\r\n" + data
        packet_bytes = packet_string.encode(const.FORMAT)
        # setting up connection and sending packet
        data_received = send_packet(hostname, port_number, packet_bytes)
        #add response message to cache
        cache_dict[command_string] = data_received
        print(data_received)
    except IOError:
        # if file is not found, print error msg for client
        print("FILE NOT FOUND")

def send_packet(hostname,port_number,packet_bytes):
    #check if there is no connection has been made before, make new connection
    if hostname not in hostnames_dict.keys():
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        hostnames_dict[hostname] = s
        s.connect((hostname, port_number))
    #if the client has a set-up connection already, check if it is still active, use it. If the server closed it, make new one
    elif hostnames_dict[hostname]:
        print("hostname found")
        s = hostnames_dict[hostname]
    try:
        s.sendall(packet_bytes)
        data = s.recv(const.MAX_BUUFER_SIZE)
    except socket.error:
        print("connection closed --new connection has to be made")
        del hostnames_dict[hostname]
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        hostnames_dict[hostname] = s
        s.connect((hostname, port_number))
        s.sendall(packet_bytes)
        data = s.recv(const.MAX_BUUFER_SIZE)
    return data



if __name__ == '__main__':
    filename = sys.argv[-1]
    if filename == "client.py":
        filename = "input.txt"
    hostnames_dict = {}
    cache_dict = {}
    read_input(filename)

