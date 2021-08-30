#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-
#-------------------------------------------------------------------
# tarfile.py
#
# Module for reading and writing .tar and tar.gz files.
#
# Needs at least Python version 2.2.
#
# Please consult the html documentation in this distribution
# for further details on how to use tarfile.
#
#-------------------------------------------------------------------
# Copyright (C) 2002 Lars Gustäbel <lars@gustaebel.de>
# All rights reserved.
#
# Permission  is  hereby granted,  free  of charge,  to  any person
# obtaining a  copy of  this software  and associated documentation
# files  (the  "Software"),  to   deal  in  the  Software   without
# restriction,  including  without limitation  the  rights to  use,
# copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies  of  the  Software,  and to  permit  persons  to  whom the
# Software  is  furnished  to  do  so,  subject  to  the  following
# conditions:
#
# The above copyright  notice and this  permission notice shall  be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS  IS", WITHOUT WARRANTY OF ANY  KIND,
# EXPRESS OR IMPLIED, INCLUDING  BUT NOT LIMITED TO  THE WARRANTIES
# OF  MERCHANTABILITY,  FITNESS   FOR  A  PARTICULAR   PURPOSE  AND
# NONINFRINGEMENT.  IN  NO  EVENT SHALL  THE  AUTHORS  OR COPYRIGHT
# HOLDERS  BE LIABLE  FOR ANY  CLAIM, DAMAGES  OR OTHER  LIABILITY,
# WHETHER  IN AN  ACTION OF  CONTRACT, TORT  OR OTHERWISE,  ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
#
"""Read from and write to tar format archives.
"""

__version__ = "$Revision$"
# $Source$

version     = "0.6"
__author__  = "Lars Gustäbel (lars@gustaebel.de)"
__date__    = "$Date$"
__cvsid__   = "$Id$"
__credits__ = "Niels Gustäbel for his invaluable support, " \
              "Richard Townsend for endless and patient testing, " \
              "Gustavo Niemeyer for his support and his patches."

#---------
# Imports
#---------
import sys
import os
import builtins
import shutil
import stat
import errno
import time
import struct

try:
    import grp, pwd
except ImportError:
    grp = pwd = None

# We won't need this anymore in Python 2.3
#
# We import the _tarfile extension, that contains
# some useful functions to handle devices and symlinks.
# We inject them into os module, as if we were under 2.3.
#
try:
    import _tarfile
    if _tarfile.mknod is None:
        _tarfile = None
except ImportError:
    _tarfile = None
if _tarfile and not hasattr(os, "mknod"):
    os.mknod = _tarfile.mknod
if _tarfile and not hasattr(os, "major"):
    os.major = _tarfile.major
if _tarfile and not hasattr(os, "minor"):
    os.minor = _tarfile.minor
if _tarfile and not hasattr(os, "makedev"):
    os.makedev = _tarfile.makedev
if _tarfile and not hasattr(os, "lchown"):
    os.lchown = _tarfile.lchown

# XXX remove for release (2.3)
# and not required at all for python 3
# try:
#     True
#     False
# except NameError:
#     True  = 1
#     False = 0

#---------------------------------------------------------
# tar constants
#---------------------------------------------------------
NUL        = "\0"               # the null character
BLOCKSIZE  = 512                # length of processing blocks
RECORDSIZE = BLOCKSIZE * 20     # length of records
MAGIC      = "ustar"            # magic tar string
VERSION    = "00"               # version number

LENGTH_NAME    = 100            # maximum length of a filename
LENGTH_LINK    = 100            # maximum length of a linkname
LENGTH_PREFIX  = 155            # maximum length of the prefix field
MAXSIZE_MEMBER = 0o77777777777  # maximum size of a file (11 octal digits)

REGTYPE  = "0"                  # regular file
AREGTYPE = "\0"                 # regular file
LNKTYPE  = "1"                  # link (inside tarfile)
SYMTYPE  = "2"                  # symbolic link
CHRTYPE  = "3"                  # character special device
BLKTYPE  = "4"                  # block special device
DIRTYPE  = "5"                  # directory
FIFOTYPE = "6"                  # fifo special device
CONTTYPE = "7"                  # contiguous file

GNUTYPE_LONGNAME = "L"          # GNU tar extension for longnames
GNUTYPE_LONGLINK = "K"          # GNU tar extension for longlink
GNUTYPE_SPARSE   = "S"          # GNU tar extension for sparse file

#---------------------------------------------------------
# tarfile constants
#---------------------------------------------------------
SUPPORTED_TYPES = (REGTYPE, AREGTYPE, LNKTYPE,  # file types that tarfile
                   SYMTYPE, DIRTYPE, FIFOTYPE,  # can cope with.
                   CONTTYPE, GNUTYPE_LONGNAME,
                   GNUTYPE_LONGLINK, GNUTYPE_SPARSE,
                   CHRTYPE, BLKTYPE)

REGULAR_TYPES = (REGTYPE, AREGTYPE,             # file types that somehow
                 CONTTYPE, GNUTYPE_SPARSE)      # represent regular files

#---------------------------------------------------------
# Bits used in the mode field, values in octal.
#---------------------------------------------------------
S_IFLNK = 0o120000        # symbolic link
S_IFREG = 0o100000        # regular file
S_IFBLK = 0o060000        # block device
S_IFDIR = 0o040000        # directory
S_IFCHR = 0o020000        # character device
S_IFIFO = 0o010000        # fifo

TSUID   = 0o4000          # set UID on execution
TSGID   = 0o2000          # set GID on execution
TSVTX   = 0o1000          # reserved

TUREAD  = 0o400           # read by owner
TUWRITE = 0o200           # write by owner
TUEXEC  = 0o100           # execute/search by owner
TGREAD  = 0o040           # read by group
TGWRITE = 0o020           # write by group
TGEXEC  = 0o010           # execute/search by group
TOREAD  = 0o004           # read by other
TOWRITE = 0o002           # write by other
TOEXEC  = 0o001           # execute/search by other

#---------------------------------------------------------
# Some useful functions
#---------------------------------------------------------
def nts(s):
    """Convert a null-terminated string buffer to a python string.
    """
    return s.split(NUL, 1)[0]

def calc_chksum(buf):
    """Calculate the checksum for a member's header. It's a simple addition
       of all bytes, treating the chksum field as if filled with spaces.
       buf is a 512 byte long string buffer which holds the header.
    """
    chk = 256                           # chksum field is treated as blanks,
                                        # so the initial value is 8 * ord(" ")
    for c in buf[:148]: chk += ord(c)   # sum up all bytes before chksum
    for c in buf[156:]: chk += ord(c)   # sum up all bytes after chksum
    return chk

def copyfileobj(src, dst, length=None):
    """Copy length bytes from fileobj src to fileobj dst.
       If length is None, copy the entire content.
    """
    if length == 0:
        return
    if length is None:
        shutil.copyfileobj(src, dst)
        return

    BUFSIZE = 16 * 1024
    blocks, remainder = divmod(length, BUFSIZE)
    for b in range(blocks):
        buf = src.read(BUFSIZE)
        if len(buf) < BUFSIZE:
            raise IOError("end of file reached")
        dst.write(buf)

    if remainder != 0:
        buf = src.read(remainder)
        if len(buf) < remainder:
            raise IOError("end of file reached (%d)"%(remainder-len(buf)))
        dst.write(buf)
    return

