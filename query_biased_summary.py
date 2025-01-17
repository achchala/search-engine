import re
from IndexEngine import Tokenize


def clean_text(text):
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def extract_text_tag(doc_text):
    match = re.search(r"<TEXT>(.*?)</TEXT>", doc_text, re.DOTALL)
    if match:
        return match.group(1)
    return ""


def sentence_score(sentence_tokens, query_tokens):
    run = 0
    max_run = 0
    unique_words = set()
    total_count = 0
    i = 0

    while i < len(sentence_tokens):
        if sentence_tokens[i] in query_tokens:
            total_count += 1
            unique_words.add(sentence_tokens[i])
            run += 1
            i += 1
            while i < len(sentence_tokens) and sentence_tokens[i] in query_tokens:
                run += 1
                total_count += 1
                unique_words.add(sentence_tokens[i])
                i += 1
            max_run = max(run, max_run)
            run = 0
        else:
            i += 1

    distinct_count = len(unique_words)
    score = 1 + total_count + distinct_count + max_run
    return score


def generate_query_biased_snippet(doc_text, query_tokens):
    text_content = extract_text_tag(doc_text)
    if not text_content:
        return "No relevant content found."

    clean_doc_text = clean_text(text_content)

    sentences = re.split(r"(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?|!)\s", clean_doc_text)

    scored_sentences = []
    for sentence in sentences:
        tokens = []
        Tokenize(sentence, tokens)
        score = sentence_score(tokens, query_tokens)
        scored_sentences.append((score, sentence.strip()))

    best_sentence = max(
        scored_sentences, key=lambda x: x[0], default=(0, "No relevant sentence")
    )[1]
    return best_sentence
