import urlcanon
from urllib.parse import urlparse

# določanje vrste URL-ja (torej al je HTML, BINARY, ...)

BINARY_LIST = [".pdf", ".doc", ".docx", ".ppt", ".pptx"]
IMAGE_LIST = [".png", ".jpg", ".jpeg", ".gif"]
ELIMINATE_LIST = ["http://www", "http://www.", "https://www", "http://www.", "http://," "https://", "www", "www.", ".html" ]

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



# možno da se podatek o datoteki ne nahaja v končnici URLja in je zato treba preverit še head content


def urlCanonization(url):
    # odstranimo www. itd
    # kanoniziranje URL-jev 
    # (torej da bo sam ena instanca URL-ja v db, torej se da ven te parametre in podobne stvari)
    for element in ELIMINATE_LIST:
        if element in url:
            url = url.replace(element, "")
    
    pass


