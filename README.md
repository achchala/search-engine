# search-engine
Search engine built with Python backend to retrieve and display LA Times news articles.

### 1. Use the following command to run `IndexEngine`

   ```bash
   python IndexEngine.py <path_to_gz_file> <output_directory>
   ```

   - `<path_to_gz_file>`: The path to the `latimes.gz` file.
   - `<output_directory>`: The directory where the documents and metadata will be stored.

   Example:

   ```bash
   python IndexEngine.py /path/to/latimes.gz /path/to/output_dir
   ```
### 2. Ensure the storage directory is populated with your dataset and metadata files:

- Inverted Index: `storage/inverted-index.json`
- Lexicon: `storage/lexicon.json`
- Document Lengths: `storage/doc-lengths.txt`
- Document Numbers: `storage/docno_list.txt`
- Document Files: Files organized by date (e.g., `storage/1989/08/20/LA082089-0008.txt`).


### 3. To start the search engine:

   ```bash
     python interactive_bm25.py
   ```

Input: Enter a query string to search for relevant documents.

Output: Top 10 ranked documents with their headlines, dates, and query-biased snippets.

Actions:
- Enter a rank number to view the full document.
- Enter 'N' to start a new query.
- Enter 'Q' to quit.