import sys, os
print (os.getcwd())
print (sys.path)

for n in range(2):
    print('hi!')
sys.stdout.flush()


def test1():
    q = 1
    print ('I')
    print ('am')
    print ('here.')

def test():
    print('Hello')
    print('World!')
    for n in range(1000):
        pass
    print('Message:' +
    test1())
    print('Bye.')
    raise('I refuse to finish!')
    print ('yeah.')

if __name__ == '__main__':
    if 1:
##        test()
        print ('I')
        print ('am')
        print ('here.')
    else:
        import IsolatedDebugger
        dc = IsolatedDebugger.DebuggerController()
        id = dc.createServer()
        conn = IsolatedDebugger.DebuggerConnection(dc, id)
        conn.run('test()', globals(), locals())
        for n in range(3):
            print (conn.getInteractionUpdate())
            conn.set_step_over()
        for n in range(6):
            print(conn.getInteractionUpdate())
            conn.set_step()
        print (conn.getInteractionUpdate())
        conn.set_continue()
        print (conn.getInteractionUpdate())
