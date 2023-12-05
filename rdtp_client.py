## data transfer with reliable udp packets ##

# Global variables are used to simplify the code and make it easier to understand



# To run this script, use the command line as follows:
# python3 rudp.py server_IP1:5000 server_IP2:192.168.1.101:5001
import socket, threading, sys, struct, datetime, hashlib, random, time

# Manually entered interfaces IPs
local1_interface_ip, local1_port = '192.168.0.17', 53121
local2_interface_ip, local2_port = '192.168.0.17', 53122

def send_and_receive(type=1, number=0, s=0, e=0):
  try:
    request_packet = create_packet(local1_port, server1_port, type, number, s, e)
    print_packet(request_packet, (local1_interface_ip, local1_port)) # ! DEBUG MODE

    if sock1.sendto(request_packet, (server1_ip, server1_port)) != 0:
      # receive 10 bytes for header + 1024 bytes for data
      packet, sockaddr = sock1.recvfrom(1024+10) 
      print_packet(packet, sockaddr) # ! DEBUG MODE
    else:
      print("Error sending packet to server 1. Try again.")
      sock1.close()
      exit(1)
  except socket.timeout:
    try:
      print("Request timed out. Trying server 2…")
      sock1.close()
      request_packet = create_packet(local2_port, server2_port, type, number, s, e)
      print_packet(request_packet, (local2_interface_ip, local2_port)) # ! DEBUG MODE
      if sock2.sendto(request_packet, (server2_ip, server2_port)) != 0:
        packet, sockaddr = sock2.recvfrom(1024)
        print_packet(packet, sockaddr) # ! DEBUG MODE
      else:
        print("Error sending packet to server 2. Try again.")
        sock2.close()
        exit(1)
    except socket.timeout:
      print("Request timed out. Try again.")
      sock2.close()
      sys.exit(1)

  # if e != 0 then for loop: if there is still incoming packets in the socket, receive them
  if e != 0:
    while True:
      try:
        packet, sockaddr = sock1.recvfrom(1024+10)
        print_packet(packet, sockaddr) # ! DEBUG MODE
      except socket.timeout:
        break
  


  return packet, sockaddr

def create_packet(source_port, destination_port, REQUEST_TYPE, FILE_ID, START_BYTE, END_BYTE):
    header = struct.pack("!BBll", REQUEST_TYPE, FILE_ID, START_BYTE, END_BYTE)
    packet = header
    return packet

def create_socket(interface_ip, server_ip, server_port):
    """
    Create a UDP socket bound to a 
    specific interface and destined for a server.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.settimeout(1)  # Set timeout of 1 second for socket operations
    # sock.bind((interface_ip, 0))  # Bind to the interface with a random port
    # sock.connect((server_ip, server_port))  # Connect to the server
    return sock

def parse_server_address(address):
    ip, port = address.split(':')
    return ip, int(port)

def print_packet(packet, sockaddr):
  ## ! DEBUG MODE ! ##
  print(' ')
  print('-'*54)   # DEBUG: print packet
  if sockaddr[1] == server1_port:
    print('[DEBUG]: response packet received from server 1')
  elif sockaddr[1] == server2_port:
    print('[DEBUG]: response packet received from server 2')
  elif sockaddr[1] == local1_port:
    print('[DEBUG]: request packet sending from local 1')
  elif sockaddr[1] == local2_port:
    print('[DEBUG]: request packet sending from local 2')
  else:
    print('[DEBUG]: unknown socket')

  if packet[0:1].hex() == '01':
    print('[DEBUG]: file list packet [01]')
  elif packet[0:1].hex() == '02':
    print('[DEBUG]: file size packet [02]')
  elif packet[0:1].hex() == '03':
    print('[DEBUG]: file data packet [03]')
  elif packet[0:1].hex() == '100':
    print('[DEBUG]: invalid request type [100]')
  elif packet[0:1].hex() == '101':
    print('[DEBUG]: invalid file id [101]')
  elif packet[0:1].hex() == '102':
    print('[DEBUG]: invalid start or end byte [102]')
  else:
    print('[DEBUG]: unknown packet [', packet[0:1].hex(), ']')

  header = packet[0:1].hex(), packet[1:2].hex(), packet[2:6].hex(), packet[6:10].hex()
  if packet[10:] != b'':
    data = str(packet[10:26])
    # get rid of b' and ' at the beginning and end of the string
    data = data[2:-1] + '...  (truncated)'
  else:
    data = packet[10:]

  print('[DEBUG]:',datetime.datetime.now())
  print(' socket:',sockaddr)
  print(' header:',header)
  print('   data:',data)
  print('-'*54)
  ## ! DEBUG MODE ! ##

def handle_transfer(sock, destination_ip, destination_port):
    """
    Communication over a socket.
    Protocol logic, sending requests and handling responses.
    """
    # protocol logic (data transfer and handling logic)
    pass


def main():
    if len(sys.argv) != 3:  # Validate and parse command-line arguments
        print("Usage: rdtp_client server_IP1:port1 server_IP2:port2")
        sys.exit(1)

    # Parse command-line arguments, global variables simplify code
    global sock1, sock2, server1_ip, server1_port, server2_ip, server2_port;
    server1_ip, server1_port = parse_server_address(sys.argv[1])
    server2_ip, server2_port = parse_server_address(sys.argv[2])

    # Create sockets for each connection
    sock1 = create_socket(local1_interface_ip, server1_ip, server1_port)
    sock2 = create_socket(local2_interface_ip, server2_ip, server2_port)

    # 1 # get file list ###########################################################
    packet, sockaddr = send_and_receive(type=1, number=0, s=0, e=0)
    print("File List:")
    for i in range(0, len(packet[10:].split(b'\x00'))-1):
      index = packet[10:].split(b'\x00')[i].hex()[1:2]
      name = packet[10:].split(b'\x00')[i].decode('utf-8')
      print(index, name)

    # 2 # select file #############################################################
    while True:
      try:
        file_no = int(input("Enter a number: "))
        if file_no not in range(0, len(packet[10:].split(b'\x00'))):
          print("Number not found in file list. Try again.")
        else:
          break # If the file_no is in the range, break the loop and proceed
      except ValueError:
        print("Invalid number. Try again.")
    print("File", file_no, "has been selected. Getting the size information…")

    # 3 # get file size ###########################################################
    packet, sockaddr = send_and_receive(type=2, number=file_no, s=0, e=0)
    n = int(packet[10:].hex(), 16)
    # File 2 is 12345 bytes. Starting to download…
    print("\nFile", file_no, "is", n, "bytes. Starting to download…")

    # 4 # get file data ###########################################################
    '''
    File 2 has been downloaded in 32345 ms. 
    The md5 hash is 595f44fec1e92a71d3e9e77456ba80d1.
    [Other useful statistics about the download]
    '''
    # 1 timer starts
    start_time = time.time()
    # 2 send request get file header to download this file as quickly as possible.
    packet, sockaddr = send_and_receive(type=3, number=file_no, s=1, e=n)

    # 3 During the download, the client should output useful data on the screen such as 
    # transfer speed over each connection, percentage completed, elapsed time, 
    # packet loss rate experienced so far, current/average round-trip times, etc.


    ##########################################################################

    # Start threads for each connection
    # thread1 = threading.Thread(target=handle_transfer, args=(sock1, server1_ip, server1_port))
    # thread2 = threading.Thread(target=handle_transfer, args=(sock2, server2_ip, server2_port))

    # thread1.start()
    # thread2.start()

    # Optionally join threads if you want to wait for them to finish
    # thread1.join()
    # thread2.join()

if __name__ == '__main__':
    main()