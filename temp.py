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


def urlCanonization(url):
    # odstranimo www. itd
    for element in ELIMINATE_LIST:
        if element in url:
            url = url.replace(element, "")
    
    return url


