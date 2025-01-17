import math
from collections import defaultdict
from IndexEngine import Tokenize


def calculate_average_doc_length(doc_lengths):
    return sum(doc_lengths) / len(doc_lengths)


def compute_bm25(
    query_tokens, doc_lengths, avg_doc_length, lexicon, inverted_index, total_docs
):
    K1 = 1.2
    B = 0.75
    scores = defaultdict(float)

    for term in query_tokens:
        if term not in lexicon:
            continue

        term_id = lexicon[term]
        postings = inverted_index.get(str(term_id), [])
        doc_freq = len(postings)

        for doc_id, freq in postings:
            doc_length = doc_lengths[int(doc_id)]
            K = K1 * ((1 - B) + B * (doc_length / avg_doc_length))

            idf = math.log((total_docs - doc_freq + 0.5) / (doc_freq + 0.5) + 1)
            term_score = idf * ((freq * (K1 + 1)) / (freq + K))

            scores[doc_id] += term_score

    return scores


def calculate_bm25(
    queries, inverted_index, lexicon, doc_lengths, docno_list, avg_doc_length
):
    results = defaultdict(list)
    total_docs = len(doc_lengths)

    for query_id, query_text in queries.items():
        query_tokens = []
        Tokenize(query_text, query_tokens)

        doc_scores = compute_bm25(
            query_tokens,
            doc_lengths,
            avg_doc_length,
            lexicon,
            inverted_index,
            total_docs,
        )

        ranked_docs = sorted(
            doc_scores.items(), key=lambda x: (-x[1], docno_list[int(x[0])])
        )
        results[query_id] = ranked_docs[:1000]

    return results


def load_queries(file_path):
    queries = {}
    with open(file_path, "r") as f:
        lines = f.readlines()
        for i in range(0, len(lines), 2):
            query_id = lines[i].strip()
            query_text = lines[i + 1].strip()
            queries[query_id] = query_text
    return queries
