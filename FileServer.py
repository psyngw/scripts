#!/usr/bin/env python3
"""Simple HTTP Server With Upload.

This module builds on BaseHTTPServer by implementing the standard GET
and HEAD requests in a fairly straightforward manner.

Thanks to: @bitzend
see: https://gist.github.com/UniIsland/3346170
"""

__version__ = "0.1"
__all__ = ["SimpleHTTPRequestHandler"]
__author__ = "psyngw"
__home_page__ = "http://127.0.0.1:8000"

import os
import posixpath
import http.server
import urllib.request, urllib.parse, urllib.error
import html
import shutil
import mimetypes
import re
from io import BytesIO
import sys
import subprocess
import socket
import socketserver

try:
    import pyperclip

    can_use_pyperclip = True
except ImportError:
    can_use_pyperclip = False

javascript = b'''
<script>

var xmlHttp;
function do_ajax(isGet){
    xmlHttp = new XMLHttpRequest();
    var data = 'get';
    if(isGet){
        xmlHttp.onreadystatechange = res_get;
    }else{
        var ta = document.getElementById('ta');
        xmlHttp.onreadystatechange = res_send;
        data = encodeURI(ta.value);
    }
    xmlHttp.open("post","/",true);
    xmlHttp.setRequestHeader("Content-Type","application/x-www-form-urlencoded");
    xmlHttp.setRequestHeader("use-clipper","ture");
    xmlHttp.send(data);
}

function res_get(){
    if(xmlHttp.status==200&&xmlHttp.readyState==4){
        if(xmlHttp.responseText === 'error'){
            alert('get error');
        }else{
            var ta = document.getElementById('ta');
            console.info(xmlHttp.responseText);
            ta.value = xmlHttp.responseText;
        }
    }
}

function res_send(){
    if(xmlHttp.status==200&&xmlHttp.readyState==4){
        alert("send "+xmlHttp.responseText);
    }
}

</script>

'''


def execute(cmd, encoding='UTF-8', timeout=None, shell=False):
    """Execute a shell command/binary.
    If you are using this function in a script ran by a priviliged user,
    be careful as to what your are executing.
    Arguments:
    cmd:        List[str] -- splitted command (ex: ['ls', '-la', '~'])
    encoding:   str (default: 'UTF-8') -- used for decoding the command output
    timeout:    int (default: None) -- in seconds, raises TimeoutExpired if the
    result: a tuple coontaining stdout, the returncode and stderr
    """

    proc = subprocess.Popen(cmd,
                            stdin=subprocess.DEVNULL,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            shell=shell,
                            universal_newlines=True)
    output, error = proc.communicate(timeout=timeout)
    # rstrip('\n') may be more accurate, actually nothing may be better
    if type(output) is not str:
        output = output.decode(encoding).rstrip()
    if type(error) is not str:
        error = error.decode(encoding).rstrip()
    rc = proc.returncode
    return (output, rc, error)


def clipper_get():
    if can_use_pyperclip:
        return pyperclip.paste()
    else:
        # out, rc, err = execute('termux-clipboard-get')
        out, rc, err = execute(['xsel', '-ob'])
        if rc:
            return 'error'
        return out


def clipper_set(data):
    if can_use_pyperclip:
        pyperclip.copy(data)
        return True
    else:

        # out, rc, err = execute(['termux-clipboard-set', repr(data)[1:-1]])
        # out, rc, err = execute(['echo', repr(data)[1:-1], '|grep', 'xsel', '-b'])
        os.system(f"echo {repr(data)[1:-1]} | xsel -b")
        # if rc:
        #     return False
        return True


