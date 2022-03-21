# External
import urllib
import urllib.request
import socket
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import hashlib
import time
from datetime import datetime
import re
from bs4 import BeautifulSoup

# Internal
from domain import *
from link_handler import LinkHandler
from queue import *
from project_properties import *

class Crawler:
    
    def __init__(self, project_name, timeout, web_driver_location, allowed_domains, crawlerDB, instance):
        self.PROJECT_NAME = project_name
        self.INSTANCE = instance

        self.crawlerDB = crawlerDB

        self.linkHandler = LinkHandler()

        self.ALLOWED_DOMAINS = allowed_domains

        self.TIMEOUT = timeout
        self.WEB_DRIVER_LOCATION = web_driver_location

        # Possible values for page type
        self.PAGE_TYPE = ['HTML', 'BINARY', 'DUPLICATE', 'FRONITER']
        self.BINARY_LIST = [".pdf", ".doc", ".docx", ".ppt", ".pptx"]
        self.IMAGE_LIST = [".png", ".PNG", ".jpg", ".JPG", ".JPEG", ".jpeg", ".gif", ".GIF"]

        # This is used for Selenium so that pages with JS will render properly
        self.CHROME_OPTIONS = Options()
        self.CHROME_OPTIONS.add_argument("user-agent=" + self.PROJECT_NAME + str(self.INSTANCE))
        self.CHROME_OPTIONS.headless = True
        # self.CHROME_OPTIONS.add_argument("--headless") # This will make the browser open headless
        self.CHROME_OPTIONS.add_experimental_option('excludeSwitches', ['enable-logging']) # Exclude "unimportant" error

        self.DRIVER = webdriver.Chrome(self.WEB_DRIVER_LOCATION, options=self.CHROME_OPTIONS)

    def crawl_page(self, page_url):
        print()
        print("-------------------- THREAD " + str(self.INSTANCE) + " ---------------------")
        print('Now crawling '+ page_url)
        print('At time '+ str(datetime.now()))
        print("---------------------------------------------------")
        print()

        # Some initial filtering (avoiding spider traps, we don't allow links longer than 1k characters)
        if "mailto:" in page_url or len(page_url) > 1000:
            print("INSTANCE " + str(self.INSTANCE) + ": skipping link")
            return

        # If for some reason or other, the website cannot be reached, move on
        try:
            with urllib.request.urlopen(page_url) as response:
                status_code = response.getcode()
                info = response.info()
                content_type = info.get_content_type()
        except:
            return

        domain = extract_domain(page_url) # Get the domain
        ip = socket.gethostbyname(domain) # Get IP of domain, to check if we can call it yet, along with the domain
        


        # --------------------------------------------------
        # Get robots content of the current domain and check
        # what is allowed and what isn't
        # --------------------------------------------------

        robots_content = self.get_robots_content(ip, domain)

        robots_D = []

        if robots_content:
            robots_A = self.getRobotsRulesA(robots_content)
            robots_D = self.getRobotsRulesD(robots_content)

            if DEBUG_MODE:
                # Check if we're not allowed to visit the page by
                # checking the robots file
                print("################################################")
                print("INSTANCE " + str(self.INSTANCE) + ": allowed:\n->"+ str(robots_A))
                print("INSTANCE " + str(self.INSTANCE) + ": disallowed:\n->"+ str(robots_D))
                print("################################################")

            split_url = page_url.split("/")

            if len(split_url) > 3 and "/" + split_url[3] in robots_D:
                print("INSTANCE " + str(self.INSTANCE) + ": robots.txt disallows the use of this page")
                return



        # ---------------------------------------------------------------
        # Check if enough time has elapsed during the domain/IP accession
        # ---------------------------------------------------------------

        timePreviousAccessed = self.crawlerDB.get_time_accessed(ip, domain)

        if self.crawlerDB.get_time_accessed_exact(ip, domain) == []:
            accessedTime = time.time()
            self.crawlerDB.insert_ip(ip, domain, accessedTime)
        else:
            while not self.hasEnoughTimeElapsed(timePreviousAccessed):
                time.sleep(self.TIMEOUT)
            accessedTime = time.time()
            self.crawlerDB.alter_time_accessed(ip, domain, accessedTime)

        accessedTime = datetime.now().isoformat()
        gatheredLinksSet, html = self.gather_links(page_url, robots_D)

        # If we got the same link we reside in right now, we get rid of it
        try:
            gatheredLinksSet.remove(page_url)
        except:
            if DEBUG_MODE:
                print("Removed link pointing to itself")

        # Filter the appropriate links and modify them
        gatheredLinksList = list(gatheredLinksSet)
        for i in range(len(gatheredLinksList)):
            # Do not include robots.txt and sitemap.xml links
            if re.search(".*.robots.txt$", gatheredLinksList[i]) or re.search(".*.sitemap.xml$", gatheredLinksList[i]):
                continue
            # Check if it's the proper format, if not, it's a relative link
            gatheredLinksList[i] = extendRelativePage(page_url, gatheredLinksList[i])


        # --------------------------------------------------------
        # Here is the necceseary stuff for inserting all the
        # necceseary data into the database
        # --------------------------------------------------------

        # INSERT SITE INTO THE DATABASE

        site_id = self.crawlerDB.find_site(domain)

        if site_id == -1:
            # Get sitemap
            sitemapxml = "sitemap.xml"
            if robots_content:
                sitemapxml = self.getSitemap(robots_content)

            sitemap_content = self.get_sitemap_content(ip, domain, sitemapxml)

            sitemap_urls = []
            if sitemap_content:
                sitemap_urls = self.processSitemap(sitemap_content)

            # Put the links into frontier
            if DEBUG_MODE:
                print("Adding sitemap content to frontier")
            gatheredLinksList = gatheredLinksList + sitemap_urls

            #Put the links into database
            site_id = self.crawlerDB.insert_site(domain, robots_content, sitemap_content)


        # INSERT PAGE INTO THE DATABASE

        # Checking page type
        duplicateId = self.check_duplicates(html)
        if duplicateId != -1:
            page_type = self.PAGE_TYPE[2]
            html = ''
        elif content_type != "text/html":
            page_type = self.PAGE_TYPE[1]
            html = ''
        else:
            page_type = self.PAGE_TYPE[0]

        page_id = self.crawlerDB.insert_page(site_id, page_type, page_url, html, status_code, accessedTime)

        if duplicateId != -1:
            self.crawlerDB.insert_link(page_id, duplicateId)
            return # Skip all the other stuff since the site was already processed
        
        # INSERT HASH
        m = hashlib.sha256(html.encode('utf-8'))
        hash = m.digest()
        self.crawlerDB.insert_hash(page_id, hash)
        
        # INSERT IMAGE CONTENTS FROM URL LIST INTO THE DATABASE

        imagesList = list(set(self.linkHandler.imgLinks(html, robots_D, page_url))) # Getting rid of duplicates

        for image in imagesList:
            extension = self.linkHandler.checkIfImage(image)

            if extension == self.IMAGE_LIST[0] or extension == self.IMAGE_LIST[1]:
                self.crawlerDB.insert_image(page_id, image, "PNG", b"None", accessedTime)
            elif extension == self.IMAGE_LIST[2] or extension == self.IMAGE_LIST[3] or extension == self.IMAGE_LIST[4] or extension == self.IMAGE_LIST[5]:
                self.crawlerDB.insert_image(page_id, image, "JPG", b"None", accessedTime)
            elif extension == self.IMAGE_LIST[6] or extension == self.IMAGE_LIST[7]:
                self.crawlerDB.insert_image(page_id, image, "GIF", b"None", accessedTime)

        # INSERT BINARY CONTENTS FROM URL LIST INTO THE DATABASE

        # We use a while loop because we'll be deleting elements from
        # the list as we loop trough it
        i = 0
        while i < len(gatheredLinksList):
            extension = self.linkHandler.checkIfBinary(gatheredLinksList[i])

            if extension != ".html":
                binary_type = ""

                if extension == self.BINARY_LIST[0]:
                    binary_type = "PDF"
                elif extension == self.BINARY_LIST[1]:
                    binary_type = "DOC"
                elif extension == self.BINARY_LIST[2]:
                    binary_type = "DOCX"
                elif extension == self.BINARY_LIST[3]:
                    binary_type = "PPT"
                else:
                    binary_type = "PPTX"

                self.crawlerDB.insert_page_data(page_id, binary_type, b"None")

                gatheredLinksList.pop(i)
            else:
                i += 1

        # --------------------------------------------------------

        if DEBUG_MODE:
            print()
            print("****************** LIST OF GATHERED LINKS **********************")
            print(gatheredLinksList)
            print("****************************************************************")
            print()

        gatheredLinksSet = set(gatheredLinksList)
        self.add_links_to_frontier(gatheredLinksSet)

    # -------------------------------------------------------
    # Downloader using selenium, in case the response doesn't
    # render properly otherwise
    # -------------------------------------------------------

    def download_and_render_page(self, page_url):
        self.DRIVER.get(page_url)
        html = self.DRIVER.page_source
        return html

    # -------------------------------
    # GET ALL THE LINKS FROM THE PAGE
    # -------------------------------

    def gather_links(self, page_url, robots_rules):
        html_string = ''

        html_string = self.download_and_render_page(page_url)
        links = self.linkHandler.hrefLinks(html_string, robots_rules, page_url) + self.linkHandler.onClickLinks(html_string, robots_rules, page_url)

        return set(links), html_string

    # ------------------------------------------
    # CHECK IF LINK IS ON THE APPROPRIATE DOMAIN
    # ------------------------------------------

    def add_links_to_frontier(self, links):
        for url in links:
            # Check if the link resides in an allowed domain
            isDomainAllowed = False

            for allowed_domain in self.ALLOWED_DOMAINS:
                if len(url.split("/")) > 2 and re.search(allowed_domain, extract_domain(url)):
                    isDomainAllowed = True

            if not isDomainAllowed:
                continue

            self.crawlerDB.insert_frontier(url)

    # ------------------
    # DUPLICATE CHECKING
    # ------------------

    def check_duplicates(self, html):
        m = hashlib.sha256(html.encode('utf-8'))
        hash = m.digest()

        return self.crawlerDB.find_hash(hash)

    # -----------------------------
    # TIME CHECKING BETWEEN FETCHES
    # -----------------------------

    def hasEnoughTimeElapsed(self, prevAll):
        for prev in prevAll:
            curr = time.time()
            diff = curr - prev

            if diff > self.TIMEOUT:
                if DEBUG_MODE:
                    print("INSTANCE " + str(self.INSTANCE) + ": Enough time has passed")
            else:
                if DEBUG_MODE:
                    print("INSTANCE " + str(self.INSTANCE) + ": Not enough time has passed (" + str(diff) + "s)")
                return False

        # Only return True if it's enough time has passed for all of them
        return True
    
    # -----
    # ROBOT
    # -----

    def get_robots_content(self, ip, domain):
        html = self.crawlerDB.find_site_robots(domain)

        if html == None:
            timePreviousAccessed = self.crawlerDB.get_time_accessed(ip, domain)

            while not self.hasEnoughTimeElapsed(timePreviousAccessed):
                time.sleep(self.TIMEOUT)

            accessedTime = time.time()
            self.crawlerDB.alter_time_accessed(ip, domain, accessedTime)

            domain = "http://" + domain + "/robots.txt"

            if DEBUG_MODE:
                print("INSTANCE " + str(self.INSTANCE) + ": Sending robots request to the webpage")
                print("INSTANCE " + str(self.INSTANCE) + ": " + domain)
            try:
                request = urllib.request.Request(
                    domain, 
                    headers={'User-Agent': self.PROJECT_NAME}
                )

                with urllib.request.urlopen(request) as response: 
                    html = response.read().decode("utf-8")
            except:
                if DEBUG_MODE:
                    print("INSTANCE " + str(self.INSTANCE) + ": Not able to retrieve robots.txt")
        else:
            if DEBUG_MODE:
                print("INSTANCE " + str(self.INSTANCE) + ": Found robots_content in the database")
            accessedTime = time.time()
            self.crawlerDB.insert_ip(ip, domain, accessedTime)

        return html

    # -----------
    # ROBOT RULES
    # -----------

    def getRobotsRulesD(self, robotsFile):
        robots_split = robotsFile.split("\n")
        rules_disallowed = []
        for i in robots_split:
            if "Disallow:" in i:
                temp = i.split(" ")
                if(len(temp) >= 2):
                    temp2 = i.split(" ")[1]
                    rules_disallowed.append(temp2)
        return rules_disallowed

    def getRobotsRulesA(self, robotsFile):
        robots_split = robotsFile.split("\n")
        rules_allowed = []
        for i in robots_split:
            if "Allow:" in i:
                temp = i.split(" ")
                if(len(temp) >= 2):
                    temp2 = i.split(" ")[1]
                    rules_allowed.append(temp2)
        return rules_allowed

    # -------
    # SITEMAP
    # -------

    def get_sitemap_content(self, ip, domain, sitemapxml):
        html = self.crawlerDB.find_site_sitemap(domain)

        if html == None:
            timePreviousAccessed = self.crawlerDB.get_time_accessed(ip, domain)

            while not self.hasEnoughTimeElapsed(timePreviousAccessed):
                time.sleep(self.TIMEOUT)

            accessedTime = time.time()
            self.crawlerDB.alter_time_accessed(ip, domain, accessedTime)

            domain = "http://" + domain + "/" + sitemapxml

            if DEBUG_MODE:
                print("INSTANCE " + str(self.INSTANCE) + ": Sending robots request to the webpage")
                print("INSTANCE " + str(self.INSTANCE) + ": " + domain)
            try:
                request = urllib.request.Request(
                    domain, 
                    headers={'User-Agent': self.PROJECT_NAME}
                )

                with urllib.request.urlopen(request) as response: 
                    html = response.read().decode("utf-8")
            except:
                if DEBUG_MODE:
                    print("INSTANCE " + str(self.INSTANCE) + ": Not able to retrieve robots.txt")
        else:
            if DEBUG_MODE:
                print("INSTANCE " + str(self.INSTANCE) + ": Found robots_content in the database")
            accessedTime = time.time()
            self.crawlerDB.insert_ip(ip, domain, accessedTime)

        return html

    # -------------
    # SITEMAP LINKS
    # -------------

    def getSitemap(self, robotsFile):
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

    def processSitemap(self, sitemapFile):
        # returns a list of URLs of all the websites listed in sitemap
        # parsing, canonization? klic funkcije - a lahko kar beautiful soup uporabim?
        file_s = BeautifulSoup(sitemapFile, features='html.parser')
        url_sitemap = []

        for i in file_s:
            url_sitemap.append(i.text) 

        return url_sitemap

    # -------------------
    # CLOSING THE CRAWLER
    # -------------------

    def close_crawler(self):
        self.DRIVER.close()