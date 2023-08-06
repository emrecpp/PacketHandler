# Packet Handler Example Usage by Emre Demircan (https://www.github.com/emrecpp) (https://www.github.com/emrecpp/PacketHandler)
# 2023-08-06 | v1.0.9
from Packet import Packet, ref, PacketManager, EListener
import sys, socket, select, time
from threading import Thread

class opcodes:
    LOGIN    = 100
    LOGOUT   = 101
    REGISTER = 102
    DOWNLOAD = 103
    UPLOAD   = 104

HOST, PORT = "127.0.0.1", 1923
packetManager = PacketManager()

def on_logout(packet:Packet):
    username = ref(str)
    packet >> username
    username = username.obj # or username = str(username) (They are SAME for string and integer)
    print(f" ***** My custom Wrapper (Logout): Logging out {username}")

def on_register(packet:Packet, some_text:str, val:int):
    username, password = ref(str), ref(str)
    packet >> username >> password
    username, password = username.obj, password.obj
    print(f" ***** My custom Wrapper (Register): Registering: {username} with password: {password}\n ***** I got some text and val too! ({some_text} and {val})")


# *** SERVER ***
def Server():
    packetManager.addListener(EListener(opcodes.LOGOUT, on_logout))
    packetManager.addListener(EListener(opcodes.REGISTER, on_register, ("some static text", 1234)))
    #packetManager.removeListenerByOpcode(opcodes.LOGOUT)

    sServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sServer.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    sServer.bind((HOST, PORT))
    sServer.listen(10)
    read_list, outputs=[sServer], []
    while True:
        readable, writable, err = select.select(read_list, outputs, [], 1)
        for s in readable:
            if s is sServer: # Got new connection
                ClientSocket, addr = sServer.accept()
                ClientSocket.setblocking(1)
                read_list.append(ClientSocket)
            else: # Got new data from already connected socket
                PacketListen = Packet(PrintErrorLog=True, Compress=True, Encrypt=True, LittleEndian=True)
                if PacketListen.Recv(s): # Will be automatically Decrypted / UnCompressed if Encrypted or Compressed
                    # PacketListen.Print("RECEIVED PACKET (YOUR TITLE)!")
                    if PacketListen.GetOpcode() == opcodes.LOGIN:

                        UserName, Password, RememberMe, Data, Fruits = ref(str), ref(str), ref(bool), ref(bytearray), ref(list)
                        PacketListen >> UserName >> Password >> RememberMe >> Data >> Fruits
                        UserName, Password, RememberMe, Data, Fruits = str(UserName), str(Password), RememberMe.obj, bytearray(Data.obj), ", ".join(Fruits.obj)  # We have to cast ref object to (int, str, bool, bytearray ...)
                        # Note: Can't use bool(RememberMe), this returns True everytime. Use .obj always !!!

                        print(f"Username: {UserName}\nPassword: {Password}\nRememberMe: {'Yes' if RememberMe else 'No'}\nData: {str(Data)}\nFruits: {Fruits}")
                    elif PacketListen.GetOpcode() == opcodes.DOWNLOAD:
                        pass # your code when recv Download packet
                    elif PacketListen.GetOpcode() == opcodes.UPLOAD:
                        pass # your code when recv Upload packet

                else:
                    print("Socket number: %d closed." % (ClientSocket.fileno()))
                    if ClientSocket in read_list: read_list.remove(ClientSocket) # Remove from read list if socket closed


# *** CLIENT ***
def Client():
    sClient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sClient.connect((HOST, PORT))

    # *** Send Login Packet ***
    Paket = Packet(opcodes.LOGIN, Encrypt=True, Compress=True, LittleEndian=True)
    Username = "Emre"
    Paket << Username << "123" << True << bytearray(b'\x07\x10BYTES\xFF') << ["Apple", "Banana", "Orange"]
    ResultSend = Paket.Send(sClient)
    print("Sent [OPCODES.LOGIN] [C->S]: %s" % ("Success" if ResultSend else "Fail"))


    # *** Send Logout Packet ***
    paketLogout = Packet(opcodes.LOGOUT)
    paketLogout << "Emre"
    ResultSend = paketLogout.Send(sClient)
    print("Sent [OPCODES.LOGOUT] [C->S]: %s" % ("Success" if ResultSend else "Fail"))

    # *** Send Register Packet ***
    pktRegister = Packet(opcodes.REGISTER)
    pktRegister << "MyUsername59" << "123581321"
    ResultSend = pktRegister.Send(sClient)
    print("Sent [OPCODES.LOGOUT] [C->S]: %s" % ("Success" if ResultSend else "Fail"))

if __name__ == "__main__":
    thrServer = Thread(target=Server, args=(), name="THR_SERVER", daemon=True)
    thrServer.start()
    Client()
    time.sleep(5)
    sys.exit(0)

