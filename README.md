# Python Packet Handler
Store data as packet. Send, Recv, Encrypt it.

For C#: https://github.com/emrecpp/DataPacket-CSharp

For C++: https://github.com/emrecpp/DataPacket-CPP

# Example Usage

```import sys
import socket
from Packet import Packet, ref

Sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
Sock.connect(('127.0.0.1', 2000))

class Opcodes:
  LOGIN=0x1
  REGISTER=0x2  
  LOGOUT=0x4
  
  UPLOAD_FILE=0x10
  DOWNLOAD_FILE=0x11  
  
  
myUsername, myPassword, rememberMe, myList, longString = "EmreDemircan", "123456", 1, [1, 2, "Emre", "Python", 3], "7777"*20

```
## Send with Socket
```
paket = Packet(Opcodes.LOGIN, littleEndian=False, Encrypt=True, Compress=True) # You can Encrypt and compress packet before send. It will automatically DeCompressed and Decrypted when received.
paket << myUsername << myPassword << rememberMe << bytearray(b'SOME_EXTRA_DATA') << myList << longString
paket.Send(Sock)
```


## Recv with Socket
```
ClientPacket = Packet()
ClientPacket.Recv(Sock)
myUsername, myPassword, rememberMe, bytearr, myList, myLongString = ref(str), ref(str), ref(int), ref(bytearray), ref(list), ref(str)
ClientPacket >> myUsername >> myPassword >> rememberMe >> bytearr >> myList >> myLongString
myUsername, myPassword, rememberMe, myList, myLongString = str(myUsername), str(myPassword), int(rememberMe), myList.obj, str(myLongString) # You have to cast ref object to your object type(str, int ...)

print("Opcode: %d" % ClientPacket.GetOpcode()) # 0x1 (Opcodes.LOGIN)
print("Username: %s" % (myUsername))
print("Password: %s" % (myPassword))
print("RememberMe: %s" % (rememberMe))
print("Some Extra Data: %s" % str(bytearr))
print("List: %s" % (myList))
print("LongString: %s" % (myLongString))

# Pretty Print and Encryption
paket.Print(maxPerLine=16, Flag=1|2|4) # Flag : [1 Addresses, 2 Hex bytes, 4 ASCII Characters]

paket.Encrypt()
paket.Print()
```

# Output:
```
Opcode: 1
Username: EmreDemircan
Password: 123456
RememberMe: 1
Some Extra Data: bytearray(b'SOME_EXTRA_DATA')
List: [1, 2, 'Emre', 'Python', 3]
LongString: 77777777777777777777777777777777777777777777777777777777777777777777777777777777
```
# Little Endian

## Normal / Decrypted Print:
```
00000000: 00 01 02 07 00 00 0C 00 00 00 45 6D 72 65 44 65   ..........EmreDe
00000010: 6D 69 72 63 61 6E 06 00 00 00 31 32 33 34 35 36   mircan....123456
00000020: 01 00 00 00 0F 00 00 00 53 4F 4D 45 5F 45 58 54   ........SOME_EXT
00000030: 52 41 5F 44 41 54 41 1B 00 00 00 5B 31 2C 20 32   RA_DATA....[1,.2
00000040: 2C 20 22 45 6D 72 65 22 2C 20 22 50 79 74 68 6F   ,."Emre",."Pytho
00000050: 6E 22 2C 20 33 5D 50 00 00 00 37 37 37 37 37 37   n",.3]P...777777
00000060: 37 37 37 37 37 37 37 37 37 37 37 37 37 37 37 37   7777777777777777
00000070: 37 37 37 37 37 37 37 37 37 37 37 37 37 37 37 37   7777777777777777
00000080: 37 37 37 37 37 37 37 37 37 37 37 37 37 37 37 37   7777777777777777
00000090: 37 37 37 37 37 37 37 37 37 37 37 37 37 37 37 37   7777777777777777
000000A0: 37 37 37 37 37 37 37 37 37 37                     7777777777
```
## Compressed
```
00000000: 00 01 06 07 00 00 42 5A 68 39 31 41 59 26 53 59   ......BZh91AY&SY
00000010: 9D 42 0F F9 00 00 0A 7F 80 61 04 80 08 50 04 3F   .B...ù.........a......P...?
00000020: 80 26 06 DC 4A AA 63 94 20 20 00 54 54 D3 47 A8   .&...Ü.J.ª.c........T.T.Ó.G.¨
00000030: D0 0D 19 03 23 D4 07 94 11 4C 9B 49 A0 D3 D2 34   Ð.......#.Ô......L..I. .Ó.Ò.4
00000040: D0 31 00 01 8F 7A 05 29 00 90 BA 74 AD 58 06 E2   Ð.1......z...)....º.t.­.X...â
00000050: B0 61 30 D1 9C 50 27 B5 B7 25 D2 43 07 EA 46 79   °.a.0.Ñ..P.'.µ.·.%.Ò.C...ê.F.y
00000060: 29 50 88 CB 48 38 45 4C 91 5C 94 4C 32 BC 11 E1   ).P..Ë.H.8.E.L..\..L.2.¼...á
00000070: 91 82 3E 2F C5 DC 91 4E 14 24 27 50 83 FE 40      ..>./.Å.Ü..N...$.'.P..þ.@
```
## Encrypted & Compressed Print:
```
00000000: 00 01 07 07 00 00 06 1A 24 F1 E5 F1 05 CE F7 F9   ................$.ñ.å.ñ...Î.÷.ù
00000010: 39 DA A3 89 8C 88 8E FF FC D9 78 F0 74 B8 68 9F   9.Ú.£.....ÿ.ü.Ù.x.ð.t.¸.h.
00000020: DC 7E 5A 2C 96 F2 A7 D4 5C 58 34 84 80 FB 6B C8   Ü.~.Z.,..ò.§.Ô.\.X.4...û.k.È
00000030: EC 25 2D 13 2F DC 0B 94 0D 44 8F 39 8C BB B6 14   ì.%.-.../.Ü......D..9..».¶..
00000040: AC 09 D4 D1 5B 42 C9 E9 BC 48 6E 24 59 00 AA 82   ¬...Ô.Ñ.[.B.É.é.¼.H.n.$.Y...ª.
00000050: 4C F9 C4 61 28 D8 AB 35 33 9D 46 B3 73 52 AA D9   L.ù.Ä.a.(.Ø.«.5.3..F.³.s.R.ª.Ù
00000060: 85 A8 DC 1B 94 80 89 8C CD 94 C8 7C 5E E4 35 01   .¨.Ü.......Í..È.|.^.ä.5..
00000070: AD 9A 52 3F D1 E4 95 4E 10 1C 1B 40 6F E6 24      ­..R.?.Ñ.ä..N.......@.o.æ.$
```


