import json
import os
import re
import time
from bm25 import calculate_bm25, Tokenize
from query_biased_summary import generate_query_biased_snippet, extract_text_tag
from collections import defaultdict
from GetDoc import docno_to_date

DOCUMENTS_PATH = "storage"


def load_metadata(base_dir, docno):
    year, month, day = docno_to_date(docno)
    metadata_path = os.path.join(base_dir, year, month, day, f"{docno}.metadata.txt")

    if not os.path.exists(metadata_path):
        return {"headline": "Unknown Title", "date": "Unknown Date"}

    metadata = {}
    with open(metadata_path, "r") as file:
        lines = file.readlines()
        for line in lines:
            if line.startswith("headline:"):
                metadata["headline"] = line[len("headline:") :].strip()
            elif line.startswith("date:"):
                metadata["date"] = line[len("date:") :].strip()

    metadata.setdefault("headline", "Unknown Title")
    metadata.setdefault("date", "Unknown Date")

    return metadata


def display_results(ranked_results, documents, query_tokens, docno_list):
    print("\nTop 10 Results:")
    for rank, (doc_id, score) in enumerate(ranked_results, start=1):
        docno = docno_list[int(doc_id)]
        doc_text = documents.get(docno, "Document not found.")

        if doc_text == "Document not found.":
            print(f"{rank}. Document not found. (Unknown Date)")
            print(f"Document not found. ({docno})")
            continue

        metadata = load_metadata(DOCUMENTS_PATH, docno)
        headline = metadata["headline"]
        date = metadata["date"]
        snippet = generate_query_biased_snippet(doc_text, query_tokens)

        print(f"{rank}. {headline} ({date})")
        print(f"{snippet} ({docno})\n")


def load_data(base_dir):
    index_path = os.path.join(base_dir, "inverted-index.json")
    lexicon_path = os.path.join(base_dir, "lexicon.json")
    doclengths_path = os.path.join(base_dir, "doc-lengths.txt")
    docno_list_path = os.path.join(base_dir, "docno_list.txt")
    documents_path = base_dir

    with open(index_path, "r") as f:
        inverted_index = json.load(f)

    with open(lexicon_path, "r") as f:
        lexicon = json.load(f)

    with open(doclengths_path, "r") as f:
        doc_lengths = [int(line.strip()) for line in f.readlines()]

    with open(docno_list_path, "r") as f:
        docno_list = [line.strip() for line in f.readlines()]

    documents = {}
    for root, _, files in os.walk(documents_path):
        for file in files:
            if file.endswith(".txt") and not file.endswith(".metadata.txt"):
                doc_path = os.path.join(root, file)
                docno = os.path.splitext(file)[0]
                with open(doc_path, "r") as doc_file:
                    documents[docno] = doc_file.read()

    print(f"Loaded {len(documents)} documents from {DOCUMENTS_PATH}.")

    return inverted_index, lexicon, doc_lengths, docno_list, documents


def main():
    print("Loading data from storage...")
    inverted_index, lexicon, doc_lengths, docno_list, documents = load_data(
        DOCUMENTS_PATH
    )
    avg_doc_length = sum(doc_lengths) / len(doc_lengths)
    print("Data loaded.")

    while True:
        query = input("\nEnter your query (or 'Q' to quit): ").strip()
        if query.lower() == "q":
            print("Exiting the search engine. Goodbye!")
            break

        start_time = time.time()
        query_tokens = []
        Tokenize(query, query_tokens)
        queries = {1: " ".join(query_tokens)}

        ranked_results = calculate_bm25(
            queries, inverted_index, lexicon, doc_lengths, docno_list, avg_doc_length
        )
        elapsed_time = time.time() - start_time

        display_results(ranked_results[1][:10], documents, query_tokens, docno_list)

        print(f"\nRetrieval took {elapsed_time:.2f} seconds.")

        while True:
            action = input(
                "\nType a rank number to view the document, 'N' for a new query, or 'Q' to quit: "
            ).strip()
            if action.lower() == "q":
                print("Exiting the search engine. Goodbye!")
                return
            elif action.lower() == "n":
                break
            elif action.isdigit() and 1 <= int(action) <= 10:
                rank = int(action)
                doc_id = ranked_results[1][rank - 1][0]
                docno = docno_list[doc_id]
                print(f"\nDocument {docno}:\n")
                print(documents.get(docno, "Document content not found."))
            else:
                print("Invalid input. Please try again.")


if __name__ == "__main__":
    main()
