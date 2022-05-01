import os
import copy
import traceback

from bs4 import BeautifulSoup, Tag, NavigableString
from lxml.html.clean import Cleaner

DEBUG_MODE = True



"""
Create wrapper with recurvsive tag and string matching check
"""

def create_wrapper(site_wrapper, pages):

    # Go trough all pages, iterativelly building a wrapper
    for page in pages:
        site_wrapper = recursive_matching(site_wrapper, page)

    return site_wrapper


def recursive_matching(node1i, node2i):

    # Start with the first child node
    i = 0

    # Creating a copy of node, decoupling it from parent
    node1 = [copy.copy(el) for el in node1i.children if not (isinstance(el, NavigableString) and el.string.isspace())]
    node2 = [copy.copy(el) for el in node2i.children if not (isinstance(el, NavigableString) and el.string.isspace())]

    if len(node1) == 0 and len(node2) == 0:
        return node1i

    # Loop trough them, adding new ones
    while i < len(node1) or i < len(node2):

        # If we came to the end with first page, but not with the second,
        # add tags from the second page as optionals
        if i >= len(node1) and i < len(node2):

            # We just add the remainint items, and anotate them as optionals
            for j in range(i, len(node2)):
                node1.insert(j, node2[j])

                if isinstance(node1[j], Tag):
                    node1[j]['roadrunner_optional'] = '?'

        # If we came to the end with second page, but not with the first,
        # set tags from the first page as optionals
        elif i >= len(node2) and i < len(node1):
            for j in range(i, len(node1)):
                if isinstance(node1[j], Tag):
                    node1[j]['roadrunner_optional'] = '?'

        # There is no tag mismatch, check for mismatches recursivelly
        elif isinstance(node1[i], Tag) and isinstance(node2[i], Tag) and node1[i].name == node2[i].name:

            # If current tag is of type ul, ol or td, do iterator tag mismatching
            if node1[i].name == "ol" or node1[i].name == "ul" or node1[i].name == "thead" or node1[i].name == "tbody" or node1[i].name == "tfoot":
                node1[i] = iterator_matching(node1[i], node2[i])

            # Else do regular tag mismatching
            else:
                node1[i] = recursive_matching(node1[i], node2[i])

        # String mismatch
        elif isinstance(node1[i], NavigableString) and isinstance(node2[i], NavigableString) and node1[i].string != node2[i].string:
            node1[i] = "#PCDATA"

        # If the strings are the same, don't change them        
        elif isinstance(node1[i], NavigableString) and isinstance(node2[i], NavigableString) and node1[i].string == node2[i].string:
            pass

        # Other type of mismatch, we use cross search checking
        else:
            foundMatch = False

            # Do cross search
            for j in range(i, max(len(node1), len(node2))):

                # Matching tags appear on the current index
                if j < len(node1) and j < len(node2) and isinstance(node1[j], Tag) and isinstance(node2[j], Tag) and node1[j].name == node2[j].name:
                    l = j - i

                    for k in range(i, j):
                        if isinstance(node1[k], Tag):
                            node1[k]['roadrunner_optional'] = '?'
                        node2.insert(k, node1[k])

                    for k in range(j, j + l):
                        if isinstance(node2[k], Tag):
                            node2[k]['roadrunner_optional'] = '?'
                        node1.insert(k, node2[k])
                    
                    foundMatch = True

                    break
                
                # Current tag on second page has appeared before
                elif j < len(node2) and isinstance(node2[j], Tag) and node2[j].name in [el.name for el in node1[i:min(j, len(node1))] if isinstance(el, Tag)]:
                    foundIndex = i
                    
                    while not isinstance(node1[foundIndex], Tag) or node2[j].name != node1[foundIndex].name:
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
                    
                    break

                # Current tag on first page has appeared before
                elif j < len(node1) and isinstance(node1[j], Tag) and node1[j].name in [el.name for el in node2[i:min(j, len(node2))] if isinstance(el, Tag)]:
                    foundIndex = i
                    
                    while not isinstance(node2[foundIndex], Tag) or node1[j].name != node2[foundIndex].name:
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
                    
                    break

            # If there were no matches in cross search, add all the remaining nodes
            if not foundMatch:
                for k in range(i, len(node1)):
                    if isinstance(node1[k], Tag):
                        node1[k]['roadrunner_optional'] = '?'

                for k in range(i, len(node2)):
                    if isinstance(node2[k], Tag):
                        node2[k]['roadrunner_optional'] = '?'

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

    return node1i


def count_list_elements(element_list):
    
    element_count = 0

    for child in element_list:
        # TODO - finish this so that it'll work for tables too
        if isinstance(child, Tag) and child.name == "li":
            element_count += 1

    return element_count


def filter_non_li(element_list):
    return [el for el in element_list if isinstance(el, Tag) and el.name == "li"]


def iterator_matching(node1i, node2i):

    # First check how many children nodes each node has, if they differ, assume
    # that all the list items are the same

    node1 = list(node1i.children)
    node2 = list(node2i.children)

    # Remove whitespace elements which seemed to occur
    node1 = [copy.copy(el) for el in node1 if isinstance(el, Tag) or (isinstance(el, NavigableString) and not el.isspace())]
    node2 = [copy.copy(el) for el in node2 if isinstance(el, Tag) or (isinstance(el, NavigableString) and not el.isspace())]

    n1_len = count_list_elements(node1)
    n2_len = count_list_elements(node2)

    nodes_return = []

    if n1_len != n2_len:

        # If the element count is not the same, assume the elements are equal
        # and make them + optionals
        if n1_len > 0 and n2_len > 0:
            nodes_return.append(recursive_matching(node1[0], node2[0]))
            nodes_return[0]['roadrunner_optional'] = '+'

        # If there's no elements in first table, bring in an element from second table
        # as * optional
        elif n1_len == 0:
            nodes_return = node2
            for i in range(0, len(nodes_return)):
                nodes_return[i]['roadrunner_optional'] = '*'

        # If there's no elements in second table, bring in an element from first table
        # as * optional
        elif n2_len == 0:
            nodes_return = node1
            for i in range(0, len(nodes_return)):
                nodes_return[i]['roadrunner_optional'] = '*'

    # Otherwise compare each list element in one list to the
    # corresponding element in the other list
    else:
        node1 = filter_non_li(node1)
        node2 = filter_non_li(node2)
        
        for i in range(0, len(node1)):
            nodes_return.append(recursive_matching(node1[i], node2[i]))

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

    # Remove style tags
    for style in soup.find_all("style"): 
        style.decompose()

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
    page_encodings = ['utf-8', 'ansi', 'ascii']
    for page in pages:
        # TODO - if charset is present in file oblige it (overstock.com doesn't have it though)
        page_html = try_reading_with_encoding(dir_name, page, page_encodings)

        # If no encoding worked, return
        if page_html == None:
            print("################## ERROR CREATING WRAPPER FOR SITE ##################")
            return

        # Add the page to the list
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

            # Clean up html files not formatted according to XHTML specification
            cleaner = Cleaner(remove_unknown_tags=False, page_structure=True)
            return cleaner.clean_html(f.read())

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


# TODO - remove this, it's just for debugging purpouses
# run_roadrunner()