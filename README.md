# Python Packet Handler
Store data as packet. Send, Recv, Encrypt it.

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
paket = Packet(Opcodes.LOGIN, littleEndian=False)
paket << myUsername << myPassword << rememberMe << bytearray(b'SOME_EXTRA_DATA')
# paket.Encrypt()   if you want encrypt packet, then encrypt!
paket.Send(Sock)
```


## Recv with Socket
```
ClientPacket = Packet()
ClientPacket.Recv(Sock)
myUsername, myPassword, rememberMe, bytearr = Packet.ref(str), Packet.ref(str), Packet.ref(int), Packet.ref(bytearray)
ClientPacket >> myUsername >> myPassword >> rememberMe >> bytearr
myUsername, myPassword, rememberMe = str(myUsername), str(myPassword), int(rememberMe) # You have to cast ref object to your object type(str, int ...)

print("Opcode: %d" % ClientPacket.GetOpcode()) # 0x1 (Opcodes.LOGIN)
print("myUsername: %s" % (myUsername))
print("myPassword: %s" % (myPassword))
print("rememberMe: %s" % (rememberMe))
print("Some Extra Data: %s" % str(bytearr))

# Pretty Print and Encryption
paket.Print(maxPerLine=16, Flag=1|2|4) # Flag : [1 Addresses, 2 Hex bytes, 4 ASCII Characters]

paket.Encrypt()
paket.Print()


```

# Output:
```
Opcode: 1
myUsername: EmreDemircan
myPassword: 123456
rememberMe: 1
Packet Size: 50


Little Endian
Normal / Decrypted Print:
00000000: 00 01 02 04 00 00 0C 00 00 00 45 6D 72 65 44 65   ..........EmreDe
00000010: 6D 69 72 63 61 6E 06 00 00 00 31 32 33 34 35 36   mircan....123456
00000020: 01 00 00 00 0F 00 00 00 53 4F 4D 45 5F 45 58 54   ........SOME_EXT
00000030: 52 41 5F 44 41 54 41                               RA_DATA

Encrypted Print:
00000000: 00 01 03 04 00 00 D0 C0 BC B8 F9 1D 1E 0D E8 05   ............Ð.À.¼.¸.ù.......è..
00000010: 09 01 06 F3 ED F6 8A 80 7C 78 A5 A2 9F 9C 99 96   ......ó.í.ö...|.x.¥.¢....
00000020: 5D 58 54 50 5B 48 44 40 8F 87 81 75 8B 6D 7C 74   ].X.T.P.[.H.D.@....u..m.|.t
00000030: 6E 59 73 54 4D 5C 45                               nYsTM\E


Big Endian


Normal / Decrypted Print:
00000000: 00 01 00 04 00 00 00 00 00 0C 45 6D 72 65 44 65   ..........EmreDe
00000010: 6D 69 72 63 61 6E 00 00 00 06 31 32 33 34 35 36   mircan....123456
00000020: 00 00 00 01 00 00 00 0F 53 4F 4D 45 5F 45 58 54   ........SOME_EXT
00000030: 52 41 5F 44 41 54 41                               RA_DATA

Encrypted Print:
00000000: 00 01 01 04 00 00 C4 C0 BC C4 F9 1D 1E 0D E8 05   ............Ä.À.¼.Ä.ù.......è..
00000010: 09 01 06 F3 ED F6 84 80 7C 7E A5 A2 9F 9C 99 96   ......ó.í.ö...|.~.¥.¢....
00000020: 5C 58 54 51 4C 48 44 4F 8F 87 81 75 8B 6D 7C 74   \.X.T.Q.L.H.D.O....u..m.|.t
00000030: 6E 59 73 54 4D 5C 45                               nYsTM\E


```



