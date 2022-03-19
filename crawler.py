# External
import urllib
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import re
import hashlib
import requests

import socket
import time

# Internal
from domain import *
from link_finder import LinkFinder
from queue import *
from project_properties import *

class Crawler:

    PROJECT_NAME = ''
    INSTANCE = ''

    crawlerDB = None

    ALLOWED_DOMAINS = set()

    # This is used for Selenium so that pages with JS will render properly
    WEB_DRIVER_LOCATION = ''
    TIMEOUT = 5
    CHROME_OPTIONS = None
    DRIVER = None

    
    def __init__(self, project_name, timeout, web_driver_location, allowed_domains, crawlerDB, instance):
        self.PROJECT_NAME = project_name
        self.INSTANCE = instance

        self.crawlerDB = crawlerDB

        self.ALLOWED_DOMAINS = allowed_domains

        self.TIMEOUT = timeout
        self.WEB_DRIVER_LOCATION = web_driver_location

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
        print("---------------------------------------------------")
        print()

        # Check if website is reachable first
        header = requests.head(page_url)

        # Get information about the site
        domain = extract_domain(page_url)

        # Get IP of domain, to check if we can call it yet
        ip = socket.gethostbyname(domain)
        timePreviousAccessed = self.crawlerDB.get_time_accessed(ip)

        accessedTime = ""
        if timePreviousAccessed:
            while not self.hasEnoughTimeElapsed(timePreviousAccessed):
                time.sleep(self.TIMEOUT)
            accessedTime = datetime.now().isoformat()
            self.crawlerDB.alter_time_accessed(accessedTime)
        else:
            accessedTime = datetime.now().isoformat()

        gatheredLinksSet, html = self.gather_links(page_url)

        # Filter the appropriate links and modify them
        # TODO - also do canonization!!!!
        gatheredLinksList = list(gatheredLinksSet)
        for i in range(len(gatheredLinksList)):
            # Do not include robots.txt and sitemap.xml links
            if re.search(".*.robots.txt$", gatheredLinksList[i]) or re.search(".*.sitemap.xml$", gatheredLinksList[i]):
                continue
            # Check if it's the proper format, if not, it's a relative link
            if not re.search("^http*.", gatheredLinksList[i]):
                if gatheredLinksList[i][0] == "/":
                    gatheredLinksList[i] = page_url + gatheredLinksList[i]
                else:
                    gatheredLinksList[i] = page_url + "/" + gatheredLinksList[i]

        self.check_duplicates(page_url, html)
        
        gatheredLinksSet = set(gatheredLinksList)

        self.add_links_to_frontier(gatheredLinksSet)

        # --------------------------------------------------------
        # Here is the necceseary stuff for inserting all the
        # necceseary data into the database
        # --------------------------------------------------------

        site_id = self.crawlerDB.find_site(domain)

        if site_id == -1:
            robots_content = self.get_robots_content(domain)
            sitemap = self.get_sitemap_content(page_url)
            
            site_id = self.crawlerDB.insert_site(domain, robots_content, sitemap)

        # Insert page into the database

        # TODO fix this to accomodate different page types
        page_id = self.crawlerDB.insert_page(site_id, 'HTML', page_url, html, header.status_code, accessedTime)

        # Insert hash
        m = hashlib.sha256(html.encode('utf-8'))
        hash = m.digest()
        self.crawlerDB.insert_hash(page_id, hash)

        # TODO - all the other data
        # Also reorder some methods

        # Create a link if the said page is present in the database
        for url in gatheredLinksList:
            self.crawlerDB.insert_link(page_id, self.crawlerDB.find_page(url))
        
        # TODO - check what stuff is binary data, and insert it accordingly
        """ JUST PSEUDOCODE
        gatheredData = # get the data from links
        for data in gatheredData:
            insert_page_data(page_id, "PDF", data.data) # TODO - change it so it's not only PDFs
        """

        # TODO - get image data
        """ JUST PSEUDOCODE
        gatheredImages = # get the data from links
        for image in gatheredImages:
            insert_image(page_id, image.name, image.content.type, image.data, accessedTime)
        """

        # --------------------------------------------------------

    # Downloader using selenium, in case the response doesn't render properly otherwise
    def download_and_render_page(self, page_url):
        self.DRIVER.get(page_url)

        html = self.DRIVER.page_source
        
        return html

    def get_robots_content(self, domain):
        # Remove \n from the sting because that posed a problem
        domain += "/robots.txt"

        html = ''

        try:
            request = urllib.request.Request(
                domain, 
                headers={'User-Agent': self.PROJECT_NAME}
            )

            with urllib.request.urlopen(request) as response: 
                html = response.read().decode("utf-8")
        except:
            print("Not able to retrieve robots.txt")

        return html

    def get_sitemap_content(self, domain):
        domain += "/sitemap.xml" # TODO fix this, it may not reside at this domain

        content = []

        try:
            sitemap_links, _, _ = self.gather_links(domain)
            content = list(sitemap_links)
        except:
            print("Not able to retrieve sitemap.xml")

        return ", ".join(content)

    def gather_links(self, page_url):
        html_string = ''

        try:
            html_string = self.download_and_render_page(page_url)
            finder = LinkFinder(extract_domain(page_url), page_url)
            finder.feed(html_string)
        except Exception as e:
            print(str(e))
            return [], '' 

        return finder.page_links(), html_string

    def url_is_in_database(self, url):
        # If the search returns -1 it means we haven't found the url
        # otherwise we have foudn it
        return self.crawlerDB.find_page(url) != -1

    def add_links_to_frontier(self, links):
        for url in links:
            # Check if the link resides in an allowed domain
            isDomainAllowed = False

            for allowed_domain in self.ALLOWED_DOMAINS:
                if re.search(allowed_domain, extract_domain(url)):
                    isDomainAllowed = True

            if not isDomainAllowed:
                continue

            self.crawlerDB.insert_frontier(url)

    def check_duplicates(self, url, html):
        # TODO - find_page_id(url)
        m = hashlib.sha256(html.encode('utf-8'))
        hash = m.digest()

        savedHash = self.crawlerDB.find_hash(self.crawlerDB.find_page(url))

        return hash == savedHash

    def hasEnoughTimeElapsed(self, timePreviousAccessed):
        prev = time.strptime(timePreviousAccessed)
        curr = time.strptime(datetime.now().isoformat())

        prev = time.mktime(prev)
        curr = time.mktime(curr)

        diff = curr - prev

        seconds = int(diff) % 60

        if seconds > self.TIMEOUT:
            return True
        else:
            return False

    def close_crawler(self):
        self.DRIVER.close()