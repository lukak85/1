# External
import threading

# Internal
from project_properties import *
from crawler import Crawler

lock = threading.Lock()

class CrawlerThread(threading.Thread):
    def __init__(self, thread, crawlerDB):
        threading.Thread.__init__(self)
        self.thread = thread
        self.crawlerDB = crawlerDB
        self.crawler = Crawler(PROJECT_NAME, TIMEOUT, WEB_DRIVER_LOCATION, ALLOWED_DOMAINS_REGEX, crawlerDB, thread)

    def run(self):
        # TODO - fix this so that it closes properly when
        # no more links are present
        while True:
            with lock:
                currentUrl = self.crawlerDB.get_first_frontier()
                self.crawlerDB.delete_from_frontier(currentUrl)

            if currentUrl != None:
                self.crawler.crawl_page(currentUrl)
            
            else:
                self.close_thread()
                return
            
    def close_thread(self):
        self.crawler.close_crawler()