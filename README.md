# Packet Handler for Python
With Socket, Send, Recv and Parse data.

# Example Usage

```import sys
from Packet import Packet

class Opcodes:
  LOGIN=0x1
  REGISTER=0x2  
  LOGOUT=0x4
  
  UPLOAD_FILE=0x10
  DOWNLOAD_FILE=0x11
  
  
  
myUsername="EmreDemircan"
myPassword = "123456"
rememberMe = 1
```
## Send with Socket
```
paket = Packet(Opcodes.LOGIN)
paket << myUsername << myPassword << rememberMe

packetSize = len(paket) # bytes must have been sent
```


## Recv with Socket
```
myUsername, myPassword, rememberMe = Packet.ref(str), Packet.ref(str), Packet.ref(int)
paket >> myUsername >> myPassword >> rememberMe
print("opcode: %d" % paket.GetOpcode()) # 0x1 (Opcodes.LOGIN)
print("myUsername: %s" % (myUsername))
print("myPassword: %s" % (myPassword))
print("rememberMe: %s" % (rememberMe))

```

# Output:
```
myUsername: EmreDemircan
myPassword: 123456
rememberMe: 1
```