filemode_table = (
    (S_IFLNK, "l",
     S_IFREG, "-",
     S_IFBLK, "b",
     S_IFDIR, "d",
     S_IFCHR, "c",
     S_IFIFO, "p"),
    (TUREAD,  "r"),
    (TUWRITE, "w"),
    (TUEXEC,  "x", TSUID, "S", TUEXEC|TSUID, "s"),
    (TGREAD,  "r"),
    (TGWRITE, "w"),
    (TGEXEC,  "x", TSGID, "S", TGEXEC|TSGID, "s"),
    (TOREAD,  "r"),
    (TOWRITE, "w"),
    (TOEXEC,  "x", TSVTX, "T", TOEXEC|TSVTX, "t"))

def filemode(mode):
    """Convert a file's mode to a string of the form
       -rwxrwxrwx.
       Used by TarFile.list()
    """
    s = ""
    for t in filemode_table:
        while True:
            if mode & t[0] == t[0]:
                s += t[1]
            elif len(t) > 2:
                t = t[2:]
                continue
            else:
                s += "-"
            break
    return s

if os.sep != "/":
    normpath = lambda path: os.path.normpath(path).replace(os.sep, "/")
else:
    normpath = os.path.normpath

class TarError(Exception):
    """General exception for extract errors"""
    pass
class ReadError(Exception):
    """Exception for unreadble tar archives"""
    pass
class CompressionError(Exception):
    """Exception for unavailable compression methods"""
    pass
class StreamError(Exception):
    """Exception for misuse of stream-like TarFiles"""
    pass

error = (TarError, ReadError, CompressionError, StreamError)

#--------------------
# exported functions
#--------------------
def open(name=None, mode="r", fileobj=None, bufsize=20*512):
    """Open a tar archive for reading, writing or appending. Return
       an appropriate TarFile class.

       mode:
       'r'          open for reading with transparent compression
       'r:'         open for reading exclusively uncompressed
       'r:gz'       open for reading with gzip compression
       'a'          open for appending
       'w' or 'w:'  open for writing without compression
       'w:gz'       open for writing with gzip compression
       'r|'         open an uncompressed stream of tar blocks for reading
       'r|gz'       open a gzip compressed stream of tar blocks
       'w|'         open an uncompressed stream for writing
       'w|gz'       open a gzip compressed stream for writing
    """
    if not name and not fileobj:
        raise ValueError("nothing to open")

    if ":" in mode:
        filemode, comptype = mode.split(":")
        filemode = filemode or "r"
        comptype = comptype or "tar"

        if "%sopen" % comptype in globals():
            func = eval("%sopen" % comptype)
        else:
            raise CompressionError("unknown compression type %r" % comptype)
        return func(name, filemode, fileobj)

    elif "|" in mode:
        filemode, comptype = mode.split("|")
        filemode = filemode or "r"
        comptype = comptype or "tar"

        if filemode not in "rw":
            raise ValueError("mode must be 'r' or 'w'")

        t = TarFile(name, filemode,
                    _Stream(name, filemode, comptype, fileobj, bufsize))
        t._extfileobj = False
        return t

    elif mode == "r":
        findcomp = lambda f: f[-4:] == "open" and f[:-4]
        comptypes = list(filter(findcomp, list(globals().keys())))
        comptypes = list(map(findcomp, comptypes))
        for comptype in comptypes:
            func = eval("%sopen" % comptype)
            try:
                return func(name, "r", fileobj)
            except error:
                continue
        raise ReadError("file could not be opened successfully")

    elif mode in "aw":
        return taropen(name, mode, fileobj)

    raise ValueError("undiscernible mode")

def taropen(name, mode="r", fileobj=None):
    """Open uncompressed tar archive name for reading or writing.
    """
    if len(mode) > 1 or mode not in "raw":
        raise ValueError("mode must be 'r', 'a' or 'w'")
    return TarFile(name, mode, fileobj)

def gzopen(name, mode="r", fileobj=None, compresslevel=9):
    """Open gzip compressed tar archive name for reading or writing.
       Appending is not allowed.
    """
    if len(mode) > 1 or mode not in "raw":
        raise ValueError("mode must be 'r', 'a' or 'w'")

    try:
        import gzip
    except ImportError:
        raise CompressionError("gzip module is not available")

    pre, ext = os.path.splitext(name)
    pre = os.path.basename(pre)
    if ext == ".tgz":
        ext = ".tar"
    if ext == ".gz":
        ext = ""
    tarname = pre + ext

    tarsrc = None
    if fileobj is None:
        if mode == 'a':
            # to emulate an tar.gz file append
            fileobj = io.StringIO(builtins.file(name, "rb").read())
            tarsrc = taropen(tarname, "r", gzip.GzipFile(name, "rb", 
                  compresslevel, fileobj))

            mode = 'w'
        
        fileobj = builtins.file(name, mode+"b")

    if mode != "r":
        name = tarname

    try:
        t = taropen(tarname, mode, gzip.GzipFile(tarname, mode+"b", compresslevel, fileobj))
    except IOError:
        raise ReadError("not a gzip file")
    
    # copy existing entries when appending
    if tarsrc:
        for m in tarsrc.getmembers():
            t.addfile(m, tarsrc.extractfile(m))

    t._extfileobj = False
    
    return t

def gzopena(name, mode="a", fileobj=None, compresslevel=9):
    """Open gzip compressed tar archive name for appending.
    """
    #if len(mode) > 1 or mode not in "a":
    #    raise ValueError, "mode must be 'r', 'a' or 'w'"

    try:
        import gzip
    except ImportError:
        raise CompressionError("gzip module is not available")

    pre, ext = os.path.splitext(name)
    pre = os.path.basename(pre)
    if ext == ".tgz":
        ext = ".tar"
    if ext == ".gz":
        ext = ""
    tarname = pre + ext

    if fileobj is None:
        if mode == 'a':
            # to emulate an tar.gz file append
            fileobj = builtins.file(name, "wb")
            
            gzipmode = 'w'
        else:
            gzipmode = mode
        
        

    if mode != "r":
        name = tarname

    try:
        t = taropen(tarname, mode, gzip.GzipFile(name, mode + "b",
                                                 compresslevel, fileobj))
    except IOError:
        raise ReadError("not a gzip file")
    t._extfileobj = False
    return t
def bz2open(name, mode="r", fileobj=None, compresslevel=9):
    """Open bzip2 compressed tar archive name for reading or writing.
       Appending is not allowed.
    """
    if len(mode) > 1 or mode not in "rw":
        raise ValueError("mode must be 'r' or 'w'.")

    try:
        import bz2
    except ImportError:
        raise CompressionError("bz2 module is not available")

    pre, ext = os.path.splitext(name)
    pre = os.path.basename(pre)
    if ext == ".tbz2":
        ext = ".tar"
    if ext == ".bz2":
        ext = ""
    tarname = pre + ext

    if fileobj is not None:
        raise ValueError("no support for external file objects")

    try:
        t = taropen(tarname, mode, bz2.BZ2File(name, mode + "b"))
    except IOError:
        raise ReadError("not a bzip2 file")
    return t

def is_tarfile(name):
    """Return True if name points to a tar archive that we
       are able to handle, else return False.
    """
    try:
        t = open(name)
        t.close()
        return True
    except error:
        return False

