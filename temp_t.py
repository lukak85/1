#!/usr/bin/env python3

# URL canonization
import urllib
from urllib.parse import urlparse
import re
import urltools
from urllib.parse import quote


# NOT DONE YET!

# testing urls
url1 = "http://www.cs.indiana.edu" # add trailing slash -> http://cs.indiana.edu/
url2 = "http://cs.indiana.edu:80/" # remove default port number -> http://cs.indiana.edu/
url3 = "http://cs.indiana.edu/People" # add trailing slash -> http://cs.indiana.edu/People/
url4 = "http://cs.indiana.edu/path#anchor" # remove anchor / fragment -> http://cs.indiana.edu/path/
url5 = "http://cs.indiana.edu:80/hello/index.html"
url6 = "http://cs.indiana.edu:80/test/./../end" # remove unnecessary path parts -> http://cs.indiana.edu/end/
url7 = "/relative/path" # relative to absolute path - mors poznat absolute? domain?
url8 = "http://cs.indiana.edu/file.pdf" # remove -> http://cs.indiana.edu/
url9 = "http://cs.indiana.edu:80/My File.html" # encode disallowed characters -> http://cs.indiana.edu:80/My%20File.html
url10 = "http://CS.INDIANA.EDU/path" # upper case to lower case -> http://cs.indiana.edu/path/
url11 = "http://cs.indiana.edu:80/%7Efil/"

def urlCanonization(url, parent_scheme, parent_netloc):
    print(url)

    # decoding needlessly encoded characters
    url = urllib.parse.unquote(url)

    parsed_url = urlparse(url)
    print(parsed_url)

    scheme = parsed_url.scheme
    # relative to absolute
    if (scheme == ""):
        scheme = parent_scheme
    scheme = scheme + ("://")

    netloc = parsed_url.netloc
    # relative to absolute
    if (netloc == ""):
        netloc = parent_netloc
    netloc = netloc.lower()
    # removing default port number
    netloc = parsed_url.hostname
    # removing www - if not removed beforehand
    if (netloc[0] == "w" and netloc[1] == "w" and netloc[2] == "w"):
        netloc = netloc[4:]

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


    query = parsed_url.query
    fragment = parsed_url.fragment


    canon_url = scheme + netloc + path
    print(canon_url)
    return canon_url


urlCanonization(url11, "", "")