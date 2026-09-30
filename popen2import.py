# pyright: ignore
# type: ignore

import popen2

def popen3(cmd):
    inst = popen2.Popen3(cmd)
    return inst.fromchild, inst.tochild, inst.childerr, inst.pid