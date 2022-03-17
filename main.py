# Calling the crawler

import concurrent.futures
import threading

from domain import *
from mm import *
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

# Create a crawler instance
Crawler(PROJECT_NAME, TIMEOUT, WEB_DRIVER_LOCATION, STARTING_PAGES, ALLOWED_DOMAINS_REGEX)

lock = threading.Lock()

# Crawling
with concurrent.futures.ThreadPoolExecutor() as executor:
    print(f"\n ... executing workers ...\n")
    for _ in range(NUMBER_OF_WORKERS):
        executor.submit(Crawler.boot())

print(Crawler.queue)