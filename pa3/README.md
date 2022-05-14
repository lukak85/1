# s.pyderman indexer

A web indexer is a progam that extracts data from webpages and organizes said data to be able to achieve very quick responses to data retrieval queries.

For data retrieval, we use two approaches:
* without SQLite or
* with SQLite.

# Prerequisites

Install the dependencies by opening the command line prompt inside [current folder](/pa3/) and running the following command:

```bash
pip install -r requirements.txt
```

# Running the indexer

First, we need to run the indexer to fill the SQLite database with the appropriate data which we will use for fast data retrieval. Open the command line prompt in the [implementation-indexing](/pa3/implementation-indexing/) folder, then run the following command:

```bash
py indexing.py
```

For data retrieval without SQLite, use the following command:

```bash
py run-basic-search.py
```

For a much faster data retrieval using SQLite using the data obtained with the indexer, use the the following command:

```bash
py run-sqlite-search.py
```