#---------------------------
# internal stream interface
#---------------------------
class _LowLevelFile:
    """Low-level file object. Supports reading and writing.
       It is used instead of a regular file object for streaming
       access.
    """

    def __init__(self, name, mode):
        mode = {
            "r": os.O_RDONLY,
            "w": os.O_WRONLY | os.O_CREAT,
        }[mode]
        if hasattr(os, "O_BINARY"):
            mode |= os.O_BINARY
        self.fd = os.open(name, mode)

    def close(self):
        os.close(self.fd)

    def read(self, size):
        return os.read(self.fd, size)

    def write(self, s):
        os.write(self.fd, s)

class _Stream:
    """Class that serves as an adapter between TarFile and
       a stream-like object.  The stream-like object only
       needs to have a read() or write() method and is accessed
       blockwise.  Use of gzip compression is possible.
       A stream-like object could be for example: sys.stdin,
       sys.stdout, a socket, a tape device etc.

       _Stream is intended to be used only internally.
    """

    def __init__(self, name, mode, type, fileobj, bufsize):
        """Construct a _Stream object.
        """
        self._extfileobj = True
        if fileobj is None:
            fileobj = _LowLevelFile(name, mode)
            self._extfileobj = False

        self.name    = name
        self.mode    = mode
        self.type    = type
        self.fileobj = fileobj
        self.bufsize = bufsize
        self.buf     = ""
        self.pos     = 0
        self.closed  = False

        if type == "gz":
            try:
                import zlib
            except ImportError:
                raise CompressionError("zlib module is not available")
            self.zlibmod = zlib
            self.crc = zlib.crc32("")
            if mode == "r":
                self._init_read_gz()
            else:
                self._init_write_gz()

    def __del__(self):
        if not self.closed:
            self.close()

    def _init_write_gz(self):
        """Initialize for writing with gzip compression.
        """
        zlib = self.zlibmod
        self.zlib = zlib.compressobj(9, zlib.DEFLATED,
                                        -zlib.MAX_WBITS,
                                        zlib.DEF_MEM_LEVEL,
                                        0)
        timestamp = struct.pack("<L", int(time.time()))
        self.__write("\037\213\010\010%s\002\377" % timestamp)
        if self.name.endswith(".gz"):
            self.name = self.name[:-3]
        self.__write(self.name + NUL)

    def write(self, s):
        """Write string s to the stream.
        """
        if self.type == "gz":
            self.pos += len(s)
            self.crc = self.zlibmod.crc32(s, self.crc)
            s = self.zlib.compress(s)
        self.__write(s)

    def __write(self, s):
        """Write string s to the stream if a whole new block
           is ready to be written.
        """
        self.buf += s
        while len(self.buf) > self.bufsize:
            self.fileobj.write(self.buf[:self.bufsize])
            self.buf = self.buf[self.bufsize:]

    def close(self):
        """Close the _Stream object. No operation should be
           done on it afterwards.
        """
        if self.closed:
            return

        if self.mode == "w" and self.buf:
            if self.type == "gz":
                self.buf += self.zlib.flush()
            self.fileobj.write(self.buf)
            self.buf = ""
            if self.type == "gz":
                self.fileobj.write(struct.pack("<l", self.crc))
                self.fileobj.write(struct.pack("<l", self.pos))

        if not self._extfileobj:
            self.fileobj.close()

        self.fileobj = None

    def _init_read_gz(self):
        """Initialize for reading a gzip compressed fileobj.
        """
        self.zlib = self.zlibmod.decompressobj(-self.zlibmod.MAX_WBITS)
        self.dbuf = ""

        # taken from gzip.GzipFile with some alterations
        if self.__read(2) != "\037\213":
            raise ReadError("not a gzip file")
        if self.__read(1) != "\010":
            raise CompressionError("unsupported compression method")

        flag = ord(self.__read(1))
        self.__read(6)

        if flag & 4:
            xlen = ord(self.__read(1)) + 256 * ord(self.__read(1))
            self.read(xlen)
        if flag & 8:
            while True:
                s = self.__read(1)
                if not s or s == NUL: break
        if flag & 16:
            while True:
                s = self.__read(1)
                if not s or s == NUL: break
        if flag & 2:
            self.__read(2)

    def tell(self):
        """Return the stream's file pointer position.
        """
        return self.pos

    def seek(self, pos=0):
        """Set the stream's file pointer to pos. Negative seeking
           is forbidden.
        """
        if pos - self.pos >= 0:
            self.read(pos - self.pos)
        else:
            raise StreamError("seeking backwards is not allowed")
        return self.pos

    def read(self, size=None):
        """Return the next size number of bytes from the stream.
           If size is not defined, return all bytes of the stream
           up to EOF.
        """
        if size is None:
            s = []
            while True:
                buf = self._read(self.bufsize)
                if not buf: break
                s.append(buf)
            buf = "".join(s)
        else:
            buf = self._read(size)
        self.pos += len(buf)
        return buf

    def _read(self, size):
        """Return size bytes from the stream. gzip compression is
           handled here.
        """
        if self.type != "gz":
            return self.__read(size)

        while len(self.dbuf) < size:
            buf = self.__read(1024)
            if not buf: break
            self.dbuf += self.zlib.decompress(buf)
        buf = self.dbuf[:size]
        self.dbuf = self.dbuf[size:]
        return buf

    def __read(self, size):
        """Return size bytes from stream. If internal buffer is empty,
           read another block from the stream.
        """
        while len(self.buf) < size:
            buf = self.fileobj.read(self.bufsize)
            if not buf: break
            self.buf += buf
        buf = self.buf[:size]
        self.buf = self.buf[size:]
        return buf

#------------------
# Exported Classes
#------------------
class TarInfo:
    """Informational class which holds the details about an
       archive member given by a tar header block.
       TarInfo instances are returned by TarFile.getmember(),
       TarFile.getmembers() and TarFile.gettarinfo() and are
       usually created internally.
    """

    def __init__(self, name=""):
        """Construct a TarInfo instance. name is the optional name
           of the member.
        """

        self.name     = name       # member name (dirnames must end with '/')
        self.mode     = 0o666       # file permissions
        self.uid      = 0          # user id
        self.gid      = 0          # group id
        self.size     = 0          # file size
        self.mtime    = 0          # modification time
        self.chksum   = 0          # header checksum
        self.type     = REGTYPE    # member type
        self.linkname = ""         # link name
        self.uname    = "user"     # user name
        self.gname    = "group"    # group name
        self.devmajor = 0          #-
        self.devminor = 0          #-for use with CHRTYPE and BLKTYPE
        self.prefix   = ""         # prefix to filename or holding information
                                   # about sparse files

        self.offset   = 0          # the tar header starts here
        self.offset_data = 0       # the optional file's data starts here
        
        # zipfile compatibility
        self.filename = name 

    def getheader(self):
        """Return a tar header block as a 512 byte string.
        """
        name = self.name
        if self.isdir() and name[-1:] != "/":
            name += "/"
        # The following code was contributed by Detlef Lannert.
        parts = []
        for value, fieldsize in (
                (name, 100),
                ("%07o" % (self.mode & 0o7777), 8),
                ("%07o" % self.uid, 8),
                ("%07o" % self.gid, 8),
                ("%011o" % self.size, 12),
                ("%011o" % self.mtime, 12),
                ("        ", 8),
                (self.type, 1),
                (self.linkname, 100),
                (MAGIC, 6),
                (VERSION, 2),
                (self.uname, 32),
                (self.gname, 32),
                ("%07o" % self.devmajor, 8),
                ("%07o" % self.devminor, 8),
                (self.prefix, 155)
                ):
            l = len(value)
            parts.append(value + (fieldsize - l) * NUL)

        buf = "".join(parts)
        chksum = calc_chksum(buf)
        buf = buf[:148] + "%06o\0" % chksum + buf[155:]
        buf += (512 - len(buf)) * NUL
        self.buf = buf
        return buf

    def isreg(self):
        return self.type in REGULAR_TYPES
    def isfile(self):
        return self.isreg()
    def isdir(self):
        return self.type == DIRTYPE
    def issym(self):
        return self.type == SYMTYPE
    def islnk(self):
        return self.type == LNKTYPE
    def ischr(self):
        return self.type == CHRTYPE
    def isblk(self):
        return self.type == BLKTYPE
    def isfifo(self):
        return self.type == FIFOTYPE
    def issparse(self):
        return self.type == GNUTYPE_SPARSE
    def isdev(self):
        return self.type in (CHRTYPE, BLKTYPE, FIFOTYPE)
