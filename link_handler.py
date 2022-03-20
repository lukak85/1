from html.parser import HTMLParser

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

    def imgLinks(self, html, robots_rules):
        all_img = html.find_all("img")
        end = 0
        for element in all_img:
            #if 'src' in element: # mogoče malo drugače - ne vem če to dela
            if element.hasattr('src'):
                img_link = element['src']
                
                if len(img_link) != 0 and img_link is not None:
                    
                    for r in robots_rules:
                        if r in img_link:
                            end = 1

    def hrefLinks(self, html, robots_rules):
        all_href = html.find_all("a")
        end = 0
        for element in all_href:
            if element is not None and element.hasattr('href'): # verjetno nekaj drugače kot "in" - hasattr()
                href_val = element.get('href')

                if len(href_val) != 0 and href_val is not None:
                    for r in robots_rules:
                        if r in href_val:
                            end = 1

    def onClickLinks(self, html, robots_rules):
        all_onClick = html.find_all("onclick")
        end = 0
        for element in all_onClick:
            if element is not None and element.hasattr('onclick'): # verjetno nekaj drugače kot "in" - hasattr()
                onClick_value = element.get('onclick')

                if len(onClick_value) != 0 and onClick_value is not None:
                    for r in robots_rules:
                        if r in onClick_value:
                            end = 1
