from urllib.request import urlopen
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import threading
import queue
import time
import sys
import getopt
from util import *

class GraphThread(threading.Thread):
    def __init__(self, p, graph, queue):
        threading.Thread.__init__(self)
        self.queue = queue
        self.graph = graph
        self.p = p

    def run(self):
        while True:
            link = self.queue.get()
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
                self.graph.addNext(self.p, page)
            self.graph.buildGraph(page)
            self.queue.task_done()

class Graph():
    def __init__(self):
        self.pages = []
        self.dead_pages = []

    def buildGraph(self, p):
        if not p.visited and not p.dead_page:
            p.visited = True
            if not self.findPage(p.url):
                self.addPage(p)
            for link in p.in_links:
                page = self.findPage(link) if self.findPage(link) else self.findDeadPage(link)
                if page:
                    pass
                else:
                    page = Page(link)
                    if not page.dead_page:
                        self.addPage(page)
                    else:
                        self.addDeadPage(page)
                if not page.dead_page:
                    self.addNext(p, page)
                self.buildGraph(page)

    def findPage(self, url):
        for p in self.pages:
            if p.url == url:
                return p

    def findDeadPage(self, url):
        for p in self.dead_pages:
            if p.url == url:
                return p

    def addPage(self, p):
        if not self.findPage(p.url):
            self.pages.append(p)
            return p

    def addDeadPage(self, p):
        if not self.findDeadPage(p.url):
            self.dead_pages.append(p)
            return p

    def addNext(self, current, next_page):
        current.next.append(next_page)

class Page():
    def __init__(self, url):
        self.url = str(url)
        self.next = []
        self.visited = False
        self.dead_page = False
        parse_result = urlparse(url)
        self.domain = parse_result.netloc
        self.path = parse_result.path if parse_result.path != '' else '/'
        self.scheme = parse_result.scheme
        try:
            self.doc = urlopen(self.url)
            self.__findInternalLinks()
        except Exception as e:
            self.dead_page = True

    def __eq__(self, other):
        return self.url == other.url

    def __hash__(self):
        return hash(self.url)

    def __findInternalLinks(self):
        if self.doc:
            content = self.doc.read()
            soup = BeautifulSoup(content, 'html.parser')
            self.in_links = []
            for a in soup.find_all('a', href=True):
                parts = urlparse(a['href'])
                if parts.netloc == self.domain or parts.netloc == '':
                    if parts.netloc == self.domain:
                        if not parts.scheme:
                            link = self.scheme + "://" + a['href']
                        else:
                            link = a['href']
                    else:
                        link = self.scheme + "://" + self.domain + a['href']
                    self.in_links.append(link)
                    print(self.url + " has next: " + a['href'])
            self.in_links = set(self.in_links)

def mapper(argv):
    url = None
    try:
        opts, args = getopt.getopt(argv, "hl:")
    except getopt.GetoptError:
        print_usage()

    for opt, arg in opts:
        if opt == '-h':
            print_usage()
            sys.exit()
        elif opt == '-l':
            url = url_fix(arg)

    if not url:
        print_usage()

    mp = Page(url)
    graph = Graph()
    graph.buildGraph(mp)
    print(len(graph.pages))
    for p in graph.pages:
        print(p.url)

if __name__ == "__main__":
    start_time = time.time()
    mapper(sys.argv[1:])
    print("execution time: ", time.time() - start_time, "seconds")