# class TarInfo

class TarFile:
    """The TarFile Class provides an interface to tar archives.
    """

    debug = 0                   # May be set from 0 (no msgs) to 3 (all msgs)

    dereference = False         # If true, add content of linked file to the
                                # tar file, else the link.

    ignore_zeros = False        # If true, skips empty or invalid blocks and
                                # continues processing.

    errorlevel = 0              # If 0, fatal errors only appear in debug
                                # messages (if debug >= 0). If > 0, errors
                                # are passed to the caller as exceptions.

    posix = True                # If True, generates POSIX.1-1990-compliant
                                # archives (no GNU extensions!)

    def __init__(self, name=None, mode="r", fileobj=None):
        self.name = name

        if len(mode) > 1 or mode not in "raw":
            raise ValueError("mode must be 'r', 'a' or 'w'")
        self._mode = mode
        self.mode = {"r": "rb", "a": "r+b", "w": "wb"}[mode]

        if not fileobj:
            fileobj = builtins.file(self.name, self.mode)
            self._extfileobj = False
        else:
            if self.name is None and hasattr(fileobj, "name"):
                self.name = fileobj.name
            if hasattr(fileobj, "mode"):
                self.mode = fileobj.mode
            self._extfileobj = True
        self.fileobj = fileobj

        # Init datastructures
        self.closed      = False
        self.members     = []       # list of members as TarInfo instances
        self.membernames = []       # names of members
        self.chunks      = [0]      # chunk cache
        self._loaded     = False    # flag if all members have been read
        self.offset      = 0       # current position in the archive file
        self.inodes      = {}       # dictionary caching the inodes of
                                    # archive members already added

        if self._mode == "r":
            self.firstmember = None
            self.firstmember = next(self)

        if self._mode == "a":
            # Move to the end of the archive,
            # before the first empty block.
            self.firstmember = None
            while True:
                try:
                    tarinfo = next(self)
                except ReadError:
                    self.fileobj.seek(0)
                    break
                if tarinfo is None:
                    self.fileobj.seek(- BLOCKSIZE, 1)
                    break
            self._loaded = True

    def close(self):
        """Close the TarFile instance and do some cleanup.
        """
        if self.closed:
            return

        if self._mode in "aw":
            self.fileobj.write(NUL * (BLOCKSIZE * 2))
            self.offset += (BLOCKSIZE * 2)
            # fill up the end with zero-blocks
            # (like option -b20 for tar does)
            blocks, remainder = divmod(self.offset, RECORDSIZE)
            if remainder > 0:
                self.fileobj.write(NUL * (RECORDSIZE - remainder))

        if not self._extfileobj:
            self.fileobj.close()
        self.closed = True

    def __next__(self):
        """Return the next member from the archive. Return None if the
           end of the archive is reached. Normally there is no need to
           use this method directly, because the TarFile class can be
           used as an iterator.
        """
        self._check("ra")
        if self.firstmember is not None:
            r = self.firstmember
            self.firstmember = None
            return r

        # Read the next block.
        self.fileobj.seek(self.chunks[-1])
        while True:
            buf = self.fileobj.read(BLOCKSIZE)
            if not buf:
                return None
            try:
                tarinfo = self._buftoinfo(buf)
            except ValueError:
                if self.ignore_zeros:
                    if buf.count(NUL) == BLOCKSIZE:
                        adj = "empty"
                    else:
                        adj = "invalid"
                    self._dbg(2, "0x%X: %s block\n" % (self.offset, adj))
                    self.offset += BLOCKSIZE
                    continue
                else:
                    # Block is empty or unreadable.
                    if self.chunks[-1] == 0:
                        # If the first block is invalid. That does not
                        # look like a tar archive we can handle.
                        raise ReadError("empty, unreadable or compressed file")
                    return None
            break

        # If the TarInfo instance contains a GNUTYPE longname or longlink
        # statement, we must process this first.
        if tarinfo.type in (GNUTYPE_LONGLINK, GNUTYPE_LONGNAME):
            tarinfo = self._proc_gnulong(tarinfo, tarinfo.type)

        if tarinfo.isreg() and tarinfo.name[:-1] == "/":
            # some old tar programs don't know DIRTYPE
            tarinfo.type = DIRTYPE

        if tarinfo.issparse():
            # Sparse files need some care,
            # due to the possible extra headers.
            tarinfo.offset = self.offset
            self.offset += BLOCKSIZE
            origsize = self._proc_sparse(tarinfo)
            tarinfo.offset_data = self.offset
            blocks, remainder = divmod(tarinfo.size, BLOCKSIZE)
            if remainder:
                blocks += 1
            self.offset += blocks * BLOCKSIZE
            tarinfo.size = origsize
        else:
            tarinfo.offset = self.offset
            self.offset += BLOCKSIZE
            tarinfo.offset_data = self.offset
            if tarinfo.isreg():
                # Skip the following data blocks.
                blocks, remainder = divmod(tarinfo.size, BLOCKSIZE)
                if remainder:
                    blocks += 1
                self.offset += blocks * BLOCKSIZE

        self.members.append(tarinfo)
        self.membernames.append(tarinfo.name)
        self.chunks.append(self.offset)
        return tarinfo

    def getmember(self, name):
        """Return a TarInfo instance for member name.
        """
        self._check("r")
        if name not in self.membernames and not self._loaded:
            self._load()
        if name not in self.membernames:
            raise KeyError("filename %r not found" % name)
        return self._getmember(name)

    def getmembers(self):
        """Return all members in the archive as a list of TarInfo
           objects.
        """
        self._check("r")
        if not self._loaded:    # if we want to obtain a list of
            self._load()        # all members, we first have to
                                # scan the whole archive.
        return self.members

    def getnames(self):
        """Return all members in the archive as a list of their names.
        """
        self._check("r")
        if not self._loaded:
            self._load()
        return self.membernames

    def gettarinfo(self, name, arcname=None):
        """Create and return a TarInfo object that represents the existing
           physical file name. The TarInfo object and the file's data can
           be added to the TarFile using addfile(). arcname specifies the
           pathname under which the member shall be stored in the archive.

        """
        self._check("aw")
        # Building the name of the member in the archive.
        # Backward slashes are converted to forward slashes,
        # Absolute paths are turned to relative paths.
        if arcname is None:
            arcname = name
        arcname = normpath(arcname)
        drv, arcname = os.path.splitdrive(arcname)
        while arcname[0:1] == "/":
            arcname = arcname[1:]

        # Now, fill the TarInfo instance with
        # information specific for the file.
        tarinfo = TarInfo()

        # Use os.stat or os.lstat, depending on platform
        # and if symlinks shall be resolved.
        if hasattr(os, "lstat") and not self.dereference:
            statres = os.lstat(name)
        else:
            statres = os.stat(name)
        linkname = ""

        stmd = statres.st_mode
        if stat.S_ISREG(stmd):
            inode = (statres.st_ino, statres.st_dev)
            if inode in list(self.inodes.keys()) and not self.dereference:
                # Is it a hardlink to an already
                # archived file?
                type = LNKTYPE
                linkname = self.inodes[inode]
            else:
                # The inode is added only if its valid.
                # For win32 it is always 0.
                type = REGTYPE
                if inode[0]:
                    self.inodes[inode] = arcname
        elif stat.S_ISDIR(stmd):
            type = DIRTYPE
            if arcname[-1:] != "/":
                arcname += "/"
        elif stat.S_ISFIFO(stmd):
            type = FIFOTYPE
        elif stat.S_ISLNK(stmd):
            type = SYMTYPE
            linkname = os.readlink(name)
        elif stat.S_ISCHR(stmd):
            type = CHRTYPE
        elif stat.S_ISBLK(stmd):
            type = BLKTYPE
        else:
            return None

        # Fill the TarInfo instance with all
        # information we can get.
        tarinfo.name  = arcname
        tarinfo.mode  = stmd
        tarinfo.uid   = statres.st_uid
        tarinfo.gid   = statres.st_gid
        tarinfo.size  = statres.st_size
        tarinfo.mtime = statres.st_mtime
        tarinfo.type  = type
        tarinfo.linkname = linkname
        if pwd:
            try:
                tarinfo.uname = pwd.getpwuid(tarinfo.uid)[0]
            except KeyError:
                pass
        if grp:
            try:
                tarinfo.gname = grp.getgrgid(tarinfo.gid)[0]
            except KeyError:
                pass

        if type in (CHRTYPE, BLKTYPE):
            if hasattr(os, "major") and hasattr(os, "minor"):
                tarinfo.devmajor = os.major(statres.st_rdev)
                tarinfo.devminor = os.minor(statres.st_rdev)
        return tarinfo

    def list(self, verbose=1):
        """Print a formatted listing of TarFile's contents
           to sys.stdout.
        """
        self._check("r")

        for tarinfo in self:
            if verbose:
                print(filemode(tarinfo.mode), end=' ')
                print(tarinfo.uname + "/" + tarinfo.gname, end=' ')
                if tarinfo.ischr() or tarinfo.isblk():
                    print("%10s" % (str(tarinfo.devmajor) + "," + str(tarinfo.devminor)), end=' ')
                else:
                    print("%10d" % tarinfo.size, end=' ')
                print("%d-%02d-%02d %02d:%02d:%02d" \
                      % time.localtime(tarinfo.mtime)[:6], end=' ')

            print(tarinfo.name, end=' ')

            if verbose:
                if tarinfo.issym():
                    print("->", tarinfo.linkname, end=' ')
                if tarinfo.islnk():
                    print("link to", tarinfo.linkname, end=' ')
            print()

    def add(self, name, arcname=None, recursive=True):
        """Add a file to the TarFile. Directories are added
           recursively by default.
        """
        self._check("aw")

        if arcname is None:
            arcname = name

        # Skip if somebody tries to archive the archive...
        if self.name is not None \
            and os.path.abspath(name) == os.path.abspath(self.name):
            self._dbg(2, "tarfile: Skipped %r\n" % name)
            return

        # Special case: The user wants to add the current
        # working directory.
        if name == ".":
            if recursive:
                if arcname == ".":
                    arcname = ""
                for f in os.listdir("."):
                    self.add(f, os.path.join(arcname, f))
            return

        self._dbg(1, "%s\n" % name)

        # Create a TarInfo instance from the file.
        tarinfo = self.gettarinfo(name, arcname)

        if tarinfo is None:
            self._dbg(1, "tarfile: Unsupported type %r\n" % name)
            return

        # Append the tar header and data to the archive.
        if tarinfo.isreg():
            f = builtins.file(name, "rb")
            self.addfile(tarinfo, f)
            f.close()

        if tarinfo.type in (LNKTYPE, SYMTYPE, FIFOTYPE, CHRTYPE, BLKTYPE):
            tarinfo.size = 0
            self.addfile(tarinfo)

        if tarinfo.isdir():
            self.addfile(tarinfo)
            if recursive:
                for f in os.listdir(name):
                    self.add(os.path.join(name, f), os.path.join(arcname, f))

    def addfile(self, tarinfo, fileobj=None):
        """Read from fileobj and add the data to the TarFile.
           File information and the number of bytes to read is
           taken from tarinfo.
        """
        self._check("aw")

        tarinfo.name = normpath(tarinfo.name)
        if tarinfo.linkname:
            tarinfo.linkname = normpath(tarinfo.linkname)

        if tarinfo.size > MAXSIZE_MEMBER:
            raise ValueError("file is too large (>8GB)")

        if len(tarinfo.linkname) > LENGTH_LINK:
            if self.posix:
                raise ValueError("linkname is too long (>%d)" \
                                  % (LENGTH_LINK))
            else:
                self._create_gnulong(tarinfo.linkname, GNUTYPE_LONGLINK)
                tarinfo.linkname = tarinfo.linkname[:LENGTH_LINK -1]
                self._dbg(2, "tarfile: Created GNU tar extension LONGLINK\n")

        if len(tarinfo.name) > LENGTH_NAME:
            if self.posix:
                prefix = tarinfo.name[:LENGTH_PREFIX + 1]
                while prefix and prefix[-1] != "/":
                    prefix = prefix[:-1]

                name = tarinfo.name[len(prefix):]
                prefix = prefix[:-1]

                if not prefix or len(name) > LENGTH_NAME:
                    raise ValueError("name is too long (>%d)" \
                                      % (LENGTH_NAME))

                tarinfo.name   = name
                tarinfo.prefix = prefix
            else:
                self._create_gnulong(tarinfo.name, GNUTYPE_LONGNAME)
                tarinfo.name = tarinfo.name[:LENGTH_NAME - 1]
                self._dbg(2, "tarfile: Created GNU tar extension LONGNAME\n")

        header = tarinfo.getheader()
        self.fileobj.write(header)
        self.offset += BLOCKSIZE

        # If there's data to follow, append it.
        if fileobj is not None:
            copyfileobj(fileobj, self.fileobj, tarinfo.size)
            blocks, remainder = divmod(tarinfo.size, BLOCKSIZE)
            if remainder > 0:
                self.fileobj.write(NUL * (BLOCKSIZE - remainder))
                blocks += 1
            self.offset += blocks * BLOCKSIZE

    def extractfile(self, member):
        """Extract member from the TarFile and return a file-like
           object. member may be a name or a TarInfo object.
        """
        self._check("r")

        if isinstance(member, TarInfo):
            tarinfo = member
        else:
            tarinfo = self.getmember(member)

        if tarinfo.isreg():
            return _FileObject(self, tarinfo)

        elif tarinfo.type not in SUPPORTED_TYPES:
            # If a member's type is unknown, it is treated as a
            # regular file.
            return _FileObject(self, tarinfo)

        elif tarinfo.islnk() or tarinfo.issym():
            if isinstance(self.fileobj, _Stream):
                # A small but ugly workaround for the case that someone tries
                # to extract a (sym)link as a file-object from a non-seekable
                # stream of tar blocks.
                raise StreamError("cannot extract (sym)link as file object")
            else:
                # A (sym)link's file object is it's target's file object.
                return self.extractfile(self._getmember(tarinfo.linkname,
                                                        tarinfo))
        else:
            # If there's no data associated with the member (directory, chrdev,
            # blkdev, etc.), return None instead of a file object.
            return None

    def extract(self, member, path=""):
        """Extract member from the TarFile and write it to current
           working directory using its full pathname. If path is
           given, it is prepended to the pathname. member may be a
           name or a TarInfo object.
        """
        self._check("r")

        if isinstance(member, TarInfo):
            tarinfo = member
        else:
            tarinfo = self.getmember(member)

        self._dbg(1, tarinfo.name)
        try:
            self._extract_member(tarinfo, os.path.join(path, tarinfo.name))
        except EnvironmentError as e:
            if self.errorlevel > 0:
                raise
            else:
                if e.filename is None:
                    self._dbg(1, "\ntarfile: %s" % e.strerror)
                else:
                    self._dbg(1, "\ntarfile: %s %r" % (e.strerror, e.filename))
        except TarError as e:
            if self.errorlevel > 1:
                raise
            else:
                self._dbg(1, "\ntarfile: %s" % e)
        self._dbg(1, "\n")

    def _extract_member(self, tarinfo, targetpath):
        """Extract the TarInfo object tarinfo to a physical
           file called targetpath.
        """
        # Fetch the TarInfo instance for the given name
        # and build the destination pathname, replacing
        # forward slashes to platform specific separators.
        if targetpath[-1:] == "/":
            targetpath = targetpath[:-1]
        targetpath = os.path.normpath(targetpath)

        # Create all upper directories.
        upperdirs = os.path.dirname(targetpath)
        if upperdirs and not os.path.exists(upperdirs):
            ti = TarInfo()
            ti.name  = upperdirs
            ti.type  = DIRTYPE
            ti.mode  = 0o777
            ti.mtime = tarinfo.mtime
            ti.uid   = tarinfo.uid
            ti.gid   = tarinfo.gid
            ti.uname = tarinfo.uname
            ti.gname = tarinfo.gname
            try:
                self._extract_member(ti, ti.name)
            except:
                pass

        if tarinfo.isreg():
            self._makefile(tarinfo, targetpath)
        elif tarinfo.isdir():
            self._makedir(tarinfo, targetpath)
        elif tarinfo.isfifo():
            self._makefifo(tarinfo, targetpath)
        elif tarinfo.ischr() or tarinfo.isblk():
            self._makedev(tarinfo, targetpath)
        elif tarinfo.islnk() or tarinfo.issym():
            self._makelink(tarinfo, targetpath)
        else:
            self._makefile(tarinfo, targetpath)
            if tarinfo.type not in SUPPORTED_TYPES:
                self._dbg(1, "\ntarfile: Unknown file type %r, " \
                             "extracted as regular file." % tarinfo.type)

        if not tarinfo.issym():
            self._chown(tarinfo, targetpath)
            self._chmod(tarinfo, targetpath)
            self._utime(tarinfo, targetpath)

    def _makedir(self, tarinfo, targetpath):
        """Make a directory called targetpath from tarinfo.
        """
        try:
            os.mkdir(targetpath)
        except EnvironmentError as e:
            if e.errno != errno.EEXIST:
                raise

    def _makefile(self, tarinfo, targetpath):
        """Make a file called targetpath from tarinfo.
        """
        source = self.extractfile(tarinfo)
        target = builtins.file(targetpath, "wb")
        copyfileobj(source, target)
        source.close()
        target.close()

    def _makefifo(self, tarinfo, targetpath):
        """Make a fifo called targetpath from tarinfo.
        """
        if hasattr(os, "mkfifo"):
            os.mkfifo(targetpath)
        else:
            raise TarError("fifo not supported by system")

    def _makedev(self, tarinfo, targetpath):
        """Make a character or block device called targetpath
           from tarinfo.
        """
        if not hasattr(os, "mknod"):
            raise TarError("special devices not supported by system")

        mode = tarinfo.mode
        if tarinfo.isblk():
            mode |= stat.S_IFBLK
        else:
            mode |= stat.S_IFCHR

        # XXX This if statement should go away when
        # python-2.3a0-devicemacros patch succeeds.
        if hasattr(os, "makedev"):
            os.mknod(targetpath, mode,
                     os.makedev(tarinfo.devmajor, tarinfo.devminor))
        else:
            os.mknod(targetpath, mode,
                     tarinfo.devmajor, tarinfo.devminor)

    def _makelink(self, tarinfo, targetpath):
        """Make a (symbolic) link called targetpath from tarinfo.
           If it cannot be created (platform limitation), we try
           to make a copy of the referenced file instead of a link.
        """
        linkpath = tarinfo.linkname
        self._dbg(1, " -> %s" % linkpath)
        try:
            if tarinfo.issym():
                os.symlink(linkpath, targetpath)
            else:
                os.link(linkpath, targetpath)
        except AttributeError:
            if tarinfo.issym():
                linkpath = os.path.join(os.path.dirname(tarinfo.name),
                                        linkpath)
                linkpath = normpath(linkpath)

            try:
                self._extract_member(self.getmember(linkpath), targetpath)
            except (EnvironmentError, KeyError) as e:
                linkpath = os.path.normpath(linkpath)
                try:
                    shutil.copy2(linkpath, targetpath)
                except EnvironmentError as e:
                    raise IOError("link could not be created")

    def _chown(self, tarinfo, targetpath):
        """Set owner of targetpath according to tarinfo.
        """
        if pwd and os.geteuid() == 0:
            # We have to be root to do so.
            try:
                g = grp.getgrnam(tarinfo.gname)[2]
            except KeyError:
                try:
                    g = grp.getgrgid(tarinfo.gid)[2]
                except KeyError:
                    g = os.getgid()
            try:
                u = pwd.getpwnam(tarinfo.uname)[2]
            except KeyError:
                try:
                    u = pwd.getpwuid(tarinfo.uid)[2]
                except KeyError:
                    u = os.getuid()
            try:
                if tarinfo.issym() and hasattr(os, "lchown"):
                    os.lchown(targetpath, u, g)
                else:
                    os.chown(targetpath, u, g)
            except EnvironmentError as e:
                raise TarError("could not change owner")

    def _chmod(self, tarinfo, targetpath):
        """Set file permissions of targetpath according to tarinfo.
        """
        try:
            os.chmod(targetpath, tarinfo.mode)
        except EnvironmentError as e:
            raise TarError("could not change mode")

    def _utime(self, tarinfo, targetpath):
        """Set modification time of targetpath according to tarinfo.
        """
        try:
            os.utime(targetpath, (tarinfo.mtime, tarinfo.mtime))
        except EnvironmentError as e:
            raise TarError("could not change modification time")

    def _getmember(self, name, tarinfo=None):
        """Find an archive member by name from bottom to top.
           If tarinfo is given, it is used as the starting point.
        """
        if tarinfo is None:
            end = len(self.members)
        else:
            end = self.members.index(tarinfo)

        for i in range(end - 1, -1, -1):
            if name == self.membernames[i]:
                return self.members[i]

    def _load(self):
        """Read through the entire archive file and look for readable
           members.
        """
        while True:
            tarinfo = next(self)
            if tarinfo is None:
                break
        self._loaded = True

    def _check(self, mode):
        """Check if TarFile is still open, and if the operation's mode
           corresponds to TarFile's mode.
        """
        if self.fileobj is None:
            raise IOError("%s is closed" % self.__class__.__name__)
        if self._mode not in mode:
            raise IOError("bad operation for mode %r" % self._mode)

    def __iter__(self):
        """Provide an iterator object.
        """
        if self._loaded:
            return iter(self.members)
        else:
            return TarIter(self)

    def _buftoinfo(self, buf):
        """Transform a 512 byte block to a TarInfo object.
        """
        tarinfo = TarInfo()
        tarinfo.name = nts(buf[0:100])
        tarinfo.mode = int(buf[100:108], 8)
        tarinfo.uid = int(buf[108:116],8)
        tarinfo.gid = int(buf[116:124],8)
        tarinfo.size = int(buf[124:136], 8)
        tarinfo.mtime = int(buf[136:148], 8)
        tarinfo.chksum = int(buf[148:156], 8)
        tarinfo.type = buf[156:157]
        tarinfo.linkname = nts(buf[157:257])
        tarinfo.uname = nts(buf[265:297])
        tarinfo.gname = nts(buf[297:329])
        try:
            tarinfo.devmajor = int(buf[329:337], 8)
            tarinfo.devminor = int(buf[337:345], 8)
        except ValueError:
            tarinfo.devmajor = tarinfo.devmajor = 0

        prefix = buf[345:500]
        while prefix and prefix[-1] == NUL:
            prefix = prefix[:-1]
        if len(prefix.split(NUL)) == 1:
            tarinfo.prefix = prefix
            tarinfo.name = normpath(os.path.join(tarinfo.prefix, tarinfo.name))
        else:
            tarinfo.prefix = buf[345:500]

        if tarinfo.chksum != calc_chksum(buf):
            if self:
                self._dbg(1, "tarfile: Bad Checksum\n")
        return tarinfo

    def _proc_gnulong(self, tarinfo, type):
        """Evaluate the blocks that hold a GNU longname
           or longlink member.
        """
        name = None
        linkname = None
        buf = ""
        count = tarinfo.size
        while count > 0:
            block = self.fileobj.read(BLOCKSIZE)
            buf += block
            self.offset += BLOCKSIZE
            count -= BLOCKSIZE

        if type == GNUTYPE_LONGNAME:
            name = nts(buf)
        if type == GNUTYPE_LONGLINK:
            linkname = nts(buf)

        buf = self.fileobj.read(BLOCKSIZE)
        tarinfo = self._buftoinfo(buf)
        if name is not None:
            tarinfo.name = name
        if linkname is not None:
            tarinfo.linkname = linkname
        self.offset += BLOCKSIZE
        return tarinfo

    def _create_gnulong(self, name, type):
        """Write a GNU longname/longlink member to the TarFile.
           It consists of an extended tar header, with the length
           of the longname as size, followed by data blocks,
           which contain the longname as a null terminated string.
        """
        tarinfo = TarInfo()
        tarinfo.name = "././@LongLink"
        tarinfo.type = type
        tarinfo.mode = 0
        tarinfo.size = len(name)

        # write extended header
        self.fileobj.write(tarinfo.getheader())
        # write name blocks
        self.fileobj.write(name)
        blocks, remainder = divmod(tarinfo.size, BLOCKSIZE)
        if remainder > 0:
            self.fileobj.write(NUL * (BLOCKSIZE - remainder))
            blocks += 1
        self.offset += blocks * BLOCKSIZE

    def _proc_sparse(self, tarinfo):
        """Analyze a GNU sparse header plus extra headers.
        """
        buf = tarinfo.getheader()
        sp = _ringbuffer()
        pos = 386
        lastpos = 0
        realpos = 0
        # There are 4 possible sparse structs in the
        # first header.
        for i in range(4):
            try:
                offset = int(buf[pos:pos + 12], 8)
                numbytes = int(buf[pos + 12:pos + 24], 8)
            except ValueError:
                break
            if offset > lastpos:
                sp.append(_hole(lastpos, offset - lastpos))
            sp.append(_data(offset, numbytes, realpos))
            realpos += numbytes
            lastpos = offset + numbytes
            pos += 24

        isextended = ord(buf[482])
        origsize = int(buf[483:495], 8)

        # If the isextended flag is given,
        # there are extra headers to process.
        while isextended == 1:
            buf = self.fileobj.read(BLOCKSIZE)
            self.offset += BLOCKSIZE
            pos = 0
            for i in range(21):
                try:
                    offset = int(buf[pos:pos + 12], 8)
                    numbytes = int(buf[pos + 12:pos + 24], 8)
                except ValueError:
                    break
                if offset > lastpos:
                    sp.append(_hole(lastpos, offset - lastpos))
                sp.append(_data(offset, numbytes, realpos))
                realpos += numbytes
                lastpos = offset + numbytes
                pos += 24
            isextended = ord(buf[504])

        if lastpos < origsize:
            sp.append(_hole(lastpos, origsize - lastpos))

        tarinfo.sparse = sp
        return origsize

    def _dbg(self, level, msg):
        if level <= self.debug:
            sys.stdout.write(msg)
