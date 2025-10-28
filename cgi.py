"""
Compatibility module for Django with Python 3.13+
This module provides a minimal implementation of the cgi module that was removed in Python 3.13
"""

import html
import tempfile
import warnings
from collections import defaultdict
from io import StringIO
from urllib.parse import parse_qsl

__all__ = ["FieldStorage", "parse", "parse_multipart", "parse_header", "test", "print_exception",
           "print_environ", "print_form", "print_directory", "print_arguments", "print_environ_usage"]

class FieldStorage:
    """Basic implementation of FieldStorage for compatibility"""
    
    def __init__(self, fp=None, headers=None, outerboundary=b'',
                 environ=None, keep_blank_values=False, strict_parsing=False,
                 limit=None, encoding='utf-8', errors='replace', max_num_fields=None):
        self.file = fp
        self.headers = headers or {}
        self.outerboundary = outerboundary
        self.environ = environ or {}
        self.keep_blank_values = keep_blank_values
        self.strict_parsing = strict_parsing
        self.limit = limit
        self.encoding = encoding
        self.errors = errors
        self.max_num_fields = max_num_fields
        self.list = []
        self.dict = {}
        self.parse_environ()
        
    def parse_environ(self):
        """Parse the environment variables for form data"""
        if 'REQUEST_METHOD' not in self.environ:
            return
            
        if self.environ['REQUEST_METHOD'] == 'POST':
            if 'CONTENT_TYPE' in self.environ:
                ctype, pdict = parse_header(self.environ['CONTENT_TYPE'])
                if ctype == 'multipart/form-data':
                    if 'boundary' in pdict:
                        self.parse_multipart(self.file, pdict['boundary'].encode())
                elif ctype == 'application/x-www-form-urlencoded':
                    self.parse_urlencoded()
                    
        if 'QUERY_STRING' in self.environ:
            self.parse_qs(self.environ['QUERY_STRING'])
            
    def parse_multipart(self, fp, boundary):
        """Minimal multipart form parsing"""
        # This is a simplified implementation
        pass
        
    def parse_urlencoded(self):
        """Parse application/x-www-form-urlencoded data"""
        try:
            length = int(self.environ.get('CONTENT_LENGTH', 0))
        except ValueError:
            length = 0
            
        if length > 0:
            data = self.file.read(length)
            self.parse_qs(data.decode(self.encoding, self.errors))
            
    def parse_qs(self, qs):
        """Parse a query string"""
        for name, value in parse_qsl(qs, keep_blank_values=self.keep_blank_values,
                                    strict_parsing=self.strict_parsing):
            if name in self.dict:
                self.dict[name].append(value)
            else:
                self.dict[name] = [value]
                self.list.append(MiniFieldStorage(name, value))
                
    def getvalue(self, name, default=None):
        """Get the first value for a field"""
        if name in self.dict:
            return self.dict[name][0]
        else:
            return default
            
    def getlist(self, name):
        """Get all values for a field"""
        return self.dict.get(name, [])
        
    def keys(self):
        """Return list of form field names"""
        return self.dict.keys()
        
    def __getitem__(self, name):
        """Dictionary style indexing"""
        if name in self.dict:
            return self.dict[name][0]
        raise KeyError(name)
        
    def __contains__(self, name):
        """Dictionary style containment test"""
        return name in self.dict
        
class MiniFieldStorage:
    """Mini version of FieldStorage for use in FieldStorage.list"""
    
    def __init__(self, name, value):
        self.name = name
        self.value = value
        self.filename = None
        self.list = None
        self.type = None
        self.file = StringIO(value)
        self.type_options = {}
        self.disposition = None
        self.disposition_options = {}
        self.headers = {}
        
def parse_header(line):
    """Parse a Content-type like header.
    
    Return the main content-type and a dictionary of parameters.
    """
    parts = line.split(';')
    key = parts[0].strip().lower()
    pdict = {}
    for p in parts[1:]:
        if '=' not in p:
            continue
        name, value = p.split('=', 1)
        name = name.strip().lower()
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] == '"':
            value = value[1:-1]
        pdict[name] = value
    return key, pdict
    
def parse(fp=None, environ=None, keep_blank_values=False, strict_parsing=False):
    """Parse a form data."""
    return FieldStorage(fp, environ=environ, keep_blank_values=keep_blank_values,
                       strict_parsing=strict_parsing)
                       
def parse_multipart(fp, pdict):
    """Parse multipart input."""
    # This is a simplified implementation
    return {}
    
def test():
    """Minimal test function."""
    print("No tests implemented")
    
def print_exception(type, value, tb, limit=None, file=None):
    """Print exception info."""
    import traceback
    traceback.print_exception(type, value, tb, limit, file)
    
def print_environ(environ=None):
    """Print environment variables."""
    if environ is None:
        import os
        environ = os.environ
    for key, value in sorted(environ.items()):
        print(f"{key}={value}")
        
def print_form(form):
    """Format a form as HTML."""
    print("<dl>")
    for key in form.keys():
        print(f"<dt>{html.escape(key)}</dt>")
        for value in form.getlist(key):
            print(f"<dd>{html.escape(value)}</dd>")
    print("</dl>")
    
def print_directory():
    """Print files in current directory."""
    import os
    for file in os.listdir("."):
        print(file)
        
def print_arguments():
    """Print command line arguments."""
    import sys
    for arg in sys.argv:
        print(arg)
        
def print_environ_usage():
    """Print usage of environment variables."""
    print("Usage: cgi.print_environ()")
