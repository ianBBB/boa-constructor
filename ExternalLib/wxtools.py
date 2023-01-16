'''
Created on Jul 28, 2014

@author: cwt
'''

# Code from wxPython-2.8 wx.tools.img2py
import zlib
import io


def crunch_data(data, compressed):
    # compress it?
    if compressed:
        data = zlib.compress(data, 9)

    # convert to a printable format, so it can be in a Python source file
    data = repr(data)

    # This next bit is borrowed from PIL.  It is used to wrap the text intelligently.
    fp = io.StringIO()
    data = data + " "  # buffer for the +1 test
    c = i = 0
    octdigits = "01234567"
    hexdigits = "0123456789abcdef"
    while i < len(data):
        if data[i] != "\\":
            word = data[i]
            i = i + 1
        else:
            if data[i + 1] in octdigits:
                for n in range(2, 5):
                    if data[i + n] not in octdigits:
                        break
                word = data[i:i + n]
                i = i + n
            elif data[i + 1] == 'x':
                for n in range(2, 5):
                    if data[i + n] not in hexdigits:
                        break
                word = data[i:i + n]
                i = i + n
            else:
                word = data[i:i + 2]
                i = i + 2

        l = len(word)
        if c + l >= 78 - 1:
            fp.write("\\\n")
            c = 0
        fp.write(word)
        c = c + l

    # return the formatted compressed data
    return fp.getvalue()
