import sys
from query_biased_summary import generate_query_biased_snippet
from IndexEngine import Tokenize


def main():
    if len(sys.argv) != 3:
        print("Usage: python test_query_biased_summary.py <doc_file_path> <query>")
        sys.exit(1)

    doc_file_path = sys.argv[1]
    query = sys.argv[2]

    try:
        with open(doc_file_path, "r") as f:
            doc_text = f.read()
    except FileNotFoundError:
        print(f"Error: File not found at {doc_file_path}")
        sys.exit(1)

    query_tokens = []
    Tokenize(query, query_tokens)  # Correct usage of Tokenize

    snippet = generate_query_biased_snippet(doc_text, query_tokens)

    print("\nGenerated Query-Biased Snippet:")
    print(snippet)


if __name__ == "__main__":
    main()
