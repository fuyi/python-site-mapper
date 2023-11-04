import urllib.parse
from urllib.parse import urlsplit, urlunsplit

def print_usage():
    print("Usage: python mapper.py -l <url>")
    print("For help: python mapper -h")
    exit()

def url_fix(s, charset='utf-8'):
    if isinstance(s, str):
        s = s.encode(charset, 'ignore')
    scheme, netloc, path, qs, anchor = urlsplit(s)
    path = urllib.parse.quote(path, '/%')
    qs = urllib.parse.quote_plus(qs, ':&=')
    return urlunsplit((scheme.decode('utf-8'), netloc.decode('utf-8'), path, qs, anchor))