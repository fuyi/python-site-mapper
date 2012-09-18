from urllib2 import * # http client
from BeautifulSoup import BeautifulSoup # html parser
from urlparse import urlparse # url parser
import threading
import Queue
import time

class GraphThread(threading.Thread):
    def __init__(self, p, graph, queue):
        threading.Thread.__init__(self)
        self.queue = queue
        self.graph = graph
        self.p = p
    def run(self):
        while True:
            # print self.getName() + " is running"
            link = self.queue.get() # get link from queue
            page = self.graph.findPage(link) if self.graph.findPage(link) else self.graph.findDeadPage(link)
            if page:
                pass
            else:
                page = Page(link)
                if not page.dead_page:
                    self.graph.addPage(page)
                else:
                    self.graph.addDeadPage(page)
            if not page.dead_page:
                self.graph.addNext(self.p,page)
            self.graph.buildGraph(page)
            self.queue.task_done()

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
            if not self.findPage(p.url):
                self.addPage(p)
            # step 3, generate pages for each internal link and add to page next, add page to graph if it is a new page
            # method 1: multithread implementation
            queue = Queue.Queue()
            for link in p.in_links:
                queue.put(link)
            for i in range(10):
                t = GraphThread(p,self,queue)
                t.setDaemon(True)
                t.start()
            queue.join()
            # method 2: synchronized implementation
            # for link in p.in_links:
            #     page = self.findPage(link) if self.findPage(link) else self.findDeadPage(link)
            #     if page: # page already exist on graph, do nothing
            #         pass
            #     else: 
            #         page = Page(link) # page not exist, create new page
            #         if not page.dead_page:
            #             self.addPage(page) # add new page to graph if not dead page
            #         else: # page is dead page, add to deadpage list
            #             self.addDeadPage(page)
            #     if not page.dead_page:
            #         self.addNext(p,page) # add page to current pages next list if not deadpage
            #     self.buildGraph(page) # recursively build graph

    # find if a page with giving url existing in graph or not
    def findPage(self, url):
        for p in self.pages:
            if p.url == url:
                return p
    # find if a page is in the dead_page list
    def findDeadPage(self, url):
        for p in self.dead_pages:
            if p.url == url:
                return p
    # add a page to graph if the page is not in graph yet
    def addPage(self,p):
        if not self.findPage(p.url):
            self.pages.append(p)
            return p
    # add a page to deadpage list if the page is not in deadpage list yet
    def addDeadPage(self,p):
        if not self.findDeadPage(p.url):
            self.dead_pages.append(p)
            return p
    def addNext(self,current, next):
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
        except Exception as e: # TODO: need to speicify exception
            self.dead_page = True
            # print str(e)
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
    print len(graph.pages)
    for p in graph.pages:
        print p.url

if __name__ == "__main__":
    start_time = time.time()
    mapper()
    print "execution time: ", time.time() - start_time, "seconds"
        