import struct

def pack(fmt, *args):
    return struct.pack('<' + fmt, *args)

def unpack(fmt, *args):
    pay, *rest = args
    pay = pay[:struct.calcsize(fmt)]
    return struct.unpack('<' + fmt, pay)


def text(scr, font, txt, pos, clr=(255,255,255)):
    scr.blit(font.render(txt, True, clr), pos)
