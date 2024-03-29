# -*- coding: utf-8 -*-
""" Store data as packet. Encrypt, Compress, Send-Recv(Serialize, Deserialize) it.."""


# https://www.github.com/emrecpp

version = "1.0.9"
__author__ = "Emre Demircan (emrecpp1@gmail.com)"
__date__ = "2023-08-06"
__github__ = "emrecpp"

import sys, time, json, socket, struct
from functools import singledispatch
from datetime import datetime
from enum import IntEnum
try:
    import core.helpers as helper
    from core.DataEnums import EListener
except ImportError:
    import PacketHandler.core.helpers as helper
    from PacketHandler.core.DataEnums import EListener


class PacketManager(object):
    _m_recv:list[EListener] = []
    @staticmethod
    def addListener(listener:EListener):
        PacketManager._m_recv.append(listener)

    @staticmethod
    def getListenerByOpcode(opcode:int):
        for listener in PacketManager._m_recv:
            if listener.opcode == opcode:
                return listener
        return None
    @staticmethod
    def removeListener(listener:EListener):
        if not listener: return
        if listener in PacketManager._m_recv:
            PacketManager._m_recv.remove(listener)
    @staticmethod
    def removeListenerByOpcode(opcode:int):
        PacketManager.removeListener(PacketManager.getListenerByOpcode(opcode=opcode))

