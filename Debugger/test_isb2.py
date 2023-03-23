import sys, os
print (os.getcwd())
print (sys.path)


def alsoPrint():
    for n in range(2):
        print('hi also!')
    sys.stdout.flush()



# TODO testing



if __name__ == '__main__':
    for n in range(2):
        print('hi!')
    sys.stdout.flush()
    alsoPrint()
