# External
import threading

# Internal
from project_properties import *
from crawler import Crawler
from database import *

lock = threading.Lock()

class CrawlerThread(threading.Thread):
    def __init__(self, thread):
        threading.Thread.__init__(self)
        self.thread = thread
        self.crawler = Crawler(PROJECT_NAME, TIMEOUT, WEB_DRIVER_LOCATION, ALLOWED_DOMAINS_REGEX, thread)

    def run(self):
        while True:
            with lock:
                currentUrl = get_first_frontier()
                delete_from_frontier(currentUrl)

            if currentUrl != None:
                try:
                    self.crawler.crawl_page(currentUrl)
                except:
                    print("An error occurred crawling the page, pushed to the back of frontier")
                    insert_frontier(currentUrl)
            
            else:
                self.close_thread()
                return
            
    def close_thread(self):
        self.crawler.close_crawler()