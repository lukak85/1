from asyncore import loop
import os
import copy
import traceback

from bs4 import BeautifulSoup, Tag, NavigableString, Comment, Doctype

DEBUG_MODE = False



"""
Create wrapper with recurvsive tag and string matching check
"""

def create_wrapper(site_wrapper, pages):

    # Go trough all pages, iterativelly building a wrapper
    for page in pages:
        site_wrapper, _ = recursive_matching(site_wrapper, page)

    return site_wrapper


def recursive_matching(node1i, node2i):

    # Defines if all the tags in the current node match
    tags_match = True

    # Start with the first child node
    i = 0

    # Creating a copy of node, decoupling it from parent
    node1 = [copy.copy(el) for el in node1i.children if not (isinstance(el, NavigableString) and el.string.isspace())]
    node2 = [copy.copy(el) for el in node2i.children if not (isinstance(el, NavigableString) and el.string.isspace())]

    if len(node1) == 0 and len(node2) == 0:
        return node1i, tags_match

    # Loop trough them, adding new ones
    while i < len(node1) or i < len(node2):

        # If we came to the end with first page, but not with the second,
        # add tags from the second page as optionals
        if i >= len(node1) and i < len(node2):

            tags_match = False

            # We just add the remaining items, and anotate them as optionals
            for j in range(i, len(node2)):
                node1.insert(j, node2[j])

                if isinstance(node1[j], Tag):
                    node1[j]['roadrunner_optional'] = '?'

        # If we came to the end with second page, but not with the first,
        # set tags from the first page as optionals
        elif i >= len(node2) and i < len(node1):

            tags_match = False

            for j in range(i, len(node1)):
                if isinstance(node1[j], Tag):
                    node1[j]['roadrunner_optional'] = '?'

        # There is no tag mismatch, check for mismatches recursivelly
        elif isinstance(node1[i], Tag) and isinstance(node2[i], Tag) and node1[i].name == node2[i].name and tags_class_id_match(node1[i], node2[i]):

            # If current tag is of type ul, ol or td, do iterator tag mismatching
            if node1[i].name == "ol" or node1[i].name == "ul" or node1[i].name == "thead" or node1[i].name == "tbody" or node1[i].name == "tfoot":

                # List element is in either ordered or unordered list
                el = "li"

                # List element is in table
                if node1[i].name == "thead" or node1[i].name == "tbody" or node1[i].name == "tfoot":
                    el = "tr"
                
                node1[i] = iterator_matching(node1[i], node2[i], el)

            # Else do regular tag mismatching
            else:
                node1[i], tagm = recursive_matching(node1[i], node2[i])
                tags_match = tagm and tags_match

        # String mismatch
        elif isinstance(node1[i], NavigableString) and isinstance(node2[i], NavigableString) and node1[i].string != node2[i].string:
            node1[i] = "#PCDATA"

        # If the strings are the same, don't change them        
        elif isinstance(node1[i], NavigableString) and isinstance(node2[i], NavigableString) and node1[i].string == node2[i].string:
            pass

        # Other type of mismatch, we use cross search checking
        else:
            foundMatch = False
            tags_match = False

            # Do cross search
            for j in range(i, max(len(node1), len(node2))):

                # Matching tags appear on the current index
                if j < len(node1) and j < len(node2) and isinstance(node1[j], Tag) and isinstance(node2[j], Tag) and node1[j].name == node2[j].name and tags_class_id_match(node1[j], node2[j]):
                    l = j - i

                    for k in range(i, j):
                        if isinstance(node2[k], Tag):
                            node2[k]['roadrunner_optional'] = '?'
                        node1.insert(k, node2[k])

                    for k in range(j, j + l):
                        if isinstance(node1[k], Tag):
                            node1[k]['roadrunner_optional'] = '?'
                        node2.insert(k, node1[k])

                    foundMatch = True
                    i = j + l

                    break
                
                # Current tag on second page has appeared before
                elif j < len(node2) and isinstance(node2[j], Tag) and node2[j].name in [el.name for el in node1[i:min(j, len(node1))] if isinstance(el, Tag)] and any([tags_class_id_match(el, node2[j]) for el in node1[i:min(j, len(node1))] if isinstance(el, Tag)]):
                    foundIndex = i
                    
                    while not isinstance(node1[foundIndex], Tag) or node2[j].name != node1[foundIndex].name and not tags_class_id_match(node1[j], node2[foundIndex]):
                        foundIndex += 1

                    for k in range(i, foundIndex):
                        if isinstance(node1[k], Tag):
                            node1[k]['roadrunner_optional'] = '?'
                        node2.insert(k, node1[k])

                    for k in range(foundIndex, foundIndex + (j - i)):
                        if isinstance(node2[k], Tag):
                            node2[k]['roadrunner_optional'] = '?'
                        node1.insert(k, node2[k])

                    foundMatch = True
                    i = foundIndex + (j - i)
                    
                    break

                # Current tag on first page has appeared before
                elif j < len(node1) and isinstance(node1[j], Tag) and node1[j].name in [el.name for el in node2[i:min(j, len(node2))] if isinstance(el, Tag)] and any([tags_class_id_match(el, node1[j]) for el in node2[i:min(j, len(node2))] if isinstance(el, Tag)]):
                    foundIndex = i
                    
                    while not isinstance(node2[foundIndex], Tag) or node1[j].name != node2[foundIndex].name and not tags_class_id_match(node1[j], node2[foundIndex]):
                        foundIndex += 1

                    for k in range(i, foundIndex):
                        if isinstance(node2[k], Tag):
                            node2[k]['roadrunner_optional'] = '?'
                        node1.insert(k, node2[k])

                    for k in range(foundIndex, foundIndex + (j - i)):
                        if isinstance(node1[k], Tag):
                            node1[k]['roadrunner_optional'] = '?'
                        node2.insert(k, node1[k])

                    foundMatch = True
                    i = foundIndex + (j - i)
                    
                    break

            # If there were no matches in cross search, add all the remaining nodes
            if not foundMatch:
                ln1 = len(node1)

                for k in range(i, ln1):
                    if isinstance(node1[k], Tag):
                        node1[k]['roadrunner_optional'] = '?'
                        node2.insert(k, node1[k])

                ln2 = len(node2)

                for k in range(ln1, ln2):
                    if isinstance(node2[k], Tag):
                        node2[k]['roadrunner_optional'] = '?'
                        node1.insert(k ,node2[k])

        # Otherwise the elements are matching

        # Continue to the next element
        i += 1

    # Remove all previous elements and add elements from list
    for child in list(node1i.children):
        # If the child is a Tag typr, use decompose()
        if isinstance(child, Tag):
            child.decompose()
        # If the child is NavigableString, use extract()
        elif isinstance(child, NavigableString):
            child.extract()

    for node in node1:
        node1i.append(node)

    return node1i, tags_match

