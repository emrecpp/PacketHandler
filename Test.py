from Packet import Packet


class Opcodes:
    LOGIN = 0x1
    REGISTER = 0x2
    LOGOUT = 0x4

    UPLOAD_FILE = 0x10
    DOWNLOAD_FILE = 0x11


myUsername = "EmreDemircan"
rememberMe = 1


paket = Packet(Opcodes.LOGIN)
paket << myUsername << "123456" << rememberMe << bytearray(b'SOME_EXTRA_DATA')

packetSize = len(paket) # bytes must have been sent


packet_myUsername, packet_myPassword, packet_rememberMe = Packet.ref(str), Packet.ref(str), Packet.ref(int)
paket >> packet_myUsername >> packet_myPassword >> packet_rememberMe
packet_myUsername, packet_myPassword, packet_rememberMe = str(packet_myUsername), str(packet_myPassword), int(packet_rememberMe) # You have to cast ref object to your object type(str, int ...)
print("Opcode: %d" % paket.GetOpcode()) # 0x1 (Opcodes.LOGIN)
print("myUsername: %s" % (packet_myUsername))
print("myPassword: %s" % (packet_myPassword))
print("rememberMe: %s" % (packet_rememberMe))
print("Packet Size: %d" % (packetSize))


print("Normal Print:")
paket.Print(Flag=1|2|4) # 1 Addresses, 2 Hex bytes, 4 ASCII

print("Encrypted Print:")
paket.Encrypt()
paket.Print()

print("Decrypted Print:")
paket.Decrypt()
paket.Print()
