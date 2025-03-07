import json
import re
import sys
from argparse import ArgumentParser, ArgumentTypeError, FileType
from collections import defaultdict
from io import TextIOWrapper
from typing import Dict, List, Set, Union

DEFAULT_PATH_TO_STOPWORDS = "./input_files/stop_words_en.txt"
DEFAULT_PATH_TO_STORE_INVERTED_INDEX = "./output_files/inverted.index"


class EncodedFileType(FileType):
    """File encoder"""

    def __call__(self, string):
        # the special argument "-" means sys.std{in,out}
        if string == "-":
            if "r" in self._mode:
                stdin = TextIOWrapper(sys.stdin.buffer, encoding=self._encoding)
                return stdin
            if "w" in self._mode:
                stdout = TextIOWrapper(sys.stdout.buffer, encoding=self._encoding)
                return stdout
            msg = 'argument "-" with mode %r' % self._mode
            raise ValueError(msg)

        # all other arguments are used as file names
        try:
            return open(string, self._mode, self._bufsize, self._encoding, self._errors)
        except OSError as exception:
            args = {"filename": string, "error": exception}
            message = "can't open '%(filename)s': %(error)s"
            raise ArgumentTypeError(message % args)

    def print_encoder(self):
        """printer of encoder"""
        print(self._encoding)


class InvertedIndex:
    """
    This module is necessary to extract inverted indexes from documents.
    """

    def __init__(self, words_ids: Dict[str, List[int]]):
        self.inverted_index = words_ids

    def query(self, words: List[str]) -> List[int]:
        """Return the list of relevant documents for the given query"""
        result = set()
        for word in words:
            entry = self.inverted_index.get(word)
            if not entry:
                continue
            result.update(entry)
        return list(result)

    def dump(self, handler: Union[str, TextIOWrapper]) -> None:
        """
        Allow us to write inverted indexes documents to temporary directory or local storage
        :param handler: path to file with documents or TextIOWrapper
        :return: None
        """
        file = get_handler(handler, "w")
        with file as f:
            json.dump(self.inverted_index, f)

    @classmethod
    def load(cls, handler: Union[str, TextIOWrapper]) -> "InvertedIndex":
        """
        Allow us to upload inverted indexes from either temporary directory or local storage
        :param handler: path to file with documents or TextIOWrapper
        :return: InvertedIndex
        """
        file = get_handler(handler, "r")
        with file as f:
            return cls(json.load(f))


def get_handler(handler: Union[str, TextIOWrapper], mode: str) -> TextIOWrapper:
    """
    :param handler: path to file with documents or TextIOWrapper
    :param mode: mode of file
    :return: TextIOWrapper
    """
    # The appropriate TextIOWrapper should be returned depending on
    # whether we are using ArgumentParser in the CLI or running pytest tests
    return handler if isinstance(handler, TextIOWrapper) else open(handler, mode, encoding="utf-8")


def load_documents(handler: Union[str, TextIOWrapper]) -> Dict[int, str]:
    """
    Allow us to upload documents from either temporary directory or local storage
    :param handler: path to file with documents or TextIOWrapper
    :return: Dict[int, str]
    """
    file = get_handler(handler, "r")
    documents: Dict[int, str] = {}
    with file as f:
        for line in f:
            doc_id, content = line.lower().split("\t", 1)
            documents[int(doc_id)] = content
    return documents


def load_stopwords(handler: Union[str, TextIOWrapper]) -> Set[str]:
    """
    Load stopwords from file
    :param handler: path to file with stopwords or TextIOWrapper
    :return: Set[str]
    """
    file = get_handler(handler, "r")
    with file as f:
        stopwords: Set[str] = set(word.strip().lower() for word in f)
    return stopwords