def tags_class_id_match(tag1, tag2):
    class_match = False
    id_match = False

    # If classes are matching, assume it's the same tag
    if tag1.has_attr('class') and tag2.has_attr('class'):
        
        # If neither tag has a class present, but has a class attrbute,
        # we assume they're equal
        if len(tag1['class']) == 0 and len(tag2['class']) == 0:
            class_match = True

        # Sometimes, the first tag by itself determines the content type,
        # so we use this approach instead of expecting all classes to match
        if len(tag1['class']) > 0 and len(tag2['class']) > 0:
            class_match = tag1['class'][0] == tag2['class'][0]

    # If ids are matching, assume it's the same tag
    elif tag1.has_attr('id') and tag2.has_attr('id'):
        id_match = tag1['id'] == tag2['id']

    # If neither tag has class or id attribute, assume it's the same tag
    elif not tag1.has_attr('class') and not tag2.has_attr('class') and not tag1.has_attr('id') and not tag2.has_attr('id'):
        return True

    return class_match or id_match

def count_elements(element_list, el):
    
    element_count = 0

    for child in element_list:
        if isinstance(child, Tag) and child.name == el:
            element_count += 1

    return element_count

def filter_non_elements(element_list, le):
    return [el for el in element_list if isinstance(el, Tag) and el.name == le]


