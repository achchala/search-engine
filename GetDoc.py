"""
This program retrieves and displays a document and its metadata from a document store
that was created by IndexEngine. It supports fetching documents by DOCNO or internal ID.

Usage:
    python GetDoc.py <document_store> <id|docno> <identifier>
    
Arguments:
    <document_store>: path to the directory where the documents are stored
    <id|docno>: specify whether to search by internal ID or DOCNO
    <identifier>: either the internal ID or DOCNO of the document to retrieve

    GetDoc /home/smucker/latimes-index docno LA010290-0030
    GetDoc /home/smucker/latimes-index id 6832

"""

import os
import sys


def main():
    if len(sys.argv) != 4:
        print("Usage: python GetDoc.py <document_store> <id|docno> <identifier>")
        sys.exit(1)

    document_store = sys.argv[1]
    search_type = sys.argv[2]
    identifier = sys.argv[3]

    docnos = load_docnos(document_store)

    if search_type == "docno":
        docno = identifier
        if docno not in docnos:
            print(f"Error: Document with DOCNO {docno} not found.")
            sys.exit(1)
        internal_id = docnos.index(docno)
    elif search_type == "id":
        internal_id = int(identifier)
        if internal_id >= len(docnos):
            print(f"Error: Document with internal ID {internal_id} not found.")
            sys.exit(1)
        docno = docnos[internal_id]
    else:
        print("Error: The second argument must be either 'id' or 'docno'.")
        sys.exit(1)

    display_document(document_store, docno, internal_id)


def load_docnos(document_store):
    docnos_file = os.path.join(document_store, "docno_list.txt")
    if not os.path.exists(docnos_file):
        print(f"Error: docno_list.txt file not found in {document_store}")
        sys.exit(1)

    with open(docnos_file, "r") as f:
        docnos = [line.strip() for line in f.readlines()]
    return docnos


def display_document(document_store, docno, internal_id):
    year, month, day = docno_to_date(docno)
    doc_file_path = os.path.join(document_store, year, month, day, f"{docno}.txt")
    metadata_file_path = os.path.join(
        document_store, year, month, day, f"{docno}.metadata.txt"
    )

    if not os.path.exists(metadata_file_path):
        print(f"Error: Metadata file {metadata_file_path} not found.")
        sys.exit(1)

    if not os.path.exists(doc_file_path):
        print(f"Error: Document file {doc_file_path} not found.")
        sys.exit(1)

    with open(metadata_file_path, "r") as metadata_file:
        metadata_content = metadata_file.read()
        print(metadata_content)

    print("raw document:")
    with open(doc_file_path, "r") as doc_file:
        content = doc_file.read()
        print(content)


def docno_to_date(docno):
    month = docno[2:4]
    day = docno[4:6]
    year = "19" + docno[6:8]
    return year, month, day


def format_date(year, month, day):
    from datetime import datetime

    date_obj = datetime.strptime(f"{year}-{month}-{day}", "%Y-%m-%d")
    return date_obj.strftime("%B %d, %Y")


if __name__ == "__main__":
    main()
