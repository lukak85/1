from http.client import ImproperConnectionState
from urllib.request import urlopen

from mm import *
from domain import *
from database import *
from link_finder import LinkFinder

import time
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

        Crawler.DRIVER = webdriver.Chrome(Crawler.WEB_DRIVER_LOCATION, options=Crawler.CHROME_OPTIONS)

        Crawler.boot()
        Crawler.crawl_page(list(Crawler.queue)[0])

    @staticmethod
    def boot():
        Crawler.queue = file_to_set(Crawler.QUEUE_FILE)

    @staticmethod
    def crawl_page(page_url):
        if Crawler.url_is_in_database(page_url):
            print('Now crawling '+ page_url)
            print('Queue: '+ str(len(Crawler.queue)))

            Crawler.add_links_to_queue(Crawler.gather_links(page_url))
            Crawler.queue.remove(page_url)

            # Insert page into the database
            insert_page(page_url)

            Crawler.update_files()

    # Downloader using selenium, in case the response doesn't render properly otherwise
    @staticmethod
    def download_and_render_page(page_url):
        Crawler.DRIVER.get(page_url)

        time.sleep(Crawler.TIMEOUT)
        html = Crawler.DRIVER.page_source
        Crawler.DRIVER.close()
        
        return html

    @staticmethod
    def gather_links(page_url):
        html_string = ''

        try:
            response = urlopen(page_url)
            if 'text/html' in response.getheader('Content-Type'):
                html_bytes = response.read()

                # Commented because of the before mentioned problem without
                # Selenium
                # html_string = html_bytes.decode("utf-8")

                # Get HTML using 
                html_string = Crawler.download_and_render_page(page_url)
            finder = LinkFinder(Crawler.base_url, page_url)
            finder.feed(html_string)
        except Exception as e:
            print(str(e))
            return set()

        return finder.page_links()

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
                if re.search(allowed_domain, get_domain_name(url)):
                    isDomainAllowed = True
            if not isDomainAllowed:
                continue

            Crawler.queue.add(url)
    
    @staticmethod
    def update_files():
        set_to_file(Crawler.queue, Crawler.QUEUE_FILE)