def iterator_matching(node1i, node2i, el):

    # First check how many children nodes each node has, if they differ, assume
    # that all the list items are the same

    node1 = list(node1i.children)
    node2 = list(node2i.children)

    # Remove whitespace elements which seemed to occur
    node1 = [copy.copy(el) for el in node1 if isinstance(el, Tag) or (isinstance(el, NavigableString) and not el.isspace())]
    node2 = [copy.copy(el) for el in node2 if isinstance(el, Tag) or (isinstance(el, NavigableString) and not el.isspace())]

    n1_len = count_elements(node1, el)
    n2_len = count_elements(node2, el)

    nodes_return = []

    # If both lists have an equal ammount of elements
    if n1_len == n2_len:
        node1 = filter_non_elements(node1, el)
        node2 = filter_non_elements(node2, el)
        
        for i in range(0, len(node1)):
            tag, _ = recursive_matching(node1[i], node2[i])
            nodes_return.append(tag)

    # Otherwise they're not
    else:

        if DEBUG_MODE:
            print(node1[0])
            print()
            print(node2[0])
            print()
            print(recursive_matching(copy.copy(node1[n1_len - 1]), copy.copy(node1[n1_len - 2]))[1])
            print()
            print()

        # Check if the current element and the previous one are the same - square matching
        # If they're not, insert an '?' optional
        if n1_len > n2_len and not recursive_matching(copy.copy(node1[n1_len - 1]), copy.copy(node1[n1_len - 2]))[1]:

            # Go trough all the elements comparing them
            for k in range(0, n2_len):
                tag, _ = recursive_matching(copy.copy(node1[k]), copy.copy(node2[k]))
                nodes_return.append(tag)

            # Then add all the remaining elements from the second page
            for k in range(n2_len, n1_len):
                nodes_return.append(node1[k])
                nodes_return[k]['roadrunner_optional'] = '?'

        
        elif n1_len < n2_len and not recursive_matching(copy.copy(node2[n2_len - 1]), copy.copy(node2[n2_len - 2]))[1]:

            # Go trough all the elements comparing them
            for k in range(0, n2_len):
                tag, _ = recursive_matching(copy.copy(node1[k]), copy.copy(node2[k]))
                nodes_return.append(tag)

            # Then add all the remaining elements from the second page
            for k in range(n1_len, n2_len):
                nodes_return.append(node2[k])
                nodes_return[k]['roadrunner_optional'] = '?'


        # Otherwise the elements are the same; insert as '*' or '+' optional
        elif n1_len > 0 and n2_len > 0:
            tag, _ = recursive_matching(node1[0], node2[0])
            nodes_return.append(tag)
            nodes_return[0]['roadrunner_optional'] = '+'

        # If there's no elements in first table, bring in an element from second table
        # as * optional
        elif n1_len == 0:
            if n2_len == 1:
                nodes_return = node2
                nodes_return[0]['roadrunner_optional'] = '*'
            else:
                tag, _ = recursive_matching(node2[0], node2[1])
                nodes_return.append(tag)
                nodes_return[i]['roadrunner_optional'] = '*'

        # If there's no elements in second table, bring in an element from first table
        # as * optional
        elif n2_len == 0:
            if n1_len == 1:
                nodes_return = node1
                nodes_return[0]['roadrunner_optional'] = '*'
            else:
                tag, _ = recursive_matching(node1[0], node1[1])
                nodes_return.append(tag)
                nodes_return[i]['roadrunner_optional'] = '*'

    # Remove all previous elements and add elements from list
    for child in list(node1i.children):
        # If the child is a Tag typr, use decompose()
        if isinstance(child, Tag):
            child.decompose()
        # If the child is NavigableString, use extract()
        elif isinstance(child, NavigableString):
            child.extract()

    for node in nodes_return:
        node1i.append(node)

    return node1i



