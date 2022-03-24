# Calling the crawler

# Internal
from domain import *
from project_properties import *
from thread import CrawlerThread

# Create an appropriate number of worker instances
crawlerThreads = []
for i in range(NUMBER_OF_WORKERS):
    current_thread = CrawlerThread(i)
    crawlerThreads.append(current_thread)
    print("Created worker " + str(i))

# Start the threads, start crawling
for crawlerThread in crawlerThreads:
    crawlerThread.start()