# Calling the crawler

import threading
from queue import Queue
from crawler import Crawler
from domain import *
from mm import *

PROJECT_NAME = 'fri_wier_kj_lk_tm'
TIMEOUT = 5
STARTING_PAGES = [
    "http://gov.si",
    "http://evem.gov.si",
    "http://e-uprava.gov.si",
    "http://e-prostor.gov.si"
]
ALLOWED_DOMAINS_REGEX = set(
    "*.gov.si"
)
QUEUE_FILE = PROJECT_NAME + "/frontier.txt"
WEB_DRIVER_LOCATION = "C:/ManualInstalls/ChromeDriver/chromedriver.exe"
NUMBER_OF_THREADS = 4

queue = Queue()

# Create worker threads
def create_workers():
    for _ in range(NUMBER_OF_THREADS):
        t = threading.Thread(target=crawl)
        t.daemon = True
        t.start()

# Next job in the queue
def work():
    while True:
        url = queue.get()
        Crawler.crawl_page(url)
        queue.task_done()

# Each link in queue is a new job
def create_jobs():
    for link in file_to_set(QUEUE_FILE):
        queue.put(link)
    queue.join()
    crawl()

# Check for items in the queue to crawl them
def crawl():
    # First check if the queue is empty, if it is, put in the
    # starting sites, defined by STARTING_PAGES
    # queued_links = file_to_set(QUEUE_FILE)
    if len(Crawler.queue) > 0:
        print(str(len(Crawler.queue))+ " links in the queue")
        create_jobs()

# Create this before starting the crawlers, so that it's only created once
create_project_dir(PROJECT_NAME)
create_queue_file(PROJECT_NAME, STARTING_PAGES)

# Create a crawler instance
crawler = Crawler(PROJECT_NAME, TIMEOUT, WEB_DRIVER_LOCATION, STARTING_PAGES, ALLOWED_DOMAINS_REGEX)

# Create the workers, then crawl
create_workers()
crawl()