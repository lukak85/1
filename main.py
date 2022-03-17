# Calling the crawler

import concurrent.futures
import threading

from domain import *
from mm import *
from queue_manager import Queue
from crawler import Crawler

PROJECT_NAME = 'fri_wier_kj_lk_tm'
TIMEOUT = 5
STARTING_PAGES = [
    "http://gov.si",
    "http://evem.gov.si",
    "http://e-uprava.gov.si",
    "http://e-prostor.gov.si"
]
ALLOWED_DOMAINS_REGEX = set() # We give the set of regexes of allowed domains
ALLOWED_DOMAINS_REGEX.add(".*.gov.si") # This means all the domains with a suffix ".gov.si" are allowed
QUEUE_FILE = PROJECT_NAME + "/frontier.txt"
WEB_DRIVER_LOCATION = "C:/ManualInstalls/ChromeDriver/chromedriver.exe"
NUMBER_OF_WORKERS = 4

# Create this before starting the crawlers, so that it's only created once
create_project_dir(PROJECT_NAME)
create_queue_file(PROJECT_NAME, STARTING_PAGES)

# Setup queue
QUEUE_FILE = PROJECT_NAME + '/frontier.txt'
queueInstance = Queue(file_to_set(QUEUE_FILE))

# Create an appropriate number of worker instances (so we don't use the same driver for the different workers),
# we could also use a different approach but using different instances is cleaner
workers = []
for i in range(NUMBER_OF_WORKERS):
    workers.append(Crawler(PROJECT_NAME, TIMEOUT, WEB_DRIVER_LOCATION, STARTING_PAGES, ALLOWED_DOMAINS_REGEX, queueInstance))

lock = threading.Lock()

# Crawling
with concurrent.futures.ThreadPoolExecutor() as executor:
    print(f"\n ... executing workers ...\n")
    for i in range(NUMBER_OF_WORKERS):
        executor.submit(workers[i].boot())