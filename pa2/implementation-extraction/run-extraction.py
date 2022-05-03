import sys

from roadrunner_extraction import run_roadrunner
from xpath_extraction import run_xpath

if sys.argv[1] == "A":
    print("Regular expressions extraction")
elif sys.argv[1] == "B":
    print("XPath extraction")
    run_xpath()
elif sys.argv[1] == "C":
    print("Automatic Web extraction")
    if len(sys.argv) > 3 and sys.argv[2] == "--site":
        run_roadrunner(sys.argv[3])
    else:
        run_roadrunner()