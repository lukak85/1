# Calling the crawler

# Internal
from domain import *
from project_properties import *
from thread import CrawlerThread
from database import CrawlerDatabase

# Create the database
crawlerDB = CrawlerDatabase(DB_HOST, DB_USER, DB_PASSWORD)

# Create an appropriate number of worker instances
crawlerThreads = []
for i in range(NUMBER_OF_WORKERS):
    current_thread = CrawlerThread(i, crawlerDB)
    crawlerThreads.append(current_thread)
    print("Created worker " + str(i))

# Start the threads, start crawling
for crawlerThread in crawlerThreads:
    crawlerThread.start()