# Packet Handler Test by Emre Demircan (https://www.github.com/emrecpp) (https://www.github.com/emrecpp/PacketHandler)
# 2021-04-02 | v1.0.7
from Packet import Packet, ref
import sys, socket, select, time
from threading import Thread

class opcodes:
    LOGIN=100
    LOGOUT=101

HOST, PORT = "127.0.0.1", 2000


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
                ClientSocket.setblocking(0)
                read_list.append(ClientSocket)
            else: # Got new data from already connected socket
                PacketListen = Packet()
                if PacketListen.Recv(s): # Will be automatically Decrypted / UnCompressed if Encrypted or Compressed
                    PacketListen.Print("RECEIVED PACKET (YOUR TITLE)!")
                    if PacketListen.GetOpcode() == opcodes.LOGIN:
                        UserName, Password, RememberMe, Data, Fruits = ref(str), ref(str), ref(bool), ref(bytearray), ref(list)
                        PacketListen >> UserName >> Password >> RememberMe >> Data >> Fruits
                        UserName, Password, RememberMe, Data, Fruits = str(UserName), str(Password), RememberMe.obj, bytearray(Data.obj), ", ".join(Fruits.obj)  # We have to cast ref object to (int, str, bool, bytearray ...)
                        # Note: Can't use bool(RememberMe), this returns True everytime!!!

                        print(f"Username: {UserName}\nPassword: {Password}\nRememberMe: {'Yes' if RememberMe else 'No'}\nData: {str(Data)}\nFruits: {Fruits}")

                else:
                    if ClientSocket in read_list: read_list.remove(ClientSocket) # Remove from read list if socket closed


# *** CLIENT ***
def Client():
    sClient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sClient.connect((HOST, PORT))

    Paket = Packet(opcodes.LOGIN, Encrypt=True, Compress=True)
    Username = "Emre"

    Paket << Username << "123" << True << bytearray(b'\x07\x10BYTES\xFF') << ["Apple", "Banana", "Orange"]
    Paket.Send(sClient)


if __name__ == "__main__":
    thrServer = Thread(target=Server, args=(), name="THR_SERVER")
    thrServer.daemon=True
    thrServer.start()

    Client()
    time.sleep(2000)

