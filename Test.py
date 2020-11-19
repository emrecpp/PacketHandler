from Packet import Packet


class Opcodes:
    LOGIN = 0x1
    REGISTER = 0x2
    LOGOUT = 0x4

    UPLOAD_FILE = 0x10
    DOWNLOAD_FILE = 0x11


myUsername = "EmreDemircan"
myPassword = "123456"
rememberMe = 1


paket = Packet(Opcodes.LOGIN)
paket << myUsername << myPassword << rememberMe

packetSize = len(paket) # bytes must have been sent


packet_myUsername, packet_myPassword, packet_rememberMe = Packet.ref(str), Packet.ref(str), Packet.ref(int)
paket >> packet_myUsername >> packet_myPassword >> packet_rememberMe
print("opcode: %d" % paket.GetOpcode()) # 0x1 (Opcodes.LOGIN)
print("myUsername: %s" % (packet_myUsername))
print("myPassword: %s" % (packet_myPassword))
print("rememberMe: %s" % (packet_rememberMe))
print("Packet Size: %d" % (packetSize))
