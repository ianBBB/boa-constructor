import os

def update_copyright(old_date='2006', new_date='2007'):
    os.chdir('..') # Boa root
    for p, d, files in os.walk('.'):
        for f in files:
            f = os.path.join(p, f)
            if not f.endswith('.py'):
                continue
            src = open(f).read()
            c = src.find('# Copyright:   ')
            if c != -1:
                eol = src.find('\n', c)
                d = src[c:eol].find(old_date)
                if d != -1:
                    src = src[:c+d]+new_date+src[c+d+len(new_date):]
                    open(f, 'w').write(src)
                    print('updated', f)
            

if __name__ == '__main__':
    update_copyright()