# class TarFile

class TarIter:
    """Iterator Class.

       for tarinfo in TarFile(...):
           suite...
    """

    def __init__(self, tarfile):
        """Construct a TarIter instance.
        """
        self.tarfile = tarfile
    def __iter__(self):
        """Return iterator object.
        """
        return self
    def __next__(self):
        """Return the next item using TarFile's next() method.
           When all members have been read, set TarFile as _loaded.
        """
        tarinfo = next(self.tarfile)
        if not tarinfo:
            self.tarfile._loaded = True
            raise StopIteration
        return tarinfo
# class TarIter

# Helper classes for sparse file support
class _section:
    """Base class for _data and _hole.
    """
    def __init__(self, offset, size):
        self.offset = offset
        self.size = size
    def __contains__(self, offset):
        return self.offset <= offset < self.offset + self.size

class _data(_section):
    """Represent a data section in a sparse file.
    """
    def __init__(self, offset, size, realpos):
        _section.__init__(self, offset, size)
        self.realpos = realpos

class _hole(_section):
    """Represent a hole section in a sparse file.
    """
    pass

class _ringbuffer(list):
    """Ringbuffer class which increases performance
       over a regular list.
    """
    def __init__(self):
        self.idx = 0
    def find(self, offset):
        idx = self.idx
        while True:
            item = self[idx]
            if offset in item:
                break
            idx += 1
            if idx == len(self):
                idx = 0
            if idx == self.idx:
                # End of File
                return None
        self.idx = idx
        return item

