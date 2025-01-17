"""
This program retrieves and displays a document and its metadata from a document store
that was created by IndexEngine. It supports fetching documents by DOCNO or internal ID.

Usage:
    python BooleanAND.py queries.txt hw2-results-adeepan.txt
    
Arguments:
    <index>: path to the directory where the index is stored
    <queries>: 
    <output>: 

    python BooleanAND.py queries.txt hw2-results-adeepan.txt

"""

import json
import sys


def load(index_dir):
    with open(f"{index_dir}/inverted-index.json", "r") as f:
        inv_index = json.load(f)
    with open(f"{index_dir}/lexicon.json", "r") as f:
        lexicon = json.load(f)
    with open(f"{index_dir}/docno_list.txt", "r") as f:
        docno_list = [line.strip() for line in f.readlines()]
    return inv_index, lexicon, docno_list


def read_queries(queries_file):
    queries = []
    with open(queries_file, "r") as f:
        lines = f.readlines()
        for i in range(0, len(lines), 2):
            topic_id = int(lines[i].strip())
            query = lines[i + 1].strip()
            queries.append((topic_id, query))
    return queries


def boolean_and(query, lexicon, inv_index):
    terms = []
    Tokenize(query, terms)
    print(f"Tokenized query terms: {terms}")

    terms = [term.lower() for term in terms]
    print(f"Lowercased terms: {terms}")

    valid_terms = [term for term in terms if term in lexicon]
    print(f"Valid terms found in lexicon: {valid_terms}")

    if not valid_terms:
        return []  # no valid terms found

    valid_terms.sort(key=lambda term: len(inv_index[str(lexicon[term])]))
    print(f"Terms sorted by postings list length: {valid_terms}")

    # postings list for the first valid term
    print(
        f"Postings list for '{valid_terms[0]}': {inv_index[str(lexicon[valid_terms[0]])]}"
    )

    # start with the result set from the first term
    result_set = [doc_id for doc_id, _ in inv_index[str(lexicon[valid_terms[0]])]]
    print(f"Initial result set from first term '{valid_terms[0]}': {result_set}")

    # intersect the result set with the postings lists of the other terms
    for term in valid_terms[1:]:
        postings = inv_index[str(lexicon[term])]
        print(f"Postings list for '{term}': {postings}")
        new_results = []
        i, j = 0, 0
        while i < len(result_set) and j < len(postings):
            if result_set[i] == postings[j][0]:
                new_results.append(result_set[i])
                i += 1
                j += 1
            elif result_set[i] < postings[j][0]:
                i += 1
            else:
                j += 1
        result_set = new_results
        print(f"Updated result set after processing term '{term}': {result_set}")
    return result_set


def write_results(output_file, results, docno_list):
    with open(output_file, "w") as f:
        for topic_id, docs in results.items():
            rank = 1
            num_docs = len(docs)
            for doc_id in docs:
                score = num_docs - rank
                docno = docno_list[doc_id]
                f.write(f"{topic_id} Q0 {docno} {rank} {score} adeepanAND\n")
                rank += 1


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


def TokenizeStrings(strings, tokens):
    for string in strings:
        Tokenize(string, tokens)


def main(index_dir, queries_file, output_file):
    inv_index, lexicon, docno_list = load(index_dir)
    queries = read_queries(queries_file)
    results = {}
    for topic_id, query in queries:
        print(f"\nProcessing query '{query}' (Topic ID: {topic_id})")
        docs = boolean_and(query, lexicon, inv_index)
        results[topic_id] = docs
    write_results(output_file, results, docno_list)


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: BooleanAND <index_directory> <queries_file> <output_file>")
        sys.exit(1)

    index_dir = sys.argv[1]
    queries_file = sys.argv[2]
    output_file = sys.argv[3]

    main(index_dir, queries_file, output_file)
