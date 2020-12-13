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
# or you can send encrypted Packet => paket = Packet(Opcodes.LOGIN, encryptEnabled=True) don't forget you have to pass encryptEnabled=True to receiving Packet.

paket << myUsername << myPassword << rememberMe << bytearray(b'SOME_EXTRA_DATA')

# packetSize = paket.size() # bytes must have been sent
paket.Send(Sock)
```


## Recv with Socket
```
ClientPacket = Packet()
# if Packet is Encrypted => ClientPacket = Packet(encryptEnabled=True)
ClientPacket.Recv(Sock)
myUsername, myPassword, rememberMe, bytearr = Packet.ref(str), Packet.ref(str), Packet.ref(int), Packet.ref(bytearray)
ClientPacket >> myUsername >> myPassword >> rememberMe >> bytearr
myUsername, myPassword, rememberMe = str(myUsername), str(myPassword), int(rememberMe) # You have to cast ref object to your object type(str, int ...)

print("Opcode: %d" % ClientPacket.GetOpcode()) # 0x1 (Opcodes.LOGIN)
print("myUsername: %s" % (myUsername))
print("myPassword: %s" % (myPassword))
print("rememberMe: %s" % (rememberMe))
print("Some Extra Data: %s" % str(bytearr))
print("Packet Size: %d" % (packetSize))

# Pretty Print and Encryption
print("Normal Print:")
paket.Print(maxPerLine=16, Flag=1|2|4) # Flag : [1 Addresses, 2 Hex bytes, 4 ASCII Characters]

print("Encrypted Print:"
paket.Encrypt()
paket.Print()

print("Decrypted Print:")
paket.Decrypt()
paket.Print()

```

# Output:
```
Opcode: 1
myUsername: EmreDemircan
myPassword: 123456
rememberMe: 1
Packet Size: 50

Normal Print:
00000000: 01 00 00 00 0C 45 6D 72 65 44 65 6D 69 72 63 61   .....EmreDemirca
00000010: 6E 00 00 00 06 31 32 33 34 35 36 01 00 00 00 00   n....123456.....
00000020: 00 00 0F 53 4F 4D 45 5F 45 58 54 52 41 5F 44 41   ...SOME_EXTRA_DA
00000030: 54 41                                              TA

Encrypted Print:
00000000: DD D8 D4 D0 D8 0D 31 32 21 FC 19 1D 15 1A 07 01   Ý.Ø.Ô.Ð.Ø...1.2.!.ü............
00000010: 0A 98 94 90 92 B9 B6 B3 B0 AD AA 71 6C 68 64 60   ......¹.¶.³.°.­.ª.q.l.h.d.`
00000020: 5C 58 63 A3 9B 95 89 9F 81 90 88 82 6D 87 68 61   \.X.c.£.........m..h.a
00000030: 70 59                                              pY

Decrypted Print:
00000000: 01 00 00 00 0C 45 6D 72 65 44 65 6D 69 72 63 61   .....EmreDemirca
00000010: 6E 00 00 00 06 31 32 33 34 35 36 01 00 00 00 00   n....123456.....
00000020: 00 00 0F 53 4F 4D 45 5F 45 58 54 52 41 5F 44 41   ...SOME_EXTRA_DA
00000030: 54 41                                              TA

```



