# s.pyderman Data Extractor

## About

__TODO__ - write an introduction

Explanation of each method;
* __extraction using regular expressions__: TODO
* __extraction using XPath__: TODO
* __extraction using RoadRunner implementation__: using this method, we automatically extract a wrapper using which we'll extract the data from the website. In our implementation, the website first has to be converted to an XHTML compliant format. The result is then converted into a tree, which we use to compare the content of the websites and with it iteretivelly build the wrapper

## Prerequisites

Install the dependencies by opening the command line prompt inside [current folder](/pa2/) and running the following command:

```bash
pip install -r requirements.txt
```

## Running the extractor

To run the extractor, you are given three options:
* __A__: extraction using regular expressions
* __B__: extraction using XPath
* __C__: extraction using RoadRunner implementation (automatic extraction of an arbitrary website batch)

To run the extractor, open the command line prompt inside [implementation-extraction](/pa2/implementation-extraction/) and run the following command:

```bash
py run-extraction.py A
```

Note that the command above runs the extractor using method _A_; to run using methods _B_ and _C_, use the respective letters.