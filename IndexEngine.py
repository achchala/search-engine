"""
This program reads a gzip-compressed LATimes file (latimes.gz), extracts metadata (DOCNO, HEADLINE), and text from each document, and:
- Tokenizes text from the TEXT, HEADLINE, and GRAPHIC tags (without removing stopwords or stemming)
- Calculates and stores document lengths
- Converts tokens to integer IDs using a lexicon
- Builds an in-memory inverted index, mapping term IDs to document IDs and term frequencies
- Stores each document as a separate file in a directory structure based on the document's date (YY/MM/DD), using the DOCNO as the filename

Usage:
    python index_engine.py <path_to_gz_file> <output_directory>
    
Arguments:
    <path_to_gz_file>: path to the latimes.gz file containing the documents
    <output_directory>: directory where the documents and metadata will be stored

Example:
    python IndexEngine.py /home/smucker/latimes.gz /home/smucker/latimes-index

"""

from datetime import datetime
import json
import os
import gzip
import sys
import re
from collections import defaultdict

# global vars
docnos = []
docno_to_id = {}
lexicon = {}
postings = defaultdict(list)
curr_tid = 0
doc_lengths = []


def main():
    if len(sys.argv) != 3:
        print("Usage: python IndexEngine.py <path_to_gz_file> <output_dir>")
        sys.exit(1)

    input_gz = sys.argv[1]
    output_dir = sys.argv[2]

    if not os.path.exists(input_gz):
        print(f"Error: File '{input_gz}' does not exist.")
        sys.exit(1)

    if os.path.exists(output_dir):
        print(f"Error: Output directory '{output_dir}' already exists.")
        sys.exit(1)

    os.makedirs(output_dir, exist_ok=True)

    docno_list_file = os.path.join(output_dir, "docno_list.txt")
    docno_id_map_file = os.path.join(output_dir, "docno_id_map.json")

    with open(docno_list_file, "w") as map_out:
        with gzip.open(input_gz, "rt") as f:
            doc = ""
            within = False
            for line in f:
                if "<DOC>" in line:
                    within = True
                    doc = line
                elif "</DOC>" in line:
                    doc += line
                    process(doc, output_dir, map_out, len(docnos))
                    docnos.append(doc.split("</DOCNO>")[0].split("<DOCNO>")[1].strip())
                    doc = ""
                    within = False
                elif within:
                    doc += line
    with open(docno_id_map_file, "w") as f:
        json.dump(docno_to_id, f, indent=4)

    save(output_dir)


def process(doc, output_dir, map_out, iid):
    global curr_tid
    docno = extract(doc, "DOCNO")
    headline = extract(doc, "HEADLINE")
    year, month, day = parse_docno_to_date(docno)
    text_content = (
        extract(doc, "TEXT")
        + " "
        + extract(doc, "HEADLINE")
        + " "
        + extract(doc, "GRAPHIC")
    )
    tokens = []
    Tokenize(text_content, tokens)
    length = len(tokens)
    doc_lengths.append(length)

    tf = defaultdict(int)
    for token in tokens:
        if token not in lexicon:
            lexicon[token] = curr_tid
            curr_tid += 1
        tid = lexicon[token]
        tf[tid] += 1

    for tid, freq in tf.items():
        postings[tid].append((iid, freq))

    docno_to_id[docno] = iid
    map_out.write(docno + "\n")

    # normalize the headline to a single line
    headline = " ".join(headline.split())

    date_path = os.path.join(output_dir, year, month, day)
    os.makedirs(date_path, exist_ok=True)

    raw_doc_filename = os.path.join(date_path, f"{docno}.txt")
    with open(raw_doc_filename, "w") as raw_doc_file:
        raw_doc_file.write(f"{doc}\n")

    metadata_filename = os.path.join(date_path, f"{docno}.metadata.txt")
    with open(metadata_filename, "w") as metadata_file:
        metadata_file.write(f"docno: {docno}\n")
        metadata_file.write(f"internal id: {iid}\n")
        metadata_file.write(f"date: {format_date(year, month, day)}\n")
        metadata_file.write(f"headline: {headline}\n")
        metadata_file.write(f"document length: {length}\n")


# Based on SimpleTokenizer by Trevor Strohman,
# http://www.galagosearch.org/
def Tokenize(text, tokens):
    text = text.lower()
    start = 0
    i = 0
    for currChar in text:
        if not currChar.isdigit() and not currChar.isalpha():
            if start != i:
                token = text[start:i]
                tokens.append(token)
            start = i + 1
        i = i + 1
    if start != i:
        tokens.append(text[start:i])


def save(output_dir):
    inverted_index_file = os.path.join(output_dir, "inverted-index.json")
    lexicon_file = os.path.join(output_dir, "lexicon.json")
    doc_lengths_file = os.path.join(output_dir, "doc-lengths.txt")

    with open(inverted_index_file, "w") as f:
        json.dump(postings, f)
    with open(lexicon_file, "w") as f:
        json.dump(lexicon, f)
    with open(doc_lengths_file, "w") as f:
        for length in doc_lengths:
            f.write(f"{length}\n")


def extract(doc, tag):
    start_tag = f"<{tag}>"
    end_tag = f"</{tag}>"

    start = doc.find(start_tag)
    end = doc.find(end_tag)

    if start == -1 or end == -1:
        return ""
    content = doc[start + len(start_tag) : end].strip()
    content = re.sub(r"<[^>]+>", "", content)
    return content


def parse_docno_to_date(docno):
    month = docno[2:4]
    day = docno[4:6]
    year = "19" + docno[6:8]
    return year, month, day


def format_date(year, month, day):
    date_obj = datetime.strptime(f"{year}-{month}-{day}", "%Y-%m-%d")
    formatted_date = date_obj.strftime("%B %d, %Y")
    return formatted_date


if __name__ == "__main__":
    main()
