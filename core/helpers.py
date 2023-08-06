# -*- coding: utf-8 -*-
import sys, os, json, time

def PrintErr(ERR:str) -> None:
    exc_type, exc_obj, exc_tb = sys.exc_info();
    fname = exc_tb.tb_frame.f_code.co_filename
    print(ERR, exc_type, fname, exc_tb.tb_lineno)

def CallFunc(OnClick):
    if OnClick == None: return
    if callable(OnClick) and OnClick.__name__ == "<lambda>":  # lambda ise
        OnClick()
        return
    if OnClick != None:  # and len(OnClick) == 2:
        try:
            if str(type(OnClick)) == '<class \'function\'>':
                OnClick()
            elif str(type(OnClick)) == "<class 'method'>":
                OnClick()
            elif len(OnClick) >= 2:
                f = OnClick[0]
                if OnClick[1] == None:
                    f()
                else:
                    f(*OnClick[1:])
        except TypeError as err:
            if "required positional argument:" in str(err):
                raise Exception(f"Packet Handler Couldn't bind : ({str(err)})")
        except Exception as err:
            PrintErr("PacketHandler Helper CallFunc: " % str(err))
