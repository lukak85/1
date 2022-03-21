import urllib
from urllib.parse import urlparse
import re
from html.parser import HTMLParser
from bs4 import BeautifulSoup
from numpy import full
from domain import *
from url_normalize import url_normalize

class LinkHandler(HTMLParser):

    def __init__(self):
        super().__init__()

        self.BINARY_LIST = [".pdf", ".doc", ".docx", ".ppt", ".pptx"]
        self.IMAGE_LIST = [".png", ".PNG", ".jpg", ".JPG", ".JPEG" ".jpeg", ".gif", ".GIF"]
        self.ELIMINATE_LIST = ["http://www", "http://www.", "https://www", "http://www.", "http://," "https://", "www", "www.", ".html" ]
        self.HEAD_LIST = ["favicon.ico", "maps.googleapis.", "fonts.googleapis."]

    def checkIfBinary(self, url):
        isHtml = ".html"
        for element in self.BINARY_LIST:
            d = len(element)
            if url[-d:] == element:
                return element
        return isHtml

    def checkIfImage(self, url):
        isNot = None
        for image in self.IMAGE_LIST:
            d = len(image)
            if url[-d:] == image:
                return [url]
        return isNot

    def imgLinks(self, html_str, robots_rules, page_url):
        html = BeautifulSoup(html_str, 'html.parser')
        all_img = html.find_all("img")

        returning_images = []
        
        for element in all_img:
            #if 'src' in element: # mogoče malo drugače - ne vem če to dela
            if element.has_attr('src'):
                img_link = element['src']
                
                if len(img_link) != 0 and img_link is not None:
                    noneProhibited = True

                    for r in robots_rules:
                        if r in img_link:
                            noneProhibited = False
                            
                    if noneProhibited:
                        full_url = extendRelativePage(page_url, img_link)
                        full_url = self.urlCanon(full_url)
                        returning_images.append(full_url)

        return returning_images

    def hrefLinks(self, html_str, robots_rules, page_url):
        html = BeautifulSoup(html_str, 'html.parser')
        all_href = html.find_all("a")

        returning_href_links = []
        
        for element in all_href:
            if element is not None and element.has_attr('href'): # verjetno nekaj drugače kot "in" - hasattr()
                href_val = element['href']

                if len(href_val) != 0 and href_val is not None:
                    noneProhibited = True

                    for r in robots_rules:
                        if r in href_val:
                            noneProhibited = False
                            
                    if noneProhibited:
                        full_url = extendRelativePage(page_url, href_val)
                        full_url = self.urlCanon(full_url)
                        returning_href_links.append(full_url)

        return returning_href_links
                

    def onClickLinks(self, html_str, robots_rules, page_url):
        html = BeautifulSoup(html_str, 'html.parser')
        all_onClick = html.find_all("onclick")

        returning_onclick = []
        
        for element in all_onClick:
            if element is not None and element.has_attr('onclick'): # verjetno nekaj drugače kot "in" - hasattr()
                onClick_value = element.get('onclick')

                if len(onClick_value) != 0 and onClick_value is not None:
                    noneProhibited = True

                    for r in robots_rules:
                        if r in onClick_value:
                            noneProhibited = False

                    if noneProhibited:
                        full_url = extendRelativePage(page_url, onClick_value)
                        full_url = self.urlCanon(full_url)
                        returning_onclick.append(full_url)

        return returning_onclick

    # ---------
    # TEMPORARY
    # ---------

    # ----------------
    # URL CANONIZATION
    # ----------------

    def urlCanon(self, url):

        # decoding needlessly encoded characters
        url = urllib.parse.unquote(url)

        parsed_url = urlparse(url)

        scheme = parsed_url.scheme
        scheme = str(scheme)
        # relative to absolute
        if not scheme or scheme is None:
            scheme = "http"
        scheme = scheme + ("://")

        netloc = parsed_url.netloc
        # relative to absolute
        netloc = str(netloc)
        if netloc is None or not netloc:
            netloc = extract_domain(url)

        netloc = netloc.lower()
        # removing www. if not beforehand
        netloc = re.sub("www./", "/", netloc)
        # removing default port number
        netloc = parsed_url.hostname

        add = 1
        path = parsed_url.path
        # add trailing slash to root directory if no path
        if (path == "" or path == "/"):
            path = ""
            netloc = netloc + "/"
        # resolving path
        # removing default filename
        path = re.sub("/index\.(html|htm|php)", "/", path)
        # encoding
        path = urllib.parse.quote(path)

        # add / if the link has no .pdf, ....
        if len(path) >= 5 and (path[len(path)-4] == "." or path[len(path)-5] == "."):
            add = 0
        if (add):
            path = path + "/"

        canon_url = scheme + netloc + path
        canon_url = url_normalize(canon_url)

        return canon_url