"""
Run the roadrunner trough given webpages
"""

# Removing the unnecessary head informaion
def filter_html(soup):

    # Remove head tag
    for head in soup.find_all("head"):
        head.decompose()

    # Remove script tags
    for script in soup.find_all("script"): 
        script.decompose()

    # Remove noscript tags
    for noscript in soup.find_all("noscript"): 
        noscript.decompose()

    # Remove style tags
    for style in soup.find_all("style"): 
        style.decompose()

    # Remove comments
    for comment in soup.find_all(string=lambda text: isinstance(text, Comment)): 
        comment.extract()

    # Remove doctype
    for comment in soup.find_all(string=lambda text: isinstance(text, Doctype)): 
        comment.extract()

    # Remove images and svgs
    for svg in soup.find_all("svg"): 
        svg.decompose()
    for img in soup.find_all("img"): 
        img.extract()

    # Removing all tag attributes but id and class
    for tag in soup.find_all(True):
        class_attr = None
        id_attr = None

        if tag.has_attr('class'):
            class_attr = tag['class']

        if tag.has_attr('id'):
            id_attr = tag['id']

        tag.attrs = {}

        if class_attr != None:
            tag.attrs['class'] = class_attr
        if id_attr != None:
            tag.attrs['id'] = id_attr

    return soup


def site_roadrunner(site):

    dir_name = "../input-extraction/" + site

    pages = []
    for _, _, files in os.walk(dir_name):
        pages = [item for item in files if item != ".DS_Store"]
        break # Only take the current folder

    print("---------------------------------------------------------------------")
    print("Pages to make wrapper with: ", pages)
    print("---------------------------------------------------------------------")
    print()

    # Convert all the pages into BeautifulSoup trees
    bs_pages = []
    page_encodings = ['utf-8', 'ansi', 'ascii', 'latin']
    for page in pages:
        page_html = try_reading_with_encoding(dir_name, page, page_encodings)

        # If no encoding worked, return
        if page_html == None:
            print("################## ERROR CREATING WRAPPER FOR SITE ##################")
            return

        # Add the page to the list, convert to LXML format
        bs_pages.append(filter_html(BeautifulSoup(page_html, "lxml")))

    # First page is the base to build wrapper on, other pages
    # are used to compare
    tokens = create_wrapper(bs_pages[0], bs_pages[1:])

    # Saving the wrappers into files inside roadrunner_wrappers folder
    filename = "./roadrunner_wrappers/" + site + ".html"
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    f = open(filename, 'w', encoding="utf-8")
    f.write(tokens.prettify())
    f.close()


def try_reading_with_encoding(dir_name, page, encodings):

    # If there is an encoding to try, try it
    if len(encodings) > 0:

        try:
            # Read the page from file using first element's encoding
            f = open(dir_name + "/" +  page, 'r', encoding=encodings[0])

            return f.read()

        except:
            # Delete first element from encoding list
            del encodings[0]

            # Try reading using another encoding
            return try_reading_with_encoding(dir_name, page, encodings)

    return None
        
    
def run_roadrunner(site=""):

    # If we specify only to make wrapper for one site, do that
    if site != "":
        site_roadrunner(site)

    # Otherwise do the wrapper generation for all sites
    else:
        # Get all the directories that will contain pages to make wrappers for
        directories = []

        for _, dirs, _ in os.walk("../input-extraction"):
            directories = [item for item in dirs if item != "__MACOSX"]
            break # Only take the current folder

        print("---------------------------------------------------------------------")        
        print("Websites to make wrappers for: ", directories)
        print("---------------------------------------------------------------------")        
        print()

        # Automatically create the wrapper(s)
        for site in directories:
            try:
                site_roadrunner(site)
            except:
                print("################## ERROR CREATING WRAPPER FOR SITE ##################")
                print()

                if DEBUG_MODE:
                    traceback.print_exc()
                    print()