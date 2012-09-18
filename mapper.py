from urllib2 import * # http client
from BeautifulSoup import BeautifulSoup # html parser
from urlparse import urlparse # url parser
import time

class Graph():
    """class for page graph"""
    def __init__(self):
        self.pages = []
        self.dead_pages = []         # store dead link pages
    # function to build up page graph
    def buildGraph(self, p):
        if not p.visited and not p.dead_page: # page is not visited and is accessible
            # step 1, mark page as visited
            p.visited = True
            # step 2, add current page to graph if not in graph yet
            if not self.__findPage(p.url):
                self.__addPage(p)
            # step 3, generate pages for each internal link and add to page next, add page to graph if it is a new page
            for link in p.in_links:
                page = self.__findPage(link) if self.__findPage(link) else self.__findDeadPage(link)
                if page: # page already exist on graph, do nothing
                    pass
                else: 
                    page = Page(link) # page not exist, create new page
                    if not page.dead_page:
                        self.__addPage(page) # add new page to graph if not dead page
                    else: # page is dead page, add to deadpage list
                        self.__addDeadPage(page)
                if not page.dead_page:
                    self.__addNext(p,page) # add page to current pages next list if not deadpage
                self.buildGraph(page) # recursively build graph 

    # find if a page with giving url existing in graph or not
    def __findPage(self, url):
        for p in self.pages:
            if p.url == url:
                return p
    # find if a page is in the dead_page list
    def __findDeadPage(self, url):
        for p in self.dead_pages:
            if p.url == url:
                return p
    # add a page to graph if the page is not in graph yet
    def __addPage(self,p):
        if not self.__findPage(p.url):
            self.pages.append(p)
            return p
    # add a page to deadpage list if the page is not in deadpage list yet
    def __addDeadPage(self,p):
        if not self.__findDeadPage(p.url):
            self.dead_pages.append(p)
            return p
    def __addNext(self,current, next):
        current.next.append(next)

class Page():
    """Page class"""
    # initiate page
    def __init__(self,url):
        self.url = unicode(url)
        self.next = []
        self.visited = False # flag to ensure each page is visited onece in graph
        self.dead_page = False
        # # parse url to get domain name and url path
        parse_result = urlparse(url)
        self.domain = parse_result.netloc
        self.path = parse_result.path if parse_result.path is not '' else '/'
        self.scheme = parse_result.scheme
        try:
            self.doc = urlopen(self.url)
            self.__findInternalLinks()
        except Exception: # TODO: need to speicify exception
            self.dead_page = True
    # if url is the same, page is the same
    def __eq__(self,other):
        return self.url == other.url
    # in order to put object as key, override hash method
    def __hash__(self):
        return hash(self.url)
    # find all internal url in this page
    def __findInternalLinks(self):
        if self.doc:
            content = self.doc.read()
            soup  = BeautifulSoup(content)
            self.in_links = []
            # parse all hyperlink
            for a in soup.findAll('a', href=True):
                # FIXME: enhance internal link finding
                parts = urlparse(a['href'])
                if parts.netloc == self.domain or parts.netloc =='': # filter only internal link
                    if parts.netloc == self.domain:
                        link = self.scheme + "://" + a['href']
                    else: # empty domain name
                        link = self.scheme + "://" + self.domain + a['href']
                    self.in_links.append(link)
            self.in_links = set(self.in_links) # get unique link

# main function
def mapper():
    # TODO: accept command line parameters
    url = "http://www.beiouyou.com/"
    mp = Page(url)
    graph=Graph()
    graph.buildGraph(mp)
    # Testing
    for p in graph.pages:
        print p.url

if __name__ == "__main__":
    start_time = time.time()
    mapper()
    print "execution time: ", time.time() - start_time, "seconds"
        