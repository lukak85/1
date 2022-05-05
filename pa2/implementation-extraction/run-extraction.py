import sys

from roadrunner_extraction import run_roadrunner
from xpath_extraction import run_xpath
from regex_extraction import run_regex

if sys.argv[1] == "A":
    print("Regular expressions extraction")
    run_regex()
elif sys.argv[1] == "B":
    print("XPath extraction")
    run_xpath()
elif sys.argv[1] == "C":
    print("Automatic Web extraction")
    run_roadrunner()