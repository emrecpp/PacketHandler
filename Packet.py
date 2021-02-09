# -*- coding: utf-8 -*-
""" Store data as packet. Send, Recv, Encrypt it. 
"""

version = "1.0.5"
__author__ = "Emre Demircan (emrecpp1@gmail.com)"
__date__ = "2021-02-09"
__github__ = "emrecpp"

import sys, os, time
import socket
from functools import singledispatch
import struct
from datetime import datetime

class Packet(object):
    storage = bytearray()

    # First 2 bytes : Opcodes [0-255*256]
    INDEX_OF_FLAG = 2  # Flag
    INDEX_OF_COUNT_ELEMENTS = 3 # 4. byte: Count of Total Data types
    # Todo: 5. byte: empty
    # Todo: 6. byte: empty

    _rpos, _wpos, encryptEnabled = 6, 6, False
    PrintErrorLog=False

    Last_SendTime = "" # if packet will send, will stored this
    Last_RecvTime = ""
    class Flags:
        Encrypted=1
        isLittleEndian=2

    # Maximum a Variable data Size = "\xFF\xFF\xFF\xFF" (4.294.967.295 bytes (4GB))
    # Opcode Range: [0-255*256]
    m_littleEndian=False
    def __init__(self, opcode=0, littleEndian=False, encryptBeforeSend=False, PrintErrorLog=False):
        super(Packet, self).__init__()
        self._rpos = 6
        self._wpos = 6
        self.encryptBeforeSend=encryptBeforeSend
        self.PrintErrorLog = PrintErrorLog
        self.overload_append = singledispatch(self.append)
        self.overload_append.register(int, self.append_int)
        self.overload_append.register(str, self.append_str)
        self.overload_append.register(bytearray, self.append_bytearray)
        self.storage = bytearray()
        self.storage.clear()
        self.storage.extend(struct.pack(">H", opcode))
        #self.storage.extend(struct.pack("<H", opcode) if littleEndian else struct.pack(">H", opcode))
        self.storage.extend(b'\0\0\0\0')
        self.littleEndian=littleEndian

    @property
    def littleEndian(self):
        return self.m_littleEndian

    @littleEndian.setter
    def littleEndian(self, value):
        self.m_littleEndian=value
        if value:
            self.storage[self.INDEX_OF_FLAG] |= self.Flags.isLittleEndian
        else:
            self.storage[self.INDEX_OF_FLAG] &= ~self.Flags.isLittleEndian

    def append(self, buffer):
        return TypeError("append Unknown Data Type")

    def clear(self) -> None:
        if self.size() > 0 and struct.unpack("<H" if self.littleEndian else ">H", self.storage[0:2])[0] != 0:
            # fmt = '%ds %dx %ds' % (0, 1, len(self.storage)-1)
            # self.storage = bytearray(struct.unpack(fmt, self.storage)[1])
            self.storage = bytearray(self.storage[0:2])
            self.storage.extend(b'\0\0\0\0')
        else:
            self.storage.clear()
            self.storage.extend(b'\0\0\0\0\0\0')
        self._rpos = 6
        self._wpos = 6

    def Encrypt(self) -> None:
        for i in range(2+4,self.size()): # Skip opcode and reserved 4 bytes
            data = self.storage[i]
            encVal = 0x123 + i*4
            encVal ^= 0xFF

            self.storage[i] = (data + encVal) & 0xFF
        self.storage[self.INDEX_OF_FLAG] |= self.Flags.Encrypted
    def Decrypt(self) -> None:
        for i in range(2+4,self.size()): # Skip opcode and reserved 4 bytes
            data = self.storage[i]
            encVal = 0x123 + i*4
            encVal ^= 0xFF

            self.storage[i] = (data-encVal) & 0xFF

        self.storage[self.INDEX_OF_FLAG] &= ~self.Flags.Encrypted
    def append_int(self, buffer) -> None:
        bf = struct.pack("<I", buffer) if self.littleEndian else struct.pack(">I", buffer)
        self.storage.extend(bf)
        self._wpos += len(bf)

    def append_str(self, buffer) -> None:
        bytesBuffer = bytes(buffer, "utf-8")
        bf = struct.pack("%ds" % (len(bytesBuffer)), bytesBuffer)

        self.storage.extend(struct.pack("<I", len(bf)) if self.littleEndian else struct.pack(">I", len(bf)))

        self.storage.extend(bf)
        self._wpos += len(bf)
    def append_bytearray(self, buffer) -> None:

        self.storage.extend(struct.pack("<I",len(buffer)) if self.littleEndian else struct.pack(">I", len(buffer)))

        self.storage.extend(buffer)
        self._wpos += len(buffer)

    def __len__(self) -> int:
        return self.size()

    def size(self) -> int:
        return len(self.storage)

    def GetOpcode(self) -> int:
        return 0 if len(self.storage) < 2 else (struct.unpack("<H",self.storage[0:2])[0] if self.littleEndian else struct.unpack(">H",self.storage[0:2])[0])

    def __lshift__(self, value):
        self.overload_append(value)
        COUNT_ELEMENTS = self.storage[self.INDEX_OF_COUNT_ELEMENTS]
        if COUNT_ELEMENTS +1 < 255:
            self.storage[self.INDEX_OF_COUNT_ELEMENTS] += 1
        return self

    def __rshift__(self, value):
        if self.size() > 0 and self._rpos == 0:  # Skip Opcode
            if self.GetOpcode() != 0: # if opcode is 0 that means we don't have opcode, we have only data
                self._rpos = 6
        if value.obj == int:
            Sonuc = self.read_int()
        elif value.obj == str:
            Sonuc = self.read_str()
        elif value.obj == bytearray:
            Sonuc = self.read_bytearray()
        else:
            return self

        value.obj = Sonuc
        return self

    def readLength(self) -> int: # Reserved Data Size, in 4 bytes
        return self.read_int()

    def read_int(self) -> int:  # Maximum Integer Value = \xFF\xFF\xFF\xFF = (4.294.967.295)
        if self._rpos + 4 > self.size():
            return 0

        data = struct.unpack("<I", self.storage[self._rpos:self._rpos + 4])[0] if self.littleEndian else struct.unpack(">I", self.storage[self._rpos:self._rpos + 4])[0]
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
        data = bytearray(self.storage[self._rpos:self._rpos+ReadLength])
        self._rpos += ReadLength
        return data

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

    # waitRecv = if you have a Recv function in thread, then you sent packet will received from this thread received function. So creating new socket, sending and receiving data from new socket. So Thread Recv function can't access this data.

    def Send(self, s, waitRecv=False) -> bool:
        """
        :param s: Send socket
        :param waitRecv: bool, will it wait Recv after Send
        """
        try:
            if self.size() == 0:
                return False
            if hasattr(s, "_closed") and s._closed:
                if self.PrintErrorLog: print("Packet Handler | Connection is already closed!")
                return False

            msg = struct.pack("<I", self.size()) if self.littleEndian else struct.pack(">I", self.size())

            TargetSocket = s

            if waitRecv:
                SocketCreatedNew = False
                if type(waitRecv) == socket.socket: # if Socket created we will not close it and we can use it multiple times.
                    TargetSocket = waitRecv
                else:
                    # self_socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVTIMEO, struct.pack("LL", recv_timeout, 0))
                    # self_socket.setsockopt(socket.SOL_SOCKET, socket.SO_SNDTIMEO, struct.pack("LL", send_timeout, 0))

                    SocketCreatedNew = True
                    newSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    #newSocket.connect(s.getsockname())
                    newSocket.connect(s.getpeername())  # Be sure; Server can listen more than 1 socket.
                    TargetSocket = newSocket

            TargetSocket.send(msg)
            numberOfBytes = self.size()
            totalBytesSent = 0
            if self.encryptBeforeSend and (self.storage[self.INDEX_OF_FLAG] & self.Flags.Encrypted) ==0: self.Encrypt()

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
            if self.PrintErrorLog: print("Packet Handler | Send Failed probably Connection Closed.")
            return False
        except Exception as ERR:
            if self.PrintErrorLog: self.PrintErr("Packet Send Err: %s    " % str(ERR))
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

            packetSize = struct.unpack("<I", packetSize)[0] if self.littleEndian else struct.unpack(">I", packetSize)[0]
            self.storage.clear()
            totalBytesReceived = 0


            while totalBytesReceived < packetSize:
                ReceivedBytes = s.recv(packetSize-totalBytesReceived)

                if not ReceivedBytes:
                    if self.PrintErrorLog: print("Packet Handler | Connection closed while receiving")
                    return False
                self.storage.extend(ReceivedBytes)
                totalBytesReceived+=len(ReceivedBytes)
            
            self.Last_RecvTime = datetime.now()
            if (self.storage[self.INDEX_OF_FLAG] & self.Flags.Encrypted) == 1: self.Decrypt()


            self._wpos = self.size()
            if self._rpos == 0 and self.size() > 0:
                self._rpos = 6 # Skip Opcode
            return True
        except (ConnectionError, ConnectionAbortedError, ConnectionRefusedError, ConnectionResetError):
            return False
        except Exception as ERR:
            if self.PrintErrorLog: self.PrintErr("Packet Recv Err: %s    " % str(ERR))
            return False
    def PrintErr(self, ERR) -> None:
        exc_type, exc_obj, exc_tb = sys.exc_info();
        fname = exc_tb.tb_frame.f_code.co_filename
        print(ERR, exc_type, fname, exc_tb.tb_lineno)


    def Print(self, maxPerLine=16, utf_8=True, Flag=1|2|4) -> str: # 1 Address, 2 Hex Bytes, 4 ASCII
        """
        :param maxPerLine: How many bytes will show on per line
        :param utf_8: Decode ASCII to Utf-8
        :param Flag: 1 Address, 2 Hex Bytes, 4 ASCII
        :return: printing and returning print string
        """
        try:
            Total = ""
            dumpstr=""
            for addr in range(0, self.size(),maxPerLine):
                d = bytes(self.storage[addr:addr+maxPerLine])
                if (Flag & 1) == 1:
                    line = '%08X: ' % (addr)
                else:
                    line = ""
                if (Flag & 2) == 2:
                    dumpstr = ' '.join('%02X'%hstr for hstr in d)

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
                            utf8str = str(bytes(self.storage[addr:addr+maxPerLine]), 'utf-8')
                        except UnicodeDecodeError:
                            utf8str = ' '.join(chr(hstr) for hstr in self.storage[addr:addr+maxPerLine])#str(self.storage[addr:addr+maxPerLine])
                        listutf8str = list(utf8str)
                        for i in range(len(listutf8str)):
                            #if listutf8str[i] == "\x00" or ord(listutf8str[i]) < 0x20:
                            if ord(listutf8str[i]) <= 0x20:
                                listutf8str[i]="."
                            i+=1
                        line+= "".join(listutf8str)
                    else:
                        for byte in d:
                            if byte > 0x20 and byte <= 0x7E:
                                line += chr(byte)
                            else:
                                line += '.'
                Total+=line+"\n"
            print(Total)
            return Total
        except Exception as err:
            self.PrintErr("Print Error: %s    " % err)
            return ""