class _FileObject:
    """File-like object for reading an archive member.
       Is returned by TarFile.extractfile(). Support for
       sparse files included.
    """

    def __init__(self, tarfile, tarinfo):
        self.fileobj = tarfile.fileobj
        self.name    = tarinfo.name
        self.mode    = "r"
        self.closed  = False
        self.offset  = tarinfo.offset_data
        self.size    = tarinfo.size
        self.pos     = 0
        self.linebuffer = ""
        if tarinfo.issparse():
            self.sparse = tarinfo.sparse
            self.read = self._readsparse
        else:
            self.read = self._readnormal

    def readline(self, size=-1):
        """Read a line with approx. size. If size is negative,
           read a whole line. readline() and read() must not
           be mixed up (!).
        """
        if size < 0:
            size = 2**31-1

        nl = self.linebuffer.find("\n")
        if nl >= 0:
            nl = min(nl, size)
        else:
            size -= len(self.linebuffer)
            while nl < 0:
                buf = self.read(min(size, 100))
                if not buf:
                    break
                self.linebuffer += buf
                size -= len(buf)
                if size <= 0:
                    break
                nl = self.linebuffer.find("\n")
            if nl == -1:
                s = self.linebuffer
                self.linebuffer = ""
                return s
        buf = self.linebuffer[:nl]
        self.linebuffer = self.linebuffer[nl + 1:]
        while buf[-1:] == "\r":
            buf = buf[:-1]
        return buf + "\n"

    def readlines(self):
        """Return a list with all (following) lines.
        """
        result = []
        while True:
            line = self.readline()
            if not line: break
            result.append(line)
        return result

    def _readnormal(self, size=None):
        """Read operation for regular files.
        """
        if self.closed:
            raise ValueError("file is closed")
        self.fileobj.seek(self.offset + self.pos)
        bytesleft = self.size - self.pos
        if size is None:
            bytestoread = bytesleft
        else:
            bytestoread = min(size, bytesleft)
        self.pos += bytestoread
        return self.fileobj.read(bytestoread)

    def _readsparse(self, size=None):
        """Read operation for sparse files.
        """
        if self.closed:
            raise ValueError("file is closed")

        if size is None:
            size = self.size - self.pos

        data = ""
        while size > 0:
            buf = self._readsparsesection(size)
            if not buf:
                break
            size -= len(buf)
            data += buf
        return data

    def _readsparsesection(self, size):
        """Read a single section of a sparse file.
        """
        section = self.sparse.find(self.pos)

        if section is None:
            return ""

        toread = min(size, section.offset + section.size - self.pos)
        if isinstance(section, _data):
            realpos = section.realpos + self.pos - section.offset
            self.pos += toread
            self.fileobj.seek(self.offset + realpos)
            return self.fileobj.read(toread)
        else:
            self.pos += toread
            return NUL * toread

    def tell(self):
        """Return the current file position.
        """
        return self.pos

    def seek(self, pos, whence=0):
        """Seek to a position in the file.
        """
        self.linebuffer = ""
        if whence == 0:
            self.pos = min(max(pos, 0), self.size)
        if whence == 1:
            if pos < 0:
                self.pos = max(self.pos + pos, 0)
            else:
                self.pos = min(self.pos + pos, self.size)
        if whence == 2:
            self.pos = max(min(self.size + pos, self.size), 0)

    def close(self):
        """Close the file object.
        """
        self.closed = True
