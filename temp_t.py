#!/usr/bin/env python3

# URL canonization
import urllib
from urllib.parse import urlparse
import re
import urltools
from urllib.parse import quote
from url_normalize import url_normalize

# DOESN'T WORK FOR RELATIVE URLs (yet)

# testing urls
url1 = "http://www.cs.indiana.edu" # add trailing slash -> http://cs.indiana.edu/
url2 = "http://cs.indiana.edu:80/" # remove default port number -> http://cs.indiana.edu/
url3 = "http://cs.indiana.edu/People" # add trailing slash -> http://cs.indiana.edu/People/
url4 = "http://cs.indiana.edu/path#anchor" # remove anchor / fragment -> http://cs.indiana.edu/path/
url5 = "http://cs.indiana.edu:80/hello/index.html"
url6 = "http://cs.indiana.edu:80/test/./../end" # remove unnecessary path parts -> http://cs.indiana.edu/end/
url7 = "/relative/path" # relative to absolute path - mors poznat parent scheme pa domain
url8 = "http://cs.indiana.edu/file.pdf" #
url9 = "http://cs.indiana.edu:80/My File.html" # encode disallowed characters -> http://cs.indiana.edu:80/My%20File.html
url10 = "http://CS.INDIANA.EDU/path" # upper case to lower case -> http://cs.indiana.edu/path/
url11 = "http://cs.indiana.edu:80/%7Efil/"

def urlCanon(url, parent_scheme, parent_netloc):
    """
        If path is relative (empty scheme and netloc attributes after parsing),
        parent_scheme and parent_netloc should be used.
        :param url: URL to canonicalize
        :param parent_scheme: Parent page's scheme [i.e. http, https]
        :param parent_netloc: Parent page's host (domain name) [i.e. www.cs.indiana.edu]
        :return: Canonicalized URL
    """

    # print(url)

    # decoding needlessly encoded characters
    url = urllib.parse.unquote(url)

    parsed_url = urlparse(url)
    # print(parsed_url)

    scheme = parsed_url.scheme
    scheme = str(scheme)
    # relative to absolute
    if not scheme:
        scheme = parent_scheme
    if scheme is None:
        scheme = parent_scheme
    scheme = scheme + ("://")

    netloc = parsed_url.netloc
    # relative to absolute
    netloc = str(netloc)
    if netloc is None:
        netloc = parent_netloc
    if not netloc:
        netloc = parent_netloc

    netloc = netloc.lower()
    # removing www. if not beforehand
    netloc = re.sub("www./", "/", netloc)
    # removing default port number
    netloc = parsed_url.hostname

    add = 1
    path = parsed_url.path
    # add trailing slash to root directory if no path
    if (path == "" or path == "/"):
        path = ""
        netloc = netloc + "/"
    # resolving path
    # removing default filename
    path = re.sub("/index\.(html|htm|php)", "/", path)
    # encoding
    path = urllib.parse.quote(path)

    # add / if the link has no .pdf, ....
    if (path[len(path)-4] == "." or path[len(path)-5] == "."):
        add = 0
    if (add):
        path = path + "/"


    query = parsed_url.query
    fragment = parsed_url.fragment
    canon_url = scheme + netloc + path
    canon_url = url_normalize(canon_url)

    print(canon_url)
    return canon_url


urlCanon(url9, "http", "www.some.domain")