def build_inverted_index(documents: Dict[int, str], stopwords: Set[str]) -> InvertedIndex:
    """
    Builder of inverted indexes based on documents
    :param documents: dict with documents
    :param stopwords: set of stopwords
    :return: InvertedIndex class
    """
    inverted_index: Dict[str, Set[int]] = defaultdict(set)
    for doc_id, content in documents.items():
        words = re.split(r"\W+", content)
        filtered_words = [word for word in words if word not in stopwords]
        for filtered_word in filtered_words:
            inverted_index[filtered_word].add(doc_id)
    mapped_inverted_index = {word: list(doc_ids) for word, doc_ids in inverted_index.items()}
    return InvertedIndex(mapped_inverted_index)


def callback_build(arguments) -> None:
    """process build runner"""
    return process_build(arguments.dataset, arguments.stopwords, arguments.output)


def process_build(dataset, stopwords, output) -> None:
    """
    Function is responsible for running of a pipeline to load documents,
    build and save inverted index.
    :param arguments: key/value pairs of arguments from 'build' subparser
    :return: None
    """
    documents: Dict[int, str] = load_documents(dataset)
    stop_words: Set[str] = load_stopwords(stopwords)
    inverted_index = build_inverted_index(documents, stop_words)
    inverted_index.dump(output)


def callback_query(arguments) -> None:
    """ "callback query runner"""
    process_query(arguments.query, arguments.index)


def process_query(queries, index) -> None:
    """
    Function is responsible for loading inverted indexes
    and printing document indexes for key words from arguments.query
    :param arguments: key/value pairs of arguments from 'query' subparser
    :return: None
    """
    inverted_index = InvertedIndex.load(index)
    for query in queries:
        if isinstance(query, str):
            query = query.strip().split()

        doc_indexes = " ".join(map(str, inverted_index.query(query)))
        print(f"{query}: {doc_indexes}")


def setup_subparsers(parser) -> None:
    """
    Initial subparsers with arguments.
    :param parser: Instance of ArgumentParser
    """
    subparser = parser.add_subparsers(dest="command")
    build_parser = subparser.add_parser(
        "build",
        help="this parser is need to load, build"
        " and save inverted index bases on documents",
    )
    build_parser.add_argument(
        "-d",
        "--dataset",
        required=True,
        type=EncodedFileType("r", encoding="utf-8"),
        help="You should specify path to file with documents. ",
    )
    build_parser.add_argument(
        "-s",
        "--stopwords",
        type=EncodedFileType("r", encoding="utf-8"),
        default=DEFAULT_PATH_TO_STOPWORDS,
        help="You should specify path to file with stopwords. "
        "The default: %(default)s",
    )
    build_parser.add_argument(
        "-o",
        "--output",
        type=EncodedFileType("w", encoding="utf-8"),
        default=DEFAULT_PATH_TO_STORE_INVERTED_INDEX,
        help="You should specify path to save inverted index. "
        "The default: %(default)s",
    )
    build_parser.set_defaults(callback=callback_build)

    query_parser = subparser.add_parser(
        "query", help="This parser is need to load and apply inverted index"
    )
    query_parser.add_argument(
        "--index",
        type=EncodedFileType("r", encoding="utf-8"),
        default=DEFAULT_PATH_TO_STORE_INVERTED_INDEX,
        help="specify the path where inverted indexes are. " "The default: %(default)s",
    )
    query_file_group = query_parser.add_mutually_exclusive_group(required=True)
    query_file_group.add_argument(
        "-q",
        "--query",
        dest="query",
        action="append",
        nargs="+",
        help="you can specify a sequence of queries to process them overall",
    )
    query_file_group.add_argument(
        "--query_from_file",
        dest="query",
        type=EncodedFileType("r", encoding="utf-8"),
        default=TextIOWrapper(sys.stdin.buffer, encoding="utf-8"),
        help="query file to get queries for inverted index",
    )
    query_parser.set_defaults(callback=callback_query)


def main():
    """
    Starter of the pipeline
    """

    parser = ArgumentParser(
        description="Inverted Index CLI is need to load, build,"
        "process query inverted index"
    )
    setup_subparsers(parser)
    arguments = parser.parse_args()
    arguments.callback(arguments)


if __name__ == "__main__":
    main()
