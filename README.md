### rdtp-client

#### TODO List (in order of priority)
- [ ] getting interface ip addreses and ports dynamically
- [ ] one thread can always look for incoming icmp error packets
- [ ] sending first two packets with icmp echo request
- [ ] Add logging
- [X] Add support for multiple servers
- [X] Add support for multiple clients
- [X] Add support for multiple file chunks


#### Description
A simple [RDTP client](https://github.com/streaming-university/rdtp/FileListClient) that can request a file list, file size, and file data from a [RDTP Server](https://github.com/streaming-university/rdtp/FileListServer).

#### Requirements
- Python 3.11.4

#### Pre-Installation
```bash
$ git clone https://github.com/streaming-university/rdtp
$ cat rdtp/FileListServer/readme
$ # Follow the instructions in the readme file to start the server
```

#### Installation
```bash
$ git clone https://github.com/cerebnismus/rdtp-client
$ cd rdtp-client
$ python3.11 -m venv venv
$ source venv/bin/activate
$ pip install -r requirements.txt
```

#### Usage
```bash
$ python3.11 rdtp_client.py <server1_ip>:<server1_port> <server2_ip>:<server2_port>
```

#### RDTP Protocol Specification
```bash
80 bits of RDTP Request & Response Header Format (RDTP):

    0                   1                   2                   3
    0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
   |  Request Type |    File ID(s) |              unused.!         |
   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
   |                          Start Byte                           |
   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
   |                            End Byte                           |
   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
   |     Data ...
   +-+-+-+-+-

  Examples: [Other fields are X (don't care).]

   .Request Types: 
     0 reserved
     1 file list + X + X + X
     2 file size + file id + X + X
     3 file data + file id + start byte + end byte

 ..Response Types: 
    0 reserved
    1 success + total num of files + X + X + data: array of fd
    2 success + file id + X + X + data: size of file (4bytes)
    3 success + file id + start byte + end byte + data: payload
  100 invalid request type
  101 invalid file id
  102 invalid start or end byte
```