class SimpleHTTPRequestHandler(http.server.BaseHTTPRequestHandler):
    """Simple HTTP request handler with GET/HEAD/POST commands.

    This serves files from the current directory and any of its
    subdirectories.  The MIME type for files is determined by
    calling the .guess_type() method. And can reveive file uploaded
    by client.

    The GET/HEAD/POST requests are identical except that the HEAD
    request omits the actual contents of the file.

    """

    server_version = "SimpleHTTPWithUpload/" + __version__

    def do_GET(self):
        """Serve a GET request."""
        f = self.send_head()
        if f:
            self.copyfile(f, self.wfile)
            f.close()

    def do_HEAD(self):
        """Serve a HEAD request."""
        f = self.send_head()
        if f:
            f.close()

    def do_POST(self):
        """Serve a POST request."""
        if 'use-clipper' in self.headers:
            data = self.rfile.read(int(self.headers['content-length']))
            if data == b'get':
                res = clipper_get()
            else:
                if clipper_set(
                        urllib.parse.unquote(data.decode(encoding="utf-8"))):
                    res = 'success'
                else:
                    res = 'error'
            self.send_response(200)
            res = res.encode(encoding="utf-8")
            self.send_header("Content-Length", str(len(res)))
            self.end_headers()
            self.wfile.write(res)
            return

        r, info = self.deal_post_data()
        print((r, info, "by: ", self.client_address))
        f = BytesIO()
        f.write(b'<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">')
        f.write(b"<html>\n<title>Upload Result Page</title>\n")
        f.write(b"<body>\n<h2>Upload Result Page</h2>\n")
        f.write(b"<hr>\n")
        if r:
            f.write(b"<strong>Success:</strong>")
        else:
            f.write(b"<strong>Failed:</strong>")
        f.write(info.encode())
        f.write(
            ("<br><a href=\"%s\">back</a>" % self.headers['referer']).encode())
        f.write(b"<hr><small>Powerd By: bitPi")

        f.write(b"</small></body>\n</html>\n")
        length = f.tell()
        f.seek(0)
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.send_header("Content-Length", str(length))
        self.end_headers()
        if f:
            self.copyfile(f, self.wfile)
            f.close()

    def deal_post_data(self):
        content_type = self.headers['content-type']
        if not content_type:
            return (False, "Content-Type header doesn't contain boundary")
        boundary = content_type.split("=")[1].encode()
        remainbytes = int(self.headers['content-length'])
        line = self.rfile.readline()
        remainbytes -= len(line)
        if not boundary in line:
            return (False, "Content NOT begin with boundary")
        line = self.rfile.readline()
        remainbytes -= len(line)
        fn = re.findall(r'Content-Disposition.*name="file"; filename="(.*)"',
                        line.decode())
        if not fn:
            return (False, "Can't find out file name...")
        path = self.translate_path(self.path)
        fn = os.path.join(path, fn[0])
        line = self.rfile.readline()
        remainbytes -= len(line)
        line = self.rfile.readline()
        remainbytes -= len(line)
        try:
            out = open(fn, 'wb')
        except IOError:
            return (
                False,
                "Can't create file to write, do you have permission to write?")

        preline = self.rfile.readline()
        remainbytes -= len(preline)
        while remainbytes > 0:
            line = self.rfile.readline()
            remainbytes -= len(line)
            if boundary in line:
                preline = preline[0:-1]
                if preline.endswith(b'\r'):
                    preline = preline[0:-1]
                out.write(preline)
                out.close()
                # if not can_use_pyperclip:
                #     execute(['termux-media-scan', fn])
                return (True, "File '%s' upload success!" % fn)
            else:
                out.write(preline)
                preline = line
        return (False, "Unexpect Ends of data.")

    def send_head(self):
        """Common code for GET and HEAD commands.

        This sends the response code and MIME headers.

        Return value is either a file object (which has to be copied
        to the outputfile by the caller unless the command was HEAD,
        and must be closed by the caller under all circumstances), or
        None, in which case the caller has nothing further to do.

        """
        path = self.translate_path(self.path)
        f = None
        if os.path.isdir(path):
            if not self.path.endswith('/'):
                # redirect browser - doing basically what apache does
                self.send_response(301)
                self.send_header("Location", self.path + "/")
                self.end_headers()
                return None
            for index in "index.html", "index.htm":
                index = os.path.join(path, index)
                if os.path.exists(index):
                    path = index
                    break
            else:
                ##                arkPath = os.path.join(path, "archive")
                return self.list_directory(path)
        ctype = self.guess_type(path)
        try:
            # Always read in binary mode. Opening files in text mode may cause
            # newline translations, making the actual size of the content
            # transmitted *less* than the content-length!
            f = open(path, 'rb')
        except IOError:
            self.send_error(404, "File not found")
            return None
        self.send_response(200)
        self.send_header("Content-type", ctype)
        fs = os.fstat(f.fileno())
        self.send_header("Content-Length", str(fs[6]))
        self.send_header("Last-Modified", self.date_time_string(fs.st_mtime))
        self.end_headers()
        return f

    def list_directory(self, path):
        """Helper to produce a directory listing (absent index.html).

        Return value is either a file object, or None (indicating an
        error).  In either case, the headers are sent, making the
        interface the same as for send_head().

        """
        try:
            list = os.listdir(path)
        except os.error:
            self.send_error(404, "No permission to list directory")
            return None
        list.sort(key=lambda a: a.lower())
        f = BytesIO()
        displaypath = html.escape(urllib.parse.unquote(self.path))
        f.write(b'<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">')
        f.write(
            b'<head>\n    <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />\n</head>\n'
        )
        f.write(("<html>\n<title>Directory listing for %s</title>\n" %
                 displaypath).encode())
        f.write(b"<body>\n")
        f.write(javascript)
        f.write(
            b"<div style=\"float:left;margin-right:20px\"><form ENCTYPE=\"multipart/form-data\" method=\"post\">"
        )
        f.write(b"<input name=\"file\" type=\"file\"/>")
        f.write(b"<input type=\"submit\" value=\"upload\"/></form></div>\n")
        f.write(b"<div style=\"float:left\">")
        f.write(
            b"<div style=\"float:left;margin-right:20px\"><textarea <input style=\"width:230px;height:50px\" id=\"ta\"></textarea></div>\n"
        )
        f.write(b"<div style=\"float:left\">")
        f.write(
            b"<div style=\"margin:5px 10px 1px;\"><input style=\"width:50px;\" type=\"button\" onclick=do_ajax(true) value=\"get\"/></div>"
        )
        f.write(
            b"<div style=\"margin:1px 10px 5px\"><input style=\"width:50px;\" type=\"button\" onclick=do_ajax(false) value=\"send\"/></div>"
        )
        f.write(b"</div>\n</div>\n</div>\n")
        f.write(b"<div style=\"clear:both\"><hr>\n")
        f.write(("<h2>Directory listing for %s</h2>\n" % displaypath).encode())
        f.write(b"<hr>\n<ul>\n")
        for name in list:
            fullname = os.path.join(path, name)
            displayname = linkname = name
            # Append / for directories or @ for symbolic links
            if os.path.isdir(fullname):
                displayname = name + "/"
                linkname = name + "/"
            if os.path.islink(fullname):
                displayname = name + "@"
                # Note: a link to a directory displays with @ and links with /
            f.write(('<li><a href="%s">%s</a>\n' %
                     (urllib.parse.quote(linkname),
                      html.escape(displayname))).encode())
        f.write(b"</ul>\n<hr>\n</div>\n</body>\n</html>\n")
        length = f.tell()
        f.seek(0)
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.send_header("Content-Length", str(length))
        self.end_headers()
        return f

    def translate_path(self, path):
        """Translate a /-separated PATH to the local filename syntax.

        Components that mean special things to the local file system
        (e.g. drive or directory names) are ignored.  (XXX They should
        probably be diagnosed.)

        """
        # abandon query parameters
        path = path.split('?', 1)[0]
        path = path.split('#', 1)[0]
        path = posixpath.normpath(urllib.parse.unquote(path))
        words = path.split('/')
        words = [_f for _f in words if _f]
        path = os.getcwd()
        for word in words:
            drive, word = os.path.splitdrive(word)
            head, word = os.path.split(word)
            if word in (os.curdir, os.pardir): continue
            path = os.path.join(path, word)
        return path

    def copyfile(self, source, outputfile):
        """Copy all data between two file objects.

        The SOURCE argument is a file object open for reading
        (or anything with a read() method) and the DESTINATION
        argument is a file object open for writing (or
        anything with a write() method).

        The only reason for overriding this would be to change
        the block size or perhaps to replace newlines by CRLF
        -- note however that this the default server uses this
        to copy binary data as well.

        """
        shutil.copyfileobj(source, outputfile)

    def guess_type(self, path):
        """Guess the type of a file.

        Argument is a PATH (a filename).

        Return value is a string of the form type/subtype,
        usable for a MIME Content-type header.

        The default implementation looks the file's extension
        up in the table self.extensions_map, using application/octet-stream
        as a default; however it would be permissible (if
        slow) to look inside the data to make a better guess.

        """

        base, ext = posixpath.splitext(path)
        if ext in self.extensions_map:
            return self.extensions_map[ext]
        ext = ext.lower()
        if ext in self.extensions_map:
            return self.extensions_map[ext]
        else:
            return self.extensions_map['']

    if not mimetypes.inited:
        mimetypes.init() # try to read system mime.types
    extensions_map = mimetypes.types_map.copy()
    extensions_map.update({
        '': 'application/octet-stream', # Default
        '.py': 'text/plain',
        '.c': 'text/plain',
        '.h': 'text/plain',
    })


class ForkingHTTPServer(socketserver.ForkingTCPServer):
    allow_reuse_address = 1

    def server_bind(self):
        socketserver.TCPServer.server_bind(self)
        host, port = self.socket.getsockname()[:2]
        self.server_name = socket.getfqdn(host)
        self.server_port = port


def test(HandlerClass=SimpleHTTPRequestHandler,
         ServerClass=ForkingHTTPServer,
         port=8000):
    # ServerClass=http.server.HTTPServer,
    # port=8000):
    # http.server.test(HandlerClass, ServerClass, port=port)
    http.server.test(HandlerClass, ServerClass, port=port)


def get_self_ip():
    ip = "can't get ip."
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
        return ip


if __name__ == '__main__':
    print(f"ip: {get_self_ip()}:{8000 if len(sys.argv) != 2 else sys.argv[1]}")
    if len(sys.argv) == 2:
        test(port=int(sys.argv[1]))
    else:
        test()
