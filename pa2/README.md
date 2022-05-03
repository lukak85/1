# s.pyderman Data Extractor

__TODO__ - write an introduction

Explanation of each method;
* __extraction using regular expressions__: TODO
* __extraction using XPath__: TODO
* __extraction using RoadRunner__: using this method, we automatically generate a wrapper (using a website page batch) with which we can extract data from said website. In our implementation, the website first has to be converted to an XHTML compliant format. The result is then converted into a tree, which we use to compare the content of the websites and with it iteretively build the wrapper.

    The implementation for the most part follows the approach described in the paper [RoadRunner: Towards Automatic Data Extraction from Large Web Sites](http://vldb.org/conf/2001/P109.pdf).

## Prerequisites

Install the dependencies by opening the command line prompt inside [current folder](/pa2/) and running the following command:

```bash
pip install -r requirements.txt
```

## Running the extractor

To run the extractor, you are given three options:
* __A__: extraction using regular expressions
* __B__: extraction using XPath
* __C__: extraction using RoadRunner (note that our method only generates a wrapper, which can then be used to implement an extractor)

To run the extractor, open the command line prompt inside [implementation-extraction](/pa2/implementation-extraction/) and run the following command:

```bash
py run-extraction.py A --site [site]
```

Note:
* The command above runs the extractor using method _A_; to run using methods _B_ and _C_, use the respective letters.
* Using the `--site` tag you can tell the extractor to only run the method on the site specified (e.g. `rtvslo.si`).