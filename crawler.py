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
    queue = set() # waiting list

    ALLOWED_DOMAINS = set()
    STARTING_PAGES = []

    # This is used for Selenium so that pages with JS will render properly
    WEB_DRIVER_LOCATION = ''
    TIMEOUT = 1
    CHROME_OPTIONS = None
    DRIVER = None
    
    @staticmethod
    def __init__(project_name, timeout, web_driver_location, starting_pages, allowed_domains):
        # To be sure all Crawlers are crawling the same site
        Crawler.PROJECT_NAME = project_name
        Crawler.QUEUE_FILE = Crawler.PROJECT_NAME + '/frontier.txt'

        Crawler.STARTING_PAGES = starting_pages
        Crawler.ALLOWED_DOMAINS = allowed_domains

        Crawler.TIMEOUT = timeout
        Crawler.WEB_DRIVER_LOCATION = web_driver_location

        Crawler.CHROME_OPTIONS = Options()
        Crawler.CHROME_OPTIONS.add_argument("user-agent=" + Crawler.PROJECT_NAME)
        Crawler.CHROME_OPTIONS.add_argument("--headless") # This will make the browser not open
        Crawler.CHROME_OPTIONS.add_experimental_option('excludeSwitches', ['enable-logging']) # Exclude "unimportant" error

        Crawler.DRIVER = webdriver.Chrome(Crawler.WEB_DRIVER_LOCATION, options=Crawler.CHROME_OPTIONS)

        Crawler.queue = file_to_set(Crawler.QUEUE_FILE)

    @staticmethod
    def boot():
        Crawler.crawl_page(list(Crawler.queue)[0])

    @staticmethod
    def crawl_page(page_url):
        # If queue is empty, end crawling
        if not queue:
            Crawler.DRIVER.close()

        # Else do the usual stuff
        if not Crawler.url_is_in_database(page_url):
            print('Now crawling '+ page_url)
            print('Queue: '+ str(len(Crawler.queue)))

            accessedTime = datetime.now().isoformat()
            gatheredLinksSet, html, html_bytes = Crawler.gather_links(page_url)


            # Check if it's the proper format, if not, it's a relative link
            gatheredLinksList = list(gatheredLinksSet)
            for i in range(0, len(gatheredLinksList)):
                if not re.search("http*.", gatheredLinksList[i]):
                    if gatheredLinksList[i][0] == "/":
                        gatheredLinksList[i] = page_url + gatheredLinksList[i]
                    else:
                        gatheredLinksList[i] = page_url + "/" + gatheredLinksList[i]
            
            gatheredLinksSet = set(gatheredLinksList)

            Crawler.add_links_to_queue(gatheredLinksSet)

            # --------------------------------------------------------
            # Here is the necceseary stuff for inserting all the
            # necceseary data into the database
            # --------------------------------------------------------

            # Get information about the site
            domain = extract_domain(page_url)
            print(domain)
            site_id = find_site(domain)

            if site_id == -1:
                robots_content = Crawler.get_robots_content(domain)
                sitemap = Crawler.get_sitemap_content(page_url)
                
                site_id = insert_site(domain, robots_content, sitemap)

            # Insert page into the database

            # TODO fix this to accomodate different page types
            insert_page(site_id, 'HTML', page_url, html, -1, accessedTime)

            # TODO - all the other data
            # Also reorder some methods


            # --------------------------------------------------------

            # Update frontier after we finished crawling the webpage.
            # Uncomment this when we'll run the crawler for final
            # results:
            # Crawler.update_files()

            # Remove the link at the very end, in case something went wrong
            Crawler.queue.remove(page_url)

    # Downloader using selenium, in case the response doesn't render properly otherwise
    @staticmethod
    def download_and_render_page(page_url):
        Crawler.DRIVER.get(page_url)

        time.sleep(Crawler.TIMEOUT)
        html = Crawler.DRIVER.page_source
        
        return html

    @staticmethod
    def get_robots_content(domain):
        # Remove \n from the sting because that posed a problem
        domain += "/robots.txt"

        html = ''

        try:
            request = urllib.request.Request(
                domain, 
                headers={'User-Agent': Crawler.PROJECT_NAME}
            )

            with urllib.request.urlopen(request) as response: 
                html = response.read().decode("utf-8")
        except:
            print("Not able to retrieve robots.txt")

        return html

    @staticmethod
    def get_sitemap_content(domain):
        domain += "/sitemap.xml" # TODO fix this, it may not reside at this domain

        content = []

        try:
            sitemap_links, _, _ = Crawler.gather_links(domain)
            content = list(sitemap_links)
        except:
            print("Not able to retrieve sitemap.xml")

        return ", ".join(content)

    @staticmethod
    def gather_links(page_url):
        html_string = ''

        print(page_url)

        try:
            response = urlopen(page_url)
            if 'text/html' in response.getheader('Content-Type'):
                html_bytes = response.read()

                # Commented because of the before mentioned problem without
                # Selenium
                # html_string = html_bytes.decode("utf-8")

                # Get HTML using 
                html_string = Crawler.download_and_render_page(page_url)
            finder = LinkFinder(extract_domain(page_url), page_url)
            finder.feed(html_string)
        except Exception as e:
            print(str(e))
            return [], '' , None

        return finder.page_links(), html_string, html_bytes

    @staticmethod
    def url_is_in_database(url):
        # if the search returns -1 it means we haven't found the url
        # otherwise we have foudn it
        return find_page(url) != -1

    @staticmethod
    def add_links_to_queue(links):
        for url in links:
            # Check if the link is not already present in the database
            if url in Crawler.queue or Crawler.url_is_in_database(url):
                continue
            
            # Check if the link resides in an allowed domain
            isDomainAllowed = False
            for allowed_domain in Crawler.ALLOWED_DOMAINS:
                if re.search(allowed_domain, extract_domain(url)):
                    isDomainAllowed = True
            if not isDomainAllowed:
                continue

            Crawler.queue.add(url)
    
    @staticmethod
    def update_files():
        set_to_file(Crawler.queue, Crawler.QUEUE_FILE)
