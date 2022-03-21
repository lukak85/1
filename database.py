# External
import psycopg2

# Internal
from project_properties import *

class CrawlerDatabase:

    def __init__(self, HOST, USER, PASSWORD):
        self.host = HOST
        self.user = USER
        self.password = PASSWORD

    # ---------------
    # SITE MANAGEMENT
    # ---------------
    
    def insert_site(self, domain, robots_content, sitemap_content):
        conn = psycopg2.connect(host=self.host, user=self.user, password=self.password)
        conn.autocommit = True
        
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO crawldb.site (domain, robots_content, sitemap_content) VALUES (%s,%s,%s) RETURNING id;",
            (domain, robots_content, sitemap_content)
            )
        
        site_id = -1
        result = cur.fetchall()
        if result:
            site_id = result[0][0]
        
        cur.close()
        conn.close()
        return site_id


    
    def find_site(self, domain):
        conn = psycopg2.connect(host=self.host, user=self.user, password=self.password)
        conn.autocommit = True
        
        cur = conn.cursor()
        cur.execute("SELECT * FROM crawldb.site WHERE domain='" + domain + "';")
        
        # Check if array is empty, meaning we didn't find the site already present in the table
        site_id = -1
        result = cur.fetchall()
        if result:
            site_id = result[0][0]

        cur.close()
        conn.close()
        
        return site_id

    
    def find_site_robots(self, domain):
        conn = psycopg2.connect(host=self.host, user=self.user, password=self.password)
        conn.autocommit = True
        
        cur = conn.cursor()
        cur.execute("SELECT robots_content FROM crawldb.site WHERE domain='" + domain + "';")
        
        # Check if array is empty, meaning we didn't find the site already present in the table
        robots = None
        result = cur.fetchall()
        if result:
            robots = result[0][0]

        cur.close()
        conn.close()
        
        return robots



    # ----------------
    # IMAGE MANAGEMENT
    # ----------------

    def insert_image(self, page_id, filename, content_type, data, accessed_time):
        conn = psycopg2.connect(host=self.host, user=self.user, password=self.password)
        conn.autocommit = True
        
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO crawldb.image (page_id, filename, content_type, data, accessed_time) VALUES ((SELECT id FROM crawldb.page WHERE id=%s),%s,%s,%s,%s)",
            (page_id, filename, content_type, data, accessed_time)
        )
        
        id = cur.fetchone()[0]
        
        cur.close()
        conn.close()
        return id


    
    def find_image(self, page_id, filename):
        conn = psycopg2.connect(host=self.host, user=self.user, password=self.password)
        conn.autocommit = True
        
        cur = conn.cursor()
        cur.execute("SELECT * FROM crawldb.image WHERE page_id = '" + str(page_id) + "' AND filename='" + filename + "';")
        
        image_id = -1
        
        # Check if array is empty, meaning the site isn't already present in the table
        if cur.fetchall():
            image_id = cur.fetchone()[0]
        
        cur.close()
        conn.close()
        
        return image_id



    # ---------------
    # PAGE MANAGEMENT
    # ---------------

    def insert_page(self, site_id, page_type_code, url, html_content, http_status_code, accessed_time):
        conn = psycopg2.connect(host=self.host, user=self.user, password=self.password)
        conn.autocommit = True
        
        cur = conn.cursor()
        page_id = -1
        try:
            cur.execute(
                "INSERT INTO crawldb.page (site_id, page_type_code, url, html_content, http_status_code, accessed_time) VALUES ((SELECT id FROM crawldb.site WHERE id=%s),(SELECT code FROM crawldb.page_type WHERE code=%s),%s,%s,%s,%s) RETURNING id;",
                (site_id, page_type_code, url, html_content, http_status_code, accessed_time)
            )

            page_id = -1
            result = cur.fetchall()
            if result:
                page_id = result[0][0]
        except:
            print("Page already exists")
        
        cur.close()
        conn.close()
        return page_id


    def find_page(self, url):
        conn = psycopg2.connect(host=self.host, user=self.user, password=self.password)
        conn.autocommit = True
        
        cur = conn.cursor()
        cur.execute("SELECT * FROM crawldb.page WHERE url='" + url + "';")
        
        # Check if array is empty, meaning the site isn't already present in the table
        page_id = -1
        result = cur.fetchall()
        if result:
            page_id = result[0][0]
        
        cur.close()
        conn.close()
        
        return page_id



    # --------------------
    # PAGE DATA MANAGEMENT
    # --------------------
    
    def insert_page_data(self, page_id, data_type_code, data):
        conn = psycopg2.connect(host=self.host, user=self.user, password=self.password)
        conn.autocommit = True
        
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO crawldb.page_data (page_id, data_type_code, data) VALUES ((SELECT id FROM crawldb.page WHERE id=%s),%s,%s)",
            (page_id, data_type_code, data)
        )
        
        cur.close()
        conn.close()
        return True



    # ---------------
    # LINK MANAGEMENT
    # ---------------
    
    def insert_link(self, from_page, to_page):
        conn = psycopg2.connect(host=self.host, user=self.user, password=self.password)
        conn.autocommit = True
        
        cur = conn.cursor()
        try:
            cur.execute("INSERT INTO crawldb.link (from_page, to_page) VALUES ((SELECT id FROM crawldb.page WHERE id=%s), (SELECT id FROM crawldb.page WHERE id=%s));", (from_page, to_page))
        except:
            """
            if DEBUG_MODE:
                print("insert_link: one of the pages does not exist in the database")
            """
        
        cur.close()
        conn.close()
        return



    # ---------------
    # HASH MANAGEMENT
    # ---------------
    
    def insert_hash(self, page_id, hash):
        conn = psycopg2.connect(host=self.host, user=self.user, password=self.password)
        conn.autocommit = True
        
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO crawldb.hash (page_id, hash) VALUES ((SELECT id FROM crawldb.page WHERE id=%s),%s);",
            (page_id, hash)
        )
        
        cur.close()
        conn.close()
        return


    
    def find_hash(self, page_id):
        conn = psycopg2.connect(host=self.host, user=self.user, password=self.password)
        conn.autocommit = True
        
        cur = conn.cursor()
        cur.execute("SELECT hash FROM crawldb.hash WHERE page_id=" + str(page_id) + ";")
        
        # Check if array is empty, meaning the site isn't already present in the table
        hash = -1
        result = cur.fetchall()
        if result:
            hash = result[0][0]
        
        cur.close()
        conn.close()
        
        return hash



    # -------------------
    # FRONTIER MANAGEMENT
    # -------------------
    
    def insert_frontier(self, url):
        conn = psycopg2.connect(host=self.host, user=self.user, password=self.password)
        conn.autocommit = True
        
        cur = conn.cursor()
        try:
            cur.execute(
                "INSERT INTO crawldb.frontier (url) VALUES (%s);",
                (url,)
            )
        except:
            print("The url '" + url + "' already exist in the frontier")
        
        cur.close()
        conn.close()
        return

    
    def get_first_frontier(self):
        conn = psycopg2.connect(host=self.host, user=self.user, password=self.password)
        conn.autocommit = True
        
        cur = conn.cursor()
        url = ""
        try:
            cur.execute(
                "SELECT * FROM crawldb.frontier LIMIT 1;",
                (url,)
            )

            result = cur.fetchall()
            if result:
                url = result[0][0]
        except:
            print("No more urls in frontier")
        
        cur.close()
        conn.close()
        return url

    
    def delete_from_frontier(self, url):
        conn = psycopg2.connect(host=self.host, user=self.user, password=self.password)
        conn.autocommit = True
        
        cur = conn.cursor()
        try:
            cur.execute(
                "DELETE FROM crawldb.frontier WHERE url=%s;",
                (url,)
            )
        except:
            print("No such entry")
        
        cur.close()
        conn.close()
        return

    # -------------
    # IP MANAGEMENT
    # -------------

    def insert_ip(self, ip, domain, accessedTime):
        conn = psycopg2.connect(host=self.host, user=self.user, password=self.password)
        conn.autocommit = True
        
        isNotAlreadyPresent = False
        cur = conn.cursor()
        try:
            cur.execute(
                "INSERT INTO crawldb.ips (ip, domain_name, accessed_time_sec) VALUES (%s,%s,%s);",
                (ip, domain, accessedTime)
            )
            if DEBUG_MODE:
                print("New IP and domain combination inserted")
        except:
            if DEBUG_MODE:
                print("The IP and domain combination already exist")
        
        cur.close()
        conn.close()
        return True

    def get_time_accessed(self, ip, domain):
        conn = psycopg2.connect(host=self.host, user=self.user, password=self.password)
        conn.autocommit = True
        
        cur = conn.cursor()
        accessedTime = []
        try:
            cur.execute(
                "SELECT accessed_time_sec FROM crawldb.ips WHERE ip=%s OR domain_name=%s;",
                (ip,domain)
            )

            result = cur.fetchall()
            if result:
                accessedTime = list(result[0])
                if DEBUG_MODE:
                    print(accessedTime)
        except:
            if DEBUG_MODE:
                print("No such IP and domain combination  in the database")
        
        cur.close()
        conn.close()
        return accessedTime

    def get_time_accessed_exact(self, ip, domain):
        conn = psycopg2.connect(host=self.host, user=self.user, password=self.password)
        conn.autocommit = True
        
        cur = conn.cursor()
        accessedTime = []
        try:
            cur.execute(
                "SELECT accessed_time_sec FROM crawldb.ips WHERE ip=%s AND domain_name=%s;",
                (ip,domain)
            )

            result = cur.fetchall()
            if result:
                accessedTime = list(result[0])
                if DEBUG_MODE:
                    print(accessedTime)
        except:
            if DEBUG_MODE:
                print("No such IP and domain combination  in the database")
        
        cur.close()
        conn.close()
        return accessedTime

    def alter_time_accessed(self, ip, domain, accessedTime):
        conn = psycopg2.connect(host=self.host, user=self.user, password=self.password)
        conn.autocommit = True
        
        cur = conn.cursor()
        try:
            cur.execute(
                "UPDATE crawldb.ips SET accessed_time_sec=%s WHERE ip=%s AND domain_name=%s;",
                (accessedTime, ip, domain)
            )
        except:
            if DEBUG_MODE:
                print("Could not update time accessed for the and domain combination")
        
        cur.close()
        conn.close()
        return