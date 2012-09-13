from urllib2 import * # http client
import re # regular expression
from BeautifulSoup import BeautifulSoup # html parser
from urlparse import urlparse # url parser

class Page():
    """Page class"""
    def __init__(self,url):
        self.url = url
    # if url is the same, page is the same
    def __eq__(self,other):
        return self.url == other.url
    # in order to put object as key, override hash method
    def __hash__(self):
        return hash(self.url)



url = "http://www.beiouyou.com"
link_graph  = {} # datastructure to store link relationship

# parse url to get domain name and url path
parse_result = urlparse(url)

domain = parse_result.netloc
path = parse_result.path if parse_result.path is not '' else '/'

try:
    page = urlopen(url)
except URLError:
    print "error happened when request the url"
    exit(1)

mp = Page(path)

link_graph[mp] = [] # add main page to graph

content = page.read()

# links = re.findall('''href=["'](.[^"']+)["']''', content, re.I)
soup  = BeautifulSoup(content)

in_links = []

# parse all hyperlink
for a in soup.findAll('a', href=True):
    parts = urlparse(a['href'])
    if parts.netloc == domain or parts.netloc =='': # filter only internal link
        in_links.append(parts.path)

in_links = set(in_links) # get unique link

for link in in_links:
    p  = Page(link)
    if p not in link_graph:
        link_graph[p] = []
    if p not in link_graph[mp]:
        link_graph[mp].append(p)

print link_graph
        