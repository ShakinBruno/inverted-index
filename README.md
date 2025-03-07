# Inverted Index

An inverted index is a data structure used to map words to the indices of documents where these words occur. This structure significantly enhances the efficiency of recommendation systems by enabling faster matching and retrieval of the most relevant documents.

## Overview

This project provides a command-line interface (CLI) tool for building, saving, loading, and querying an inverted index from a collection of text documents. The tool is designed to handle large datasets efficiently and supports various input and output formats.

## Features

- **Import Documents**: The script can read text files (`.txt`) into memory for processing.
- **Text Cleaning**: Stop words are removed from each document to improve the quality of the inverted index.
- **Build Inverted Index**: Constructs a dictionary where keys are words and values are lists of document indices where these words appear.
- **Save Inverted Index**: The constructed index can be saved to a JSON file for persistent storage.
- **Load Inverted Index**: Load an inverted index from a JSON file for querying.
- **Query Input**: Supports multiple formats for entering queries, including standard input (stdin) and file input.
- **Result Output**: Displays the document IDs where the queried words are found, either in standard output (stdout) or standard error (stderr).

## Typical Workflow

1. **Import**: Load the text documents into RAM.
2. **Text Cleaning**: Remove stop words from each document to focus on significant terms.
3. **Build Inverted Index**: Create the index dictionary based on the cleaned documents.
4. **Save Inverted Index**: Serialize and save the index to a JSON file.
5. **Load Inverted Index**: Deserialize and load the index from a JSON file when needed.
6. **Enter Query**: Choose the format for entering queries to search for relevant documents.
7. **Available Formats**: By default, queries are entered via stdin. Optionally, queries can be read from a file.
8. **Print the Result**: Output the document IDs to stdout or stderr.

## Usage

### Building the Inverted Index

To build the inverted index from a dataset:

```bash
python inverted_index.py build -d path/to/dataset.txt -s path/to/stopwords.txt -o path/to/output.json
```

### Querying the Inverted Index

To query the inverted index:

```bash
python inverted_index.py query --index path/to/output.json --q "word1" "word2"
```

Or, to query using a file:

```bash
python inverted_index.py query --index path/to/output.json --query_from_file path/to/query.txt
```

## Dependencies

- Python 3.x