#class _FileObject

#---------------------------------------------
# zipfile compatible TarFile class
#
# for details consult zipfile's documentation
#---------------------------------------------
import io

TAR_PLAIN = 0           # zipfile.ZIP_STORED
TAR_GZIPPED = 8         # zipfile.ZIP_DEFLATED
class TarFileCompat:
    """TarFile class compatible with standard module zipfile's
       ZipFile class.
    """
    def __init__(self, file, mode="r", compression=TAR_PLAIN):
        if not isinstance(file, (type(''), type(''))) and hasattr(file, 'read'):
            fileobj = file
            file = ''
        else:
            fileobj = None
        
        self.compression = compression
       
        if compression == TAR_PLAIN:
            self.tarfile = open(file, mode, fileobj=fileobj)
        elif compression == TAR_GZIPPED:
            if mode == 'a':
                self.tarfile = gzopen(file, mode, fileobj=fileobj)
            else:
                self.tarfile = gzopen(file, mode, fileobj=fileobj)
        else:
            raise ValueError("unknown compression constant")
        if mode[0:1] == "r":
            import time
            members = self.tarfile.getmembers()
            for i in range(len(members)):
                m = members[i]
                m.filename = m.name
                m.file_size = m.size
                m.date_time = time.gmtime(m.mtime)[:6]

    def namelist(self):
        return [m.name for m in self.infolist()]
    def infolist(self):
        return [m for m in self.tarfile.getmembers() if m.type in REGULAR_TYPES]
    def printdir(self):
        self.tarfile.list()
    def testzip(self):
        return
    def getinfo(self, name):
        return self.tarfile.getmember(name)
    def read(self, name):
        return self.tarfile.extractfile(self.tarfile.getmember(name)).read()
    def write(self, filename, arcname=None, compress_type=None):
        self.tarfile.add(filename, arcname)
    def writestr(self, zinfo, bytes):
        import calendar
        zinfo.name = zinfo.filename
        zinfo.size = zinfo.file_size
        zinfo.mtime = calendar.timegm(zinfo.date_time)
        self.tarfile.addfile(zinfo, io.StringIO(bytes))
    def close(self):
        self.tarfile.close()
