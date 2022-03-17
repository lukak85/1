from distutils.log import error
from http.client import ImproperConnectionState
from os import access
import queue
from urllib.request import urlopen
import time
from xml import dom

from mm import *
from domain import *
from database import *
from link_finder import LinkFinder
from queue import *

import urllib
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import re

class Crawler:
    # Links in waiting list, crawler will take one and connect to that page, 
    # grab html and use LinkFinder

    # Class variables
    PROJECT_NAME = ''
    QUEUE_FILE = ''
    queueInstance = None

    ALLOWED_DOMAINS = set()
    STARTING_PAGES = []

    # This is used for Selenium so that pages with JS will render properly
    WEB_DRIVER_LOCATION = ''
    TIMEOUT = 5
    CHROME_OPTIONS = None
    DRIVER = None
    
    def __init__(self, project_name, timeout, web_driver_location, starting_pages, allowed_domains, queueInstance):
        # To be sure all Crawlers are crawling the same site
        self.PROJECT_NAME = project_name
        
        self.STARTING_PAGES = starting_pages
        self.ALLOWED_DOMAINS = allowed_domains

        self.queueInstance = queueInstance

        self.TIMEOUT = timeout
        self.WEB_DRIVER_LOCATION = web_driver_location

        self.CHROME_OPTIONS = Options()
        self.CHROME_OPTIONS.add_argument("user-agent=" + self.PROJECT_NAME)
        self.CHROME_OPTIONS.add_argument("--headless") # This will make the browser not open
        self.CHROME_OPTIONS.add_experimental_option('excludeSwitches', ['enable-logging']) # Exclude "unimportant" error

        self.DRIVER = webdriver.Chrome(self.WEB_DRIVER_LOCATION, options=self.CHROME_OPTIONS)

    def boot(self):
        self.crawl_page(list(self.queueInstance.queue)[0])

    def crawl_page(self, page_url):
        # If queue is empty, end crawling
        if not queue:
            self.DRIVER.close()

        # Else do the usual stuff
        if not self.url_is_in_database(page_url):
            print('Now crawling '+ page_url)
            print('Queue: '+ str(len(self.queueInstance.queue)))

            accessedTime = datetime.now().isoformat()
            gatheredLinksSet, html, html_bytes = self.gather_links(page_url)

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
            
            gatheredLinksSet = set(gatheredLinksList)

            self.add_links_to_queue(gatheredLinksSet)

            # --------------------------------------------------------
            # Here is the necceseary stuff for inserting all the
            # necceseary data into the database
            # --------------------------------------------------------

            # Get information about the site
            domain = extract_domain(page_url)
            print(domain)
            site_id = find_site(domain)

            if site_id == -1:
                robots_content = self.get_robots_content(domain)
                sitemap = self.get_sitemap_content(page_url)
                
                site_id = insert_site(domain, robots_content, sitemap)

            # Insert page into the database

            # TODO fix this to accomodate different page types
            page_id = insert_page(site_id, 'HTML', page_url, html, -1, accessedTime)

            # TODO - all the other data
            # Also reorder some methods

            # Create a link if the said page is present in the database
            for url in gatheredLinksList:
                insert_link(page_id, find_page(url))
            
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

            # Update frontier after we finished crawling the webpage.
            # Uncomment this when we'll run the crawler for final
            # results:
            # self.update_files()

            # Remove the link at the very end, in case something went wrong
            self.queueInstance.queue.remove(page_url)

    # Downloader using selenium, in case the response doesn't render properly otherwise
    def download_and_render_page(self, page_url):
        self.DRIVER.get(page_url)

        time.sleep(self.TIMEOUT)
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
        html_bytes = None

        print(page_url)

        try:
            response = urlopen(page_url)
            if 'text/html' in response.getheader('Content-Type'):
                html_bytes = response.read()

                # Commented because of the before mentioned problem without
                # Selenium
                # html_string = html_bytes.decode("utf-8")

                # Get HTML using 
                html_string = self.download_and_render_page(page_url)
            finder = LinkFinder(extract_domain(page_url), page_url)
            finder.feed(html_string)
        except Exception as e:
            print(str(e))
            return [], '' , None

        return finder.page_links(), html_string, html_bytes

    def url_is_in_database(self, url):
        # If the search returns -1 it means we haven't found the url
        # otherwise we have foudn it
        return find_page(url) != -1

    def add_links_to_queue(self, links):
        for url in links:
            # Check if the link is not already present in the database
            if url in self.queueInstance.queue or self.url_is_in_database(url):
                continue
            
            # Check if the link resides in an allowed domain
            isDomainAllowed = False
            for allowed_domain in self.ALLOWED_DOMAINS:
                if re.search(allowed_domain, extract_domain(url)):
                    isDomainAllowed = True
            if not isDomainAllowed:
                continue

            self.queueInstance.queue.add(url)
    
    def update_files(self):
        set_to_file(self.queueInstance.queue, self.QUEUE_FILE)
