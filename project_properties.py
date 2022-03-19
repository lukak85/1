PROJECT_NAME = 'fri_wier_kj_lk_tm'
HASH_SEED = PROJECT_NAME

ALLOWED_DOMAINS_REGEX = set() # We give the set of regexes of allowed domains
ALLOWED_DOMAINS_REGEX.add(".*.gov.si") # This means all the domains with a suffix ".gov.si" are allowed

WEB_DRIVER_LOCATION = "webdriver/chromedriver.exe"
TIMEOUT = 5

NUMBER_OF_WORKERS = 4

DEBUG_MODE = True # Use this to print out more than usual to debug
PROD_MODE = False # Use this to save queue to file

# Crawler database properties
DB_HOST = "localhost"
DB_USER = "user"
DB_PASSWORD = "SecretPassword"