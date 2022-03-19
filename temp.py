from cgitb import html
import urlcanon
from urllib.parse import urlparse
from bs4 import BeautifulSoup

# določanje vrste URL-ja (torej al je HTML, BINARY, ...)

BINARY_LIST = [".pdf", ".doc", ".docx", ".ppt", ".pptx"]
IMAGE_LIST = [".png", ".PNG", ".jpg", ".JPG", ".JPEG" ".jpeg", ".gif", ".GIF"]
ELIMINATE_LIST = ["http://www", "http://www.", "https://www", "http://www.", "http://," "https://", "www", "www.", ".html" ]
HEAD_LIST = ["favicon.ico", "maps.googleapis.", "fonts.googleapis."]

def checkIfBinary(url):
    isHtml = ".html"
    for element in BINARY_LIST:
        d = len(element)
        if url[-d:] == element:
            return element
    return isHtml

def checkIfImage(url):
    isNot = None
    for image in IMAGE_LIST:
        d = len(image)
        if url[-d:] == image:
            return [url]
    return isNot


# pridobivanje img linkov - bo del neke fetch funkcije, ki dobi html vsebino?
# iz robots.txt dobimo seznam "pravil" = robots_rules = [] 

robots_rules = []
all_img = html_content.find_all("img")
def imgLinks():
    end = 0
    for element in all_img:
        #if 'src' in element: # mogoče malo drugače - ne vem če to dela
        if element.hasattr('src'):
            img_link = element['src']
            
            if len(img_link) != 0 and img_link is not None:
                
                for r in robots_rules:
                    if r in img_link:
                        end = 1
                # TODO: urejanje url-ja - kanonizacija itd, klic funkcije
                # TODO: zapis v db
                
                    
# pridobivanje href - kot imgLinks fora
all_href = html_content.find_all("a")
def hrefLinks():
    end = 0
    for element in all_href:
        if element is not None and element.hasattr('href'): # verjetno nekaj drugače kot "in" - hasattr()
            href_val = element.get('href')

            if len(href_val) != 0 and href_val is not None:
                for r in robots_rules:
                    if r in href_val:
                        end = 1

            # TODO: kanonizacija itd, klic funkcije
            # TODO: zapis v db


# onclick="myFunction()
all_onClick = html_content.find_all("onclick")
def onClickLinks():
    end = 0
    for element in all_onClick:
        if element is not None and element.hasattr('onclick'): # verjetno nekaj drugače kot "in" - hasattr()
            onClick_value = element.get('onclick')

            if len(onClick_value) != 0 and onClick_value is not None:
                for r in robots_rules:
                    if r in onClick_value:
                        end = 1
            # TODO: kanonizacija, klic funkcije
            # TODO: shranjevanje



# prebiranje dovoljenj iz robots.txt in sitemap.xml,
def getRobotsRulesD(robotsFile):
    robots_split = robotsFile.split("\n")
    rules_disallowed = []
    for i in robots_split:
        if "Disallow:" in i:
            temp = i.split(" ")
            if(len(temp) >= 2):
                temp2 = i.split(" ")[1]
                rules_disallowed.append(temp2)
    return rules_disallowed

def getRobotsRulesA(robotsFile):
    robots_split = robotsFile.split("\n")
    rules_allowed = []
    for i in robots_split:
        if "Allow:" in i:
            temp = i.split(" ")
            if(len(temp) >= 2):
                temp2 = i.split(" ")[1]
                rules_allowed.append(temp2)
    return rules_allowed

def getSitemap(robotsFile):
    # iz robots.txt sklepam?
    robots_split = robotsFile.split("\n")
    sitemapFile = ""

    for i in robots_split:
        if "Sitemap:" in i:
            temp = i.split(" ")
            if(len(temp) >= 2):
                temp2 = i.split(" ")[1]
                sitemapFile = temp2
    return sitemapFile

def processSitemap(sitemapFile):
    # returns a list of URLs of all the websites listed in sitemap
    # parsing, canonization? klic funkcije - a lahko kar beautiful soup uporabim?
    file_s = BeautifulSoup(sitemapFile, features='html.parser')
    url_sitemap = []

    for i in file_s:
        url_sitemap.append(i.text) 

    return url_sitemap




# možno da se podatek o datoteki ne nahaja v končnici URLja in je zato treba preverit še head content
# def getLinksFromHead():


def urlCanonization(url):
    # odstranimo www. itd
    # kanoniziranje URL-jev 
    # (torej da bo sam ena instanca URL-ja v db, torej se da ven te parametre in podobne stvari)
    for element in ELIMINATE_LIST:
        if element in url:
            url = url.replace(element, "")
    
    pass



