# -*- coding: utf-8 -*-
""" With Socket, Send, Recv and Parse data
"""

version     = "1.0.0"
__author__  = "Emre Demircan (emrecpp1@gmail.com)"
__date__    = "2020-11-19 11:03:53"

import sys, os, time
import socket
import ctypes
from functools import singledispatch
import struct

class Packet(object):

    storage=bytearray()
    _rpos, _wpos= 0, 0
    useNtohl = True
    # Maximum a Variable data Size = "\xFF\xFF\xFF\xFF" (4.294.967.295 bytes (4GB))

    def __init__(self, opcode=0, useNtohl=True):
        super(Packet, self).__init__()
        self._rpos=0
        self._wpos=0
        self.overload_append = singledispatch(self.append)
        self.overload_append.register(int, self.append_int)
        self.overload_append.register(str, self.append_str)
        self.storage.clear()
        self.storage.append(opcode)
        if opcode != 0:
            self._wpos=1
            self._rpos=1
        self.useNtohl = useNtohl


    def append(self, buffer):
        return TypeError("append Unknown Data Type")


    def clear(self):
        if len(self.storage) > 0 and self.storage[0] != 0:
            #fmt = '%ds %dx %ds' % (0, 1, len(self.storage)-1)
            #self.storage = bytearray(struct.unpack(fmt, self.storage)[1])
            self.storage =bytearray(self.storage[0:1])
            self._rpos = 1
            self._wpos = 1
        else:
            self.storage.clear()
            self._rpos = 0
            self._wpos = 0


    def append_int(self, buffer):
        bf = struct.pack("<I", buffer)
        if self.useNtohl:
            self.storage.extend(struct.pack("<I", socket.htonl(len(bf))))
        else:
            self.storage.extend(struct.pack("<I", len(bf)))

        self.storage.extend(bf)
        self._wpos+=len(bf)


    def append_str(self, buffer):
        bf = struct.pack("%ds" %(len(buffer)), bytes(buffer, "utf-8"))
        if self.useNtohl:
            self.storage.extend(struct.pack("<I", socket.htonl(len(bf))))
        else:
            self.storage.extend(struct.pack("<I", len(buffer)))
        self.storage.extend(bf)
        self._wpos+=len(bf)


    def __len__(self):
        return self.size()


    def size(self):
        return len(self.storage)


    def GetOpcode(self):
        return 0 if len(self.storage) == 0 else self.storage[0]


    def __lshift__(self, value):
        self.overload_append(value)
        return self


    def __rshift__(self, value):
        if self.size() > 0 and self._rpos==0: # Skip Opcode
            self._rpos=1
        if value.obj == int:
            Sonuc = self.read_int()
        elif value.obj==str:
            Sonuc = self.read_str()
        else:
            return self


        value.obj = Sonuc


        return self


    def read_int(self):
        if self._rpos + 4 >= self.size():
            return 0

        ReadLength = struct.unpack("<I", self.storage[self._rpos:self._rpos+4])[0]
        if self.useNtohl:
            ReadLength = socket.ntohl(ReadLength)

        if self._rpos+ReadLength >= self.size():
            return 0

        self._rpos += ReadLength
        data = struct.unpack("<I", self.storage[self._rpos:self._rpos+ReadLength])[0]
        self._rpos += ReadLength
        return data


    def read_str(self):
        if self._rpos + 4 >= self.size():
            return ""
        ReadLength = struct.unpack("<I", self.storage[self._rpos:self._rpos + 4])[0]
        if self.useNtohl:
            ReadLength = socket.ntohl(ReadLength)

        self._rpos += 4
        data= self.storage[self._rpos:self._rpos+ReadLength].decode('utf-8')
        self._rpos += ReadLength
        return data


    class ref(object): # We don't have Pointers in Python :(
        obj=None
        def __init__(self, obj): self.obj = obj
        def __get__(self, instance, owner): return self.obj
        def __set__(self, instance, value): self.obj = value
        def __eq__(self, other): return other == self.obj
        def __setattr__(self, key, value): self.__dict__[key]=value
        def __getattr__(self, item): return self.obj
        def __str__(self): # print("Data: %s" % (data_str))
            return str(self.obj)
        def __int__(self): # print("Data: %d" % (data_int))
            return self.obj

    def Send(self, s):
        try:
            if self.size() == 0:
                return False
            if self.useNtohl:
                msg = struct.pack(">I", socket.ntohl(self.size()))
            else:
                msg = struct.pack(">I", self.size())
            s.send(msg)
            numberOfBytes = len(self.storage)
            totalBytesSent = 0
            while totalBytesSent < numberOfBytes:
                totalBytesSent += s.send(self.storage[totalBytesSent:])
            return True
        except (ConnectionError, ConnectionAbortedError, ConnectionRefusedError, ConnectionResetError):
            return False
        except Exception as ERR:
            exc_type, exc_obj, exc_tb = sys.exc_info(); fname = exc_tb.tb_frame.f_code.co_filename
            print("Packet Send Err: %s    " % str(ERR), exc_type, fname, exc_tb.tb_lineno)

            return False


    def Recv(self, s):
        try:
            packetSize = s.recv(4)
            if not packetSize: # Connection Closed
                return False

            packetSize = struct.unpack(">I", packetSize)[0]
            if self.useNtohl:
                packetSize = socket.ntohl(packetSize)
            self.storage.clear()
            self.storage.extend(s.recv(packetSize))
            self._wpos = len(self.storage)


            return True
        except (ConnectionError, ConnectionAbortedError, ConnectionRefusedError, ConnectionResetError):
            return False
        except Exception as ERR:
            exc_type, exc_obj, exc_tb = sys.exc_info();
            fname = exc_tb.tb_frame.f_code.co_filename
            print("Packet Recv Err: %s    " % str(ERR), exc_type, fname, exc_tb.tb_lineno)
            return False

        
