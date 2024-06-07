# import htmllib, formatter, string, os, pprint, types    #orig
import html.parser, os

api_path = '../Docs/wxpython/api'
api_name = 'wxpyapi'

header_hhx = '''<!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML//EN">
<HTML>
<head>
<meta name="GENERATOR" content="BuildAPIHelpBook">
</HEAD><BODY>
<OBJECT type="text/site properties">
 <param name="ImageType" value="Folder">
</OBJECT>
'''

entry_hhx = '''<LI> <OBJECT type="text/sitemap">
<param name="Local" value="%s">
<param name="Name" value="%s">
</OBJECT>
'''

file_hhp = '''[OPTIONS]
Compatibility=1.1
Full-text search=Yes
Contents file=%(n)s.hhc
Compiled file=%(n)s.chm
Default Window=wxHelp
Default topic=index.html
Index file=%(n)s.hhk
Title=wxPython API Documentation

[WINDOWS]
wxHelp=,"%(n)s.hhc","%(n)s.hhk","index.html",,,,,,0x2420,,0x380e,,,,,0,,,
'''

def read_segment(fn, start, end):
    data = open(fn).read()
    begin = data.find(start)+len(start)
    return data[begin:data.find(end, begin)]
    

#-------------------------------------------------------------------------------

def build_project():    
    hhp = file_hhp%{'n':api_name}
    open(os.path.join(api_path, api_name+'.hhp'), 'w').write(hhp)

#-------------------------------------------------------------------------------

def build_contents():
    def traverse(l, r):
        for i in l:
            if isinstance(type(i), list):
                r.append('<UL>'+os.linesep)
                traverse(i, r)
                r.append('</UL>'+os.linesep)
            elif isinstance(type(i), tuple):
                r.append(entry_hhx%i)
            else:
                # raise Exception:
                #     'Unhandled type: %s'%type(i)
                raise TypeError( 'Unhandled type: %s'%type(i))

    data = read_segment(os.path.join(api_path, 'trees.html'),
          '<!-- =========== START OF CLASS HIERARCHY =========== -->',
          '<!-- =========== START OF NAVBAR =========== -->')
    p = APIContentsParser(html.parser.HTMLParser())
    p.feed(data)

    class_hierarchy = []
    traverse(p.current, class_hierarchy)

    data = read_segment(os.path.join(api_path, 'wx-module.html'),
          '<!-- =========== START OF SUBMODULES =========== -->',
          '<!-- =========== START OF CLASSES =========== -->')
    p = APIContentsParser(html.parser.HTMLParser())
    p.feed(data)
    submodules = []
    traverse(p.current, submodules)
    
    hhc = header_hhx+\
          '<UL>'+os.linesep+entry_hhx%('wx-module.html', 'Submodules')+\
          ''.join(submodules)+'</UL>'+os.linesep+\
          '<UL>'+os.linesep+entry_hhx%('trees.html', 'Class Hierarchy')+\
          ''.join(class_hierarchy)+'</UL>'+os.linesep 

    open(os.path.join(api_path, api_name+'.hhc'), 'w').write(hhc)


class APIContentsParser(html.parser.HTMLParser):
    def __init__(self, formatter, verbose=0):
        html.parser.HTMLParser.__init__(self, formatter, verbose)
        
        self.contents = []
        self.history = []
        self.current = self.contents

        self.cur_href = None
        self.li_a_cnt = 0

    def start_li(self, attrs):
        self.li_a_cnt = 0

    def start_a(self, attrs):
        self.li_a_cnt += 1
        if self.li_a_cnt == 1:
            if attrs[0][0] == 'href':
                self.cur_href = attrs[0][1]

    def end_a(self):
        self.cur_href = None
    
    def start_code(self, attrs):
        self.save_bgn()

    def end_code(self):
        text = self.save_end().strip()
        if self.cur_href and text:
            self.current.append( (self.cur_href, text) )
                
    def start_ul(self, attrs):
        self.history.append(self.current)
        self.current = []
        
    def end_ul(self):
        c = self.history.pop()
        c.append(self.current)
        self.current = c

#-------------------------------------------------------------------------------

def build_keywords():
    data = read_segment(os.path.join(api_path, 'indices.html'),
          '<!-- =========== START OF IDENTIFIER INDEX =========== -->',
          '<!-- =========== START OF NAVBAR =========== -->')
    p = APIIndicesParser(html.parser.HTMLParser())
    p.feed(data)
    
    hhk = header_hhx+ '<UL>'+os.linesep+\
          ''.join([entry_hhx%(u, k) for u, k in p.indices])+os.linesep+'</UL>'
    open(os.path.join(api_path, api_name+'.hhk'), 'w').write(hhk)


class APIIndicesParser(html.parser.HTMLParser):
    # def __init__(self, formatter, verbose=0):
    #     html.parser.HTMLParser.__init__(self, formatter, verbose)

    def __init__(self):
        html.parser.HTMLParser.__init__(self)
        
        self.indices = []
        self.cur_href = None
        self.tr_a_cnt = 0
    
    def start_tr(self, attrs):
        self.tr_a_cnt = 0

    def end_tr(self):
        self.tr_a_cnt = 0
        
    def start_a(self, attrs):
        self.tr_a_cnt += 1
        if self.tr_a_cnt == 1:
            if attrs[0][0] == 'href':
                self.cur_href = attrs[0][1]

    def end_a(self):
        self.cur_href = None
    
    def start_code(self, attrs):
        self.save_bgn()

    def end_code(self):
        text = self.save_end().strip()
        if self.cur_href and text:
            self.indices.append( (self.cur_href, text) )

#-------------------------------------------------------------------------------

if __name__ == '__main__':
    print('Building project...')
    build_project()    
    print('Building contents...')
    build_contents()
    print('Building keywords...')
    build_keywords()
