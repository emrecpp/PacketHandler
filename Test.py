# Packet Handler Test by Emre Demircan (https://www.github.com/emrecpp) (https://www.github.com/emrecpp/PacketHandler)
# 2022-01-04 | v1.0.8
from Packet import Packet, ref
import sys, socket, select, time
from threading import Thread

class opcodes:
    LOGIN  = 100
    LOGOUT = 101

HOST, PORT = "127.0.0.1", 2022

# *** SERVER ***
def Server():
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
                    PacketListen.Print("RECEIVED PACKET (YOUR TITLE)!")
                    if PacketListen.GetOpcode() == opcodes.LOGIN:
                        UserName, Password, RememberMe, Data, Fruits = ref(str), ref(str), ref(bool), ref(bytearray), ref(list)
                        PacketListen >> UserName >> Password >> RememberMe >> Data >> Fruits
                        UserName, Password, RememberMe, Data, Fruits = str(UserName), str(Password), RememberMe.obj, bytearray(Data.obj), ", ".join(Fruits.obj)  # We have to cast ref object to (int, str, bool, bytearray ...)
                        # Note: Can't use bool(RememberMe), this returns True everytime!!!

                        print(f"Username: {UserName}\nPassword: {Password}\nRememberMe: {'Yes' if RememberMe else 'No'}\nData: {str(Data)}\nFruits: {Fruits}")
                    elif PacketListen.GetOpcode() == opcodes.LOGOUT:
                        pass
                else:
                    print("Socket number: %d closed." % (ClientSocket.fileno()))
                    if ClientSocket in read_list: read_list.remove(ClientSocket) # Remove from read list if socket closed


# *** CLIENT ***
def Client():
    sClient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sClient.connect((HOST, PORT))
    Paket = Packet(opcodes.LOGIN, Encrypt=True, Compress=True, LittleEndian=True)
    Username = "Emre"

    Paket << Username << "123" << True << bytearray(b'\x07\x10BYTES\xFF') << ["Apple", "Banana", "Orange"]
    ResultSend = Paket.Send(sClient)
    print("Sent [C->S]: %s" % ("Success" if ResultSend else "Fail"))


if __name__ == "__main__":
    thrServer = Thread(target=Server, args=(), name="THR_SERVER", daemon=True)
    thrServer.start()
    Client()
    time.sleep(5)
    sys.exit(0)

