# Python Packet Handler
With Socket, Send, Recv and Parse data.

# Example Usage

```import sys
import socket
from Packet import Packet

Sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
Sock.connect(('127.0.0.1', 2000))

class Opcodes:
  LOGIN=0x1
  REGISTER=0x2  
  LOGOUT=0x4
  
  UPLOAD_FILE=0x10
  DOWNLOAD_FILE=0x11  
  
  
myUsername, myPassword, rememberMe = "EmreDemircan", "123456", 1

```
## Send with Socket
```
paket = Packet(Opcodes.LOGIN)
paket << myUsername << myPassword << rememberMe << bytearray(b'SOME_EXTRA_DATA')

packetSize = paket.size() # bytes must have been sent
paket.Send(Sock)
```


## Recv with Socket
```
ClientPacket = Packet()
ClientPacket.Recv(Sock)
myUsername, myPassword, rememberMe, bytearr = Packet.ref(str), Packet.ref(str), Packet.ref(int), Packet.ref(bytearray)
ClientPacket >> myUsername >> myPassword >> rememberMe >> bytearr
print("Opcode: %d" % ClientPacket.GetOpcode()) # 0x1 (Opcodes.LOGIN)
print("myUsername: %s" % (myUsername))
print("myPassword: %s" % (myPassword))
print("rememberMe: %s" % (rememberMe))
print("Some Extra Data: %s" % str(bytearr))
print("Packet Size: %d" % (packetSize))
```

# Output:
```
Opcode: 1
myUsername: EmreDemircan
myPassword: 123456
rememberMe: 1
Some Extra Data: bytearray(b'SOME_EXTRA_DATA')
Packet Size: 50
```