#class TarFileCompat

if __name__ == "__main__":
    # a "light-weight" implementation of GNUtar ;-)
    usage = """
Usage: %s [options] [files]

-h          display this help message

-c          create a tarfile

-r          append to an existing archive

-x          extract archive

-t          list archive contents

-f FILENAME use archive FILENAME, else STDOUT (-c)

-z          filter archive through gzip

-C DIRNAME  with opt -x:     extract to directory DIRNAME
            with opt -c, -r: put files to archive under DIRNAME

-v          verbose output

-q          quiet

--posix     create a POSIX 1003.1-1990 compliant archive

wildcards *, ?, [seq], [!seq] are accepted.
    """ % sys.argv[0]

    import getopt, glob
    try:
        opts, args = getopt.getopt(sys.argv[1:], "htcxrzjf:C:vq", ("posix",))
    except getopt.GetoptError as e:
        print()
        print("ERROR:", e)
        print(usage)
        sys.exit(0)

    file  = None
    mode  = None
    dir   = None
    comp  = ""
    debug = 0
    posix = False
    for o, a in opts:
        if o == "-t": mode = "l"        # list archive
        if o == "-c": mode = "w"        # write to archive
        if o == "-r": mode = "a"        # append to archive
        if o == "-x": mode = "r"        # extract from archive
        if o == "-f": file = a          # specify filename else use stdout
        if o == "-C": dir  = a          # change to dir
        if o == "-z": comp = "gz"       # filter through gzip
        if o == "-j": comp = "bz2"      # filter through bzip2
        if o == "-v": debug = 2         # verbose mode
        if o == "-q": debug = 0         # quiet mode
        if o == "--posix": posix = True # create posix compatible archive
        if o == "-h":                   # help message
            print(usage)
            sys.exit(0)

    if mode is None:
        print(usage)
        sys.exit(0)

    mode = "%s:%s" % (mode, comp)

    if not file or file == "-":
        if mode[0] != "w":
            print(usage)
            sys.exit(0)
        debug = 0
        # If under Win32, set stdout to binary.
        try:
            import msvcrt
            msvcrt.setmode(1, os.O_BINARY)
        except ImportError:
            pass
        tarfile = open("sys.stdout.tar", "%s:%s" % (mode, comp), sys.stdout)
    else:
        if mode[0] == "l":
            tarfile = open(file, "r" + mode[1:])
        else:
            tarfile = open(file, mode)

    tarfile.debug = debug
    tarfile.posix = posix

    if mode[0] == "r":
        if dir is None:
            dir = ""
        for tarinfo in tarfile:
            tarfile.extract(tarinfo, dir)
    elif mode[0] == "l":
        tarfile.list(debug)
    else:
        for arg in args:
            files = glob.glob(arg)
            for f in files:
                try:
                    tarfile.add(f, dir)
                except Exception as e:
                    print("ERROR:", e)
    tarfile.close()