class Packet(object):
    storage = bytearray()

    # First 2 bytes : Opcodes [ 0 - (256*256-1) ]
    __INDEX_OF_FLAG           = 2  # 3. byte: Flags (is Packet LittleEndian? Encrypted? Compressed?)
    __INDEX_OF_COUNT_ELEMENTS = 3  # 4. byte: Count of Total Data types
    # Todo: 5. byte: empty for now
    # Todo: 6. byte: empty for now

    _rpos = _wpos = 6
    _m_Encrypt = _m_Compress = _m_PrintErrorLog = False

    Last_SendTime = None  # datetime will stored when Packet Sent
    Last_RecvTime = None  # datetime will stored when Packet Received

    class Flags(IntEnum):
        Encrypted    = 1
        LittleEndian = 2
        Compressed   = 4

    # Maximum a Variable data Size = "\xFF\xFF\xFF\xFF" (4.294.967.295 bytes (4GB))
    def __init__(self, Opcode:int=0, LittleEndian:bool=False, Encrypt:bool=False, Compress:bool=False, PrintErrorLog:bool=False):
        super().__init__()
        self.storage = bytearray()
        self._initNew(newOpcode=Opcode) # init first 6 bytes (
        self._rpos = self._wpos = 6
        self._m_Encrypt, self._m_Compress, self._m_PrintErrorLog = Encrypt, Compress, PrintErrorLog
        self.littleEndian = LittleEndian
        self.overload_append = singledispatch(self.append)
        self.overload_append.register(int, self.append_int)
        self.overload_append.register(str, self.append_str)
        self.overload_append.register(bytearray, self.append_bytearray)
        self.overload_append.register(list, self.append_list)
        self.overload_append.register(dict, self.append_dict)
        self.overload_append.register(bool, self.append_bool)
        self.overload_append.register(bytes, self.append_bytes)

    @property
    def littleEndian(self) -> bool:
        return self.storage[self.__INDEX_OF_FLAG] & self.Flags.LittleEndian

    @littleEndian.setter
    def littleEndian(self, value):
        if value:
            self.storage[self.__INDEX_OF_FLAG] |= self.Flags.LittleEndian
        else:
            self.storage[self.__INDEX_OF_FLAG] &= ~self.Flags.LittleEndian

    def append(self, buffer):
        raise TypeError("Append Unknown Data Type")

    def _initNew(self, newOpcode=None) -> None:
        result_opcode = 0
        if newOpcode:
            result_opcode = newOpcode
        elif self.size() > 0 and self.GetOpcode() != 0:
            result_opcode = self.GetOpcode()
        self.storage.clear()
        del self.storage
        self.storage = bytearray(struct.pack(">H", result_opcode))  # Hard-coded Big Endian

        self.storage.extend(b'\0\0\0\0')
        self._rpos = self._wpos  = 6

    def clear(self) -> None:
        self._initNew()

    def Encrypt(self, seed:int = 0x123) -> None:
        for i in range(2 + 4, self.size()):  # Skip opcode (first 2 bytes) and reserved 4 bytes
            data = self.storage[i]
            encVal = seed + i * 4
            encVal ^= 0xFF

            self.storage[i] = (data + encVal) & 0xFF
        self.storage[self.__INDEX_OF_FLAG] |= self.Flags.Encrypted

    def Decrypt(self, seed:int = 0x123) -> None:
        for i in range(2 + 4, self.size()):  # Skip opcode (first 2 bytes) and reserved 4 bytes
            data = self.storage[i]
            encVal = seed + i * 4
            encVal ^= 0xFF

            self.storage[i] = (data - encVal) & 0xFF

        self.storage[self.__INDEX_OF_FLAG] &= ~self.Flags.Encrypted

    def Compress(self) -> None:
        if (self.storage[self.__INDEX_OF_FLAG] & self.Flags.Compressed) == self.Flags.Compressed:
            return  # if Already Compressed
        import bz2
        self.storage[2 + 4:] = bz2.compress(self.storage[2 + 4:])
        self.storage[self.__INDEX_OF_FLAG] |= self.Flags.Compressed

    def DeCompress(self) -> None:
        if (self.storage[self.__INDEX_OF_FLAG] & self.Flags.Compressed) != self.Flags.Compressed:
            return  # if Already DeCompressed / Not Compressed
        import bz2
        self.storage[2 + 4:] = bz2.decompress(self.storage[2 + 4:])
        self.storage[self.__INDEX_OF_FLAG] &= ~self.Flags.Compressed

    def append_int(self, buffer:int) -> None:
        bf = struct.pack("<I" if self.littleEndian else ">I", buffer)
        self.storage.extend(bf)
        self._wpos += len(bf)

    def append_str(self, buffer:str) -> None:
        bytesBuffer = bytes(buffer, "utf-8")
        bf = struct.pack("%ds" % (len(bytesBuffer)), bytesBuffer)
        self.storage.extend(struct.pack("<I" if self.littleEndian else ">I", len(bf)))
        self.storage.extend(bf)
        self._wpos += len(bf)

    def append_bytearray(self, buffer:bytearray) -> None:
        self.storage.extend(struct.pack("<I" if self.littleEndian else ">I", len(buffer)))
        self.storage.extend(buffer)
        self._wpos += len(buffer)

    def append_list(self, buffer:list) -> None:
        self << json.dumps(buffer)
    def append_dict(self, buffer:dict):
        self << json.dumps(buffer, ensure_ascii=False, indent=None)

    def append_bool(self, buffer:bool) -> None:
        self.storage.extend(b'\x01' if buffer else b'\x00')
        self._wpos += 1

    def append_bytes(self, buffer:bytes) -> None:
        self << bytearray(buffer)


    def __len__(self) -> int:
        return self.size()

    def size(self) -> int:
        return len(self.storage)

    def GetOpcode(self) -> int:
        return 0 if len(self.storage) < 2 else (struct.unpack(">H", self.storage[0:2])[0]) # hard coded big endian

    def GetItemsCount(self) -> int:  # [ 0 - 255 ]
        return int(self.storage[self.__INDEX_OF_COUNT_ELEMENTS]) if self.__INDEX_OF_COUNT_ELEMENTS < self.size() else 0

    def __lshift__(self, value):
        self.overload_append(value)
        COUNT_ELEMENTS = self.storage[self.__INDEX_OF_COUNT_ELEMENTS]
        if COUNT_ELEMENTS + 1 <= 255:
            self.storage[self.__INDEX_OF_COUNT_ELEMENTS] += 1
        return self

    def __rshift__(self, value):
        if value.obj == int:
            Sonuc = self.read_int()
        elif value.obj == str:
            Sonuc = self.read_str()
        elif value.obj == bytearray:
            Sonuc = self.read_bytearray()
        elif value.obj == bytes:
            Sonuc = self.read_bytes()
        elif value.obj == list:
            Sonuc = self.read_list()
        elif value.obj == dict:
            Sonuc = self.read_dict()
        elif value.obj == bool:
            Sonuc = self.read_bool()
        else:
            raise TypeError("Read Unknown Data Type")

        value.obj = Sonuc
        return self

    def readLength(self) -> int:  # Reserved Data Size, in 4 bytes
        return self.read_int()

    def read_int(self) -> int:  # Maximum Integer Value = \xFF\xFF\xFF\xFF = (4.294.967.295)
        if self._rpos + 4 > self.size():
            return 0

        data = struct.unpack("<I" if self.littleEndian else ">I", self.storage[self._rpos:self._rpos + 4])[0]
        self._rpos += 4
        return data

    def read_str(self) -> str:
        ReadLength = self.readLength()
        if ReadLength == None:
            return ""

        data = self.storage[self._rpos:self._rpos + ReadLength].decode('utf-8')
        self._rpos += ReadLength
        return data

    def read_bytearray(self) -> bytearray:
        ReadLength = self.readLength()
        if ReadLength == None:
            return bytearray()
        data = bytearray(self.storage[self._rpos:self._rpos + ReadLength])
        self._rpos += ReadLength
        return data
    def read_bytes(self) -> bytes:
        BYTES = ref(bytearray)
        self >> BYTES
        return bytes(BYTES.obj)

    def read_list(self) -> list:
        STR = ref(str)
        self >> STR
        return json.loads(str(STR))
    def read_dict(self) -> list:
        STR = ref(str)
        self >> STR
        return json.loads(str(STR))

    def read_bool(self) -> bool:
        bool = True if self.storage[self._rpos] == 1 else False
        self._rpos += 1
        return bool

    # waitRecv = if you have a Recv function in thread, then you sent packet will received from this thread received function. So creating new socket, sending and receiving data from new socket. So Thread Recv function can't access this data.
    def Send(self, s, waitRecv=False) -> bool:
        """
        :param s: Send socket
        :param waitRecv: bool
        """
        try:
            if self.size() == 0:
                return False
            if hasattr(s, "_closed") and s._closed:
                if self._m_PrintErrorLog: print("Packet Handler | Connection is already closed!")
                return False

            TargetSocket = s

            if waitRecv:
                SocketCreatedNew = False
                if type(waitRecv) == socket.socket:  # if Socket created we will not close it and we can use it multiple times.
                    TargetSocket = waitRecv
                else:
                    # self_socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVTIMEO, struct.pack("LL", recv_timeout, 0))
                    # self_socket.setsockopt(socket.SOL_SOCKET, socket.SO_SNDTIMEO, struct.pack("LL", send_timeout, 0))

                    SocketCreatedNew = True
                    newSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    # newSocket.connect(s.getsockname())
                    newSocket.connect(s.getpeername())  # Be sure; Server can listen more than 1 socket.
                    TargetSocket = newSocket

            if self._m_Compress and (self.storage[self.__INDEX_OF_FLAG] & self.Flags.Compressed) == 0: self.Compress()
            if self._m_Encrypt and (self.storage[self.__INDEX_OF_FLAG] & self.Flags.Encrypted) == 0: self.Encrypt()

            numberOfBytes = self.size()

            msgLength = struct.pack(">I", self.size()) # Hard-coded Big Endian
            TargetSocket.send(msgLength)  # Sending Packet Size before all data

            totalBytesSent = 0
            while totalBytesSent < numberOfBytes:
                totalBytesSent += TargetSocket.send(self.storage[totalBytesSent:])
            self.Last_SendTime = datetime.now()
            if waitRecv:
                self.Recv(TargetSocket)
                if SocketCreatedNew:
                    TargetSocket.shutdown(socket.SHUT_RDWR)
                    TargetSocket.close()

                return self

            return True
        except (ConnectionError, ConnectionAbortedError, ConnectionRefusedError, ConnectionResetError):
            return False
        except OSError:
            if self._m_PrintErrorLog: print("Packet Handler | Send Failed probably Connection Closed.")
            return False
        except Exception as ERR:
            if self._m_PrintErrorLog: helper.PrintErr("Packet Send Err: %s    " % str(ERR))
            return False

    def Recv(self, s, clear=True) -> bool:
        """
        :param s: Socket to wait Recv
        :param clear: Clear Packet before Receiving data
        """
        try:
            if clear:
                self.clear()
            packetSize = s.recv(4)
            if not packetSize:  # Connection Closed
                return False
            packetSize = struct.unpack(">I", packetSize)[0] # Hard-coded Big Endian

            self.storage.clear()
            totalBytesReceived = 0

            while totalBytesReceived < packetSize:
                ReceivedBytes = s.recv(packetSize - totalBytesReceived)

                if not ReceivedBytes:
                    if self._m_PrintErrorLog: print("Packet Handler | Connection closed while receiving")
                    return False
                self.storage.extend(ReceivedBytes)
                totalBytesReceived += len(ReceivedBytes)

            self.Last_RecvTime = datetime.now()
            if (self.storage[self.__INDEX_OF_FLAG] & self.Flags.Encrypted) == self.Flags.Encrypted: self.Decrypt()
            if (self.storage[self.__INDEX_OF_FLAG] & self.Flags.Compressed) == self.Flags.Compressed: self.DeCompress()
            self._wpos = self.size()
            if self._rpos == 0 and self.size() > 0:
                self._rpos = 6  # Skip Opcode
            listener_if_exists = PacketManager.getListenerByOpcode(self.GetOpcode())
            if listener_if_exists:
                args = listener_if_exists.callback_arguments if listener_if_exists.callback_arguments else ()

                if listener_if_exists.first_argument_packet:
                    args = (self,) + args
                    helper.CallFunc((listener_if_exists.callback, *args))
                else:
                    helper.CallFunc((listener_if_exists.callback, args))
            return True
        except (ConnectionError, ConnectionAbortedError, ConnectionRefusedError, ConnectionResetError):
            return False
        except Exception as ERR:
            if self._m_PrintErrorLog: helper.PrintErr("Packet Recv Err: %s    " % str(ERR))
            return False

    

    def Print(self, Title="", maxPerLine=16, utf_8=True, Flag=1 | 2 | 4) -> str:  # 1 Address, 2 Hex Bytes, 4 ASCII
        """
        :param maxPerLine: How many bytes will show on per line
        :param utf_8: Decode ASCII to Utf-8
        :param Flag: 1 Address, 2 Hex Bytes, 4 ASCII
        :return: printing and returning print string
        """
        try:

            Total = ("*** %s *** (%d)\n" % (Title, self.size())) if Title != "" else ""

            dumpstr = ""
            for addr in range(0, self.size(), maxPerLine):
                d = bytes(self.storage[addr:addr + maxPerLine])
                if (Flag & 1) == 1:
                    line = '%08X: ' % (addr)
                else:
                    line = ""
                if (Flag & 2) == 2:
                    dumpstr = ' '.join('%02X' % hstr for hstr in d)

                line += dumpstr[:8 * 3]
                if len(d) > 8:
                    line += dumpstr[8 * 3:]

                pad = 2
                if len(d) < maxPerLine:
                    pad += 3 * (maxPerLine - len(d))
                if len(d) <= 8:
                    pad += 1
                line += ' ' * pad

                if (Flag & 4) == 4:
                    line += " "
                    if utf_8:
                        try:
                            utf8str = str(bytes(self.storage[addr:addr + maxPerLine]), 'utf-8')
                        except UnicodeDecodeError:
                            utf8str = ' '.join(chr(hstr) for hstr in self.storage[
                                                                     addr:addr + maxPerLine])  # str(self.storage[addr:addr+maxPerLine])
                        listutf8str = list(utf8str)
                        for i in range(len(listutf8str)):
                            # if listutf8str[i] == "\x00" or ord(listutf8str[i]) < 0x20:
                            if ord(listutf8str[i]) <= 0x20:
                                listutf8str[i] = "."
                            i += 1
                        line += "".join(listutf8str)
                    else:
                        for byte in d:
                            if byte > 0x20 and byte <= 0x7E:
                                line += chr(byte)
                            else:
                                line += '.'
                Total += line + "\n"
            print(Total)
            return Total
        except Exception as err:
            helper.PrintErr("Print Error: %s    " % err)
            return ""


class ref():  # We don't have Pointers in Python :(
    obj = None
    def __init__(self, obj): self.obj = obj
    def __get__(self, instance, owner): return self.obj
    def __set__(self, instance, value): self.obj = value
    def __eq__(self, other): return other == self.obj
    def __setattr__(self, key, value): self.__dict__[key] = value
    def __getattr__(self, item): return self.obj
    def __str__(self):  # print("Data: %s" % (data_str))
        return str(self.obj)
    def __int__(self):  # print("Data: %d" % (data_int))
        return self.obj


class EListener(EListener): # for access only packet.py file
    pass