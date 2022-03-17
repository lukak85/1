import psycopg2

# ---------------
# SITE MANAGEMENT
# ---------------

def insert_site(domain, robots_content, sitemap_content):
    conn = psycopg2.connect(host="localhost", user="user", password="SecretPassword")
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



def find_site(domain):
    conn = psycopg2.connect(host="localhost", user="user", password="SecretPassword")
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



# ----------------
# IMAGE MANAGEMENT
# ----------------

def insert_image(page_id, filename, content_type, data, accessed_time):
    conn = psycopg2.connect(host="localhost", user="user", password="SecretPassword")
    conn.autocommit = True
    
    cur = conn.cursor()
    cur.execute("INSERT INTO crawldb.image (page_id, filename, content_type, data, accessed_time) VALUES (FOREIGN KEY REFERENCES crawldb.page"
                + str(page_id) + "),'"
                + filename + "','"
                + content_type + "','"
                + data + "',"
                + str(accessed_time) + ");")
    
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
    cur.execute(
        "INSERT INTO crawldb.page (site_id, page_type_code, url, html_content, http_status_code, accessed_time) VALUES ((SELECT id FROM crawldb.site WHERE id=%s),(SELECT code FROM crawldb.page_type WHERE code=%s),%s,%s,%s,%s) RETURNING id;",
        (site_id, page_type_code, url, html_content, http_status_code, accessed_time)
    )

    page_id = -1
    result = cur.fetchall()
    if result:
        page_id = result[0][0]
    
    cur.close()
    conn.close()
    return page_id



def find_page(url):
    conn = psycopg2.connect(host="localhost", user="user", password="SecretPassword")
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
    try:
        cur.execute("INSERT INTO crawldb.link (from_page, to_page) VALUES ((SELECT id FROM crawldb.page WHERE id=%s), (SELECT id FROM crawldb.page WHERE id=%s));", (from_page, to_page))
    except:
        print("insert_link: one of the pages does not exist in the database")
    
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
