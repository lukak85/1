import psycopg2

# ---------------
# SITE MANAGEMENT
# ---------------

def insert_site(domain, robots_content, sitemap_content):
    conn = psycopg2.connect(host="localhost", user="user", password="SecretPassword")
    conn.autocommit = True
    
    cur = conn.cursor()
    cur.execute("INSERT INTO crawldb.site (domain, robots_content, sitemap_content) VALUES ('"
                + domain + "','"
                + robots_content + "','"
                + sitemap_content + "' RETURNING id);")
    
    id = cur.fetchone()[0]
    
    cur.close()
    conn.close()
    return id



def find_site(domain):
    conn = psycopg2.connect(host="localhost", user="user", password="SecretPassword")
    conn.autocommit = True
    
    cur = conn.cursor()
    cur.execute("SELECT * FROM crawldb.site WHERE domain='" + domain + "';")
    
    site_id = -1
    
    # Check if array is empty, meaning we didn't find the site already present in the table
    if cur.fetchall():
        site_id = cur.fetchone()[0]
    
    cur.close()
    conn.close()
    
    return site_id



# ----------------
# IMAGE MANAGEMENT
# ----------------

def insert_image(page_id, filename, content_type, data, accessed_time):
    conn = psycopg2.connect(host="localhost", user="user", password="SecretPassword")
    conn.autocommit = True
    
    cur = conn.cursor()
    cur.execute("INSERT INTO crawldb.image (page_id, filename, content_type, data, accessed_time) VALUES (FOREIGN KEY REFERENCES crawldb.page"
                + page_id + "),'"
                + filename + "','"
                + content_type + "','"
                + data + "','"
                + accessed_time + "');")
    
    id = cur.fetchone()[0]
    
    cur.close()
    conn.close()
    return id



def find_image(page_id, filename):
    conn = psycopg2.connect(host="localhost", user="user", password="SecretPassword")
    conn.autocommit = True
    
    cur = conn.cursor()
    cur.execute("SELECT * FROM crawldb.image WHERE page_id = '" + page_id + "' AND filename='" + filename + "';")
    
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

def insert_page(site_id, page_type_code, url, html_content, http_status_code, accessed_time):
    conn = psycopg2.connect(host="localhost", user="user", password="SecretPassword")
    conn.autocommit = True
    
    cur = conn.cursor()
    cur.execute("INSERT INTO crawldb.page (site_id, page_type_code, url, html_content, http_status_code, accessed_time) VALUES (FOREIGN KEY REFERENCES crawldb.site"
                + site_id + "),"
                + page_type_code + ",'"
                + html_content + "',"
                + http_status_code + ","
                + accessed_time + ");")
    
    cur.close()
    conn.close()
    return True



def find_page(url):
    conn = psycopg2.connect(host="localhost", user="user", password="SecretPassword")
    conn.autocommit = True
    
    cur = conn.cursor()
    cur.execute("SELECT * FROM crawldb.page WHERE url='" + url + "';")
    
    page_id = -1
    
    # Check if array is empty, meaning the site isn't already present in the table
    if cur.fetchall():
        page_id = cur.fetchone()[0]
    
    cur.close()
    conn.close()
    
    return page_id



# --------------------
# PAGE DATA MANAGEMENT
# --------------------

def insert_page_data(page_id, data_type_code, data):
    conn = psycopg2.connect(host="localhost", user="user", password="SecretPassword")
    conn.autocommit = True
    
    cur = conn.cursor()
    cur.execute("INSERT INTO crawldb.page_data (page_id, data_type_code, data) VALUES (FOREIGN KEY REFERENCES crawldb.page("
                + page_id + "),"
                + data_type_code + ",'"
                + data + "');")
    
    cur.close()
    conn.close()
    return True



# --------------------
# DATA TYPE MANAGEMENT
# --------------------

def insert_data_type(code):
    conn = psycopg2.connect(host="localhost", user="user", password="SecretPassword")
    conn.autocommit = True
    
    cur = conn.cursor()
    cur.execute("INSERT INTO crawldb.page (code) VALUES (" + code + ");")
    
    cur.close()
    conn.close()
    return



# ---------------
# LINK MANAGEMENT
# ---------------

def insert_link(from_page, to_page):
    conn = psycopg2.connect(host="localhost", user="user", password="SecretPassword")
    conn.autocommit = True
    
    cur = conn.cursor()
    cur.execute("INSERT INTO crawldb.link (page_id, data_type_code, data) VALUES (FOREIGN KEY REFERENCES crawldb.page("
                + from_page + "),FOREIGN KEY REFERENCES crawldb.page("
                + to_page + "));")
    
    cur.close()
    conn.close()
    return



# --------------------
# PAGE TYPE MANAGEMENT
# --------------------

def insert_page_type(code):
    conn = psycopg2.connect(host="localhost", user="user", password="SecretPassword")
    conn.autocommit = True
    
    cur = conn.cursor()
    cur.execute("INSERT INTO crawldb.page_type (code) VALUES (" + code + ");")
    
    cur.close()
    conn.close()
    return