# Big Endian

# Normal / Decrypted Print:
```
00000000: 00 01 00 07 00 00 00 00 00 0C 45 6D 72 65 44 65   ..........EmreDe
00000010: 6D 69 72 63 61 6E 00 00 00 06 31 32 33 34 35 36   mircan....123456
00000020: 00 00 00 01 00 00 00 0F 53 4F 4D 45 5F 45 58 54   ........SOME_EXT
00000030: 52 41 5F 44 41 54 41 00 00 00 1B 5B 31 2C 20 32   RA_DATA....[1,.2
00000040: 2C 20 22 45 6D 72 65 22 2C 20 22 50 79 74 68 6F   ,."Emre",."Pytho
00000050: 6E 22 2C 20 33 5D 00 00 00 50 37 37 37 37 37 37   n",.3]...P777777
00000060: 37 37 37 37 37 37 37 37 37 37 37 37 37 37 37 37   7777777777777777
00000070: 37 37 37 37 37 37 37 37 37 37 37 37 37 37 37 37   7777777777777777
00000080: 37 37 37 37 37 37 37 37 37 37 37 37 37 37 37 37   7777777777777777
00000090: 37 37 37 37 37 37 37 37 37 37 37 37 37 37 37 37   7777777777777777
000000A0: 37 37 37 37 37 37 37 37 37 37                     7777777777
```
## Compressed
```
00000000: 00 01 04 07 00 00 42 5A 68 39 31 41 59 26 53 59   ......BZh91AY&SY
00000010: E0 54 99 37 00 00 01 7F 80 61 04 80 08 50 04 3F   à.T..7.........a......P...?
00000020: 80 26 06 DC 4A AA 63 94 20 20 00 54 52 68 68 0D   .&...Ü.J.ª.c........T.R.h.h..
00000030: 06 20 06 D1 07 94 C4 44 64 03 27 A9 A6 9A 0C D2   ......Ñ....Ä.D.d...'.©.¦....Ò
00000040: 00 0B E9 A8 61 4C 60 00 50 06 F3 A8 06 D1 3C 56   ....é.¨.a.L.`...P...ó.¨...Ñ.<.V
00000050: 94 26 46 5E DD 1C 62 CA 1A 89 E0 39 D0 51 72 6B   .&.F.^.Ý...b.Ê....à.9.Ð.Q.r.k
00000060: 86 C0 00 D9 A5 80 9D 84 2D 49 BD 21 24 9B FE 22   .À...Ù.¥....-.I.½.!.$..þ."
00000070: 2E E4 8A 70 A1 21 C0 A9 32 6E                     ..ä..p.¡.!.À.©.2.n
```
## Encrypted & Compressed Print:
```
00000000: 00 01 05 07 00 00 06 1A 24 F1 E5 F1 05 CE F7 F9   ................$.ñ.å.ñ...Î.÷.ù
00000010: 7C EC 2D C7 8C 88 85 FF FC D9 78 F0 74 B8 68 9F   |.ì.-.Ç....ÿ.ü.Ù.x.ð.t.¸.h.
00000020: DC 7E 5A 2C 96 F2 A7 D4 5C 58 34 84 7E 90 8C 2D   Ü.~.Z.,..ò.§.Ô.\.X.4..~...-
00000030: 22 38 1A E1 13 9C C8 44 60 FB 1B 99 92 82 F0 B2   ".8...á....È.D.`.û......ð.²
00000040: DC E3 BD 78 2D 14 24 C0 0C BE A7 58 B2 79 E0 F6   Ü.ã.½.x.-...$.À...¾.§.X.².y.à.ö
00000050: 30 BE DA EE 69 A4 E6 4A 96 01 54 A9 3C B9 D6 CB   0.¾.Ú.î.i.¤.æ.J....T.©.<.¹.Ö.Ë
00000060: E2 18 54 29 F1 C8 E1 C4 69 81 F1 51 50 C3 22 42   â...T.).ñ.È.á.Ä.i..ñ.Q.P.Ã.".B
00000070: 4A FC 9E 80 AD 29 C4 A9 2E 66                     J.ü...­.).Ä.©...f